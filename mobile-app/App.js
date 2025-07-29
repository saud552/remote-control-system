/**
 * Remote Control System Mobile App
 * React Native application for remote device control and monitoring
 */

import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
} from 'react-native';
import {
  NavigationContainer,
  DefaultTheme,
  DarkTheme,
} from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Import screens
import DashboardScreen from './screens/DashboardScreen';
import DevicesScreen from './screens/DevicesScreen';
import MonitoringScreen from './screens/MonitoringScreen';
import AlertsScreen from './screens/AlertsScreen';
import AnalyticsScreen from './screens/AnalyticsScreen';
import SettingsScreen from './screens/SettingsScreen';
import LoginScreen from './screens/LoginScreen';

// Import services
import ApiService from './services/ApiService';
import NotificationService from './services/NotificationService';
import StorageService from './services/StorageService';

// Import components
import LoadingOverlay from './components/LoadingOverlay';
import NetworkStatus from './components/NetworkStatus';
import ErrorBoundary from './components/ErrorBoundary';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Custom theme
const CustomTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#3498db',
    secondary: '#2c3e50',
    success: '#27ae60',
    warning: '#f39c12',
    danger: '#e74c3c',
    background: '#f8f9fa',
    surface: '#ffffff',
    text: '#2c3e50',
    textSecondary: '#6c757d',
    border: '#dee2e6',
  },
};

const DarkCustomTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: '#3498db',
    secondary: '#34495e',
    success: '#27ae60',
    warning: '#f39c12',
    danger: '#e74c3c',
    background: '#2c3e50',
    surface: '#34495e',
    text: '#ecf0f1',
    textSecondary: '#bdc3c7',
    border: '#34495e',
  },
};

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setIsLoading(true);

      // Initialize services
      await StorageService.init();
      await NotificationService.init();

      // Check authentication
      const token = await StorageService.getToken();
      if (token) {
        const userData = await StorageService.getUser();
        if (userData) {
          setUser(userData);
          setIsAuthenticated(true);
        }
      }

      // Check theme preference
      const themePreference = await StorageService.getThemePreference();
      setIsDarkMode(themePreference === 'dark');

      // Initialize API service
      ApiService.setBaseURL('http://192.168.1.100:8000');
      if (token) {
        ApiService.setToken(token);
      }

      // Start network monitoring
      startNetworkMonitoring();

      // Start notification monitoring
      startNotificationMonitoring();

    } catch (error) {
      console.error('App initialization error:', error);
      Alert.alert('خطأ', 'حدث خطأ أثناء تهيئة التطبيق');
    } finally {
      setIsLoading(false);
    }
  };

  const startNetworkMonitoring = () => {
    // Monitor network connectivity
    const checkConnection = async () => {
      try {
        const response = await ApiService.get('/health');
        setIsOnline(true);
      } catch (error) {
        setIsOnline(false);
      }
    };

    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    checkConnection(); // Initial check

    return () => clearInterval(interval);
  };

  const startNotificationMonitoring = () => {
    // Monitor for new notifications
    const checkNotifications = async () => {
      try {
        const alerts = await ApiService.get('/api/alerts?limit=5');
        if (alerts && alerts.length > 0) {
          const newAlerts = alerts.filter(alert => 
            !notifications.find(n => n.alert_id === alert.alert_id)
          );
          
          if (newAlerts.length > 0) {
            setNotifications(prev => [...newAlerts, ...prev]);
            
            // Show notification for new alerts
            newAlerts.forEach(alert => {
              NotificationService.showNotification({
                title: `تنبيه ${alert.severity}`,
                body: alert.message,
                data: alert,
              });
            });
          }
        }
      } catch (error) {
        console.error('Notification check error:', error);
      }
    };

    // Check notifications every 60 seconds
    const interval = setInterval(checkNotifications, 60000);
    checkNotifications(); // Initial check

    return () => clearInterval(interval);
  };

  const handleLogin = async (credentials) => {
    try {
      setIsLoading(true);
      
      const response = await ApiService.post('/api/auth/login', credentials);
      
      if (response.success) {
        await StorageService.setToken(response.data.token);
        await StorageService.setUser(response.data.user);
        
        setUser(response.data.user);
        setIsAuthenticated(true);
        ApiService.setToken(response.data.token);
        
        return { success: true };
      } else {
        return { success: false, message: response.message };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, message: 'خطأ في تسجيل الدخول' };
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await StorageService.clearToken();
      await StorageService.clearUser();
      
      setUser(null);
      setIsAuthenticated(false);
      ApiService.clearToken();
      
      setNotifications([]);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleThemeToggle = async () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    await StorageService.setThemePreference(newTheme ? 'dark' : 'light');
  };

  const handleNotificationPress = (notification) => {
    // Handle notification press
    console.log('Notification pressed:', notification);
  };

  if (isLoading) {
    return <LoadingOverlay />;
  }

  if (!isAuthenticated) {
    return (
      <ErrorBoundary>
        <NavigationContainer theme={isDarkMode ? DarkCustomTheme : CustomTheme}>
          <Stack.Navigator screenOptions={{ headerShown: false }}>
            <Stack.Screen name="Login">
              {props => (
                <LoginScreen
                  {...props}
                  onLogin={handleLogin}
                  isLoading={isLoading}
                />
              )}
            </Stack.Screen>
          </Stack.Navigator>
        </NavigationContainer>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <NavigationContainer theme={isDarkMode ? DarkCustomTheme : CustomTheme}>
        <SafeAreaView style={styles.container}>
          <StatusBar
            barStyle={isDarkMode ? 'light-content' : 'dark-content'}
            backgroundColor={isDarkMode ? '#2c3e50' : '#ffffff'}
          />
          
          <NetworkStatus isOnline={isOnline} />
          
          <Tab.Navigator
            screenOptions={({ route }) => ({
              tabBarIcon: ({ focused, color, size }) => {
                let iconName;

                switch (route.name) {
                  case 'Dashboard':
                    iconName = 'dashboard';
                    break;
                  case 'Devices':
                    iconName = 'devices';
                    break;
                  case 'Monitoring':
                    iconName = 'monitor';
                    break;
                  case 'Alerts':
                    iconName = 'notifications';
                    break;
                  case 'Analytics':
                    iconName = 'analytics';
                    break;
                  case 'Settings':
                    iconName = 'settings';
                    break;
                  default:
                    iconName = 'home';
                }

                return (
                  <Icon
                    name={iconName}
                    size={size}
                    color={color}
                  />
                );
              },
              tabBarActiveTintColor: isDarkMode ? '#3498db' : '#3498db',
              tabBarInactiveTintColor: isDarkMode ? '#bdc3c7' : '#6c757d',
              tabBarStyle: {
                backgroundColor: isDarkMode ? '#34495e' : '#ffffff',
                borderTopColor: isDarkMode ? '#34495e' : '#dee2e6',
              },
              headerStyle: {
                backgroundColor: isDarkMode ? '#2c3e50' : '#ffffff',
              },
              headerTintColor: isDarkMode ? '#ecf0f1' : '#2c3e50',
            })}
          >
            <Tab.Screen
              name="Dashboard"
              component={DashboardScreen}
              options={{
                title: 'لوحة التحكم',
                headerShown: false,
              }}
            />
            
            <Tab.Screen
              name="Devices"
              component={DevicesScreen}
              options={{
                title: 'الأجهزة',
                headerShown: false,
              }}
            />
            
            <Tab.Screen
              name="Monitoring"
              component={MonitoringScreen}
              options={{
                title: 'المراقبة',
                headerShown: false,
              }}
            />
            
            <Tab.Screen
              name="Alerts"
              component={AlertsScreen}
              options={{
                title: 'التنبيهات',
                headerShown: false,
                tabBarBadge: notifications.length > 0 ? notifications.length : undefined,
              }}
            />
            
            <Tab.Screen
              name="Analytics"
              component={AnalyticsScreen}
              options={{
                title: 'التحليلات',
                headerShown: false,
              }}
            />
            
            <Tab.Screen
              name="Settings"
              component={SettingsScreen}
              options={{
                title: 'الإعدادات',
                headerShown: false,
              }}
            />
          </Tab.Navigator>
        </SafeAreaView>
      </NavigationContainer>
    </ErrorBoundary>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default App;