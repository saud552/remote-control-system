/**
 * Dashboard Screen
 * Main dashboard with real-time monitoring and quick actions
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Dimensions,
  Platform,
} from 'react-native';
import { useTheme } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';

// Import components
import MetricCard from '../components/MetricCard';
import DeviceCard from '../components/DeviceCard';
import AlertCard from '../components/AlertCard';
import PerformanceChart from '../components/PerformanceChart';
import NetworkChart from '../components/NetworkChart';

// Import services
import ApiService from '../services/ApiService';

const { width } = Dimensions.get('window');

const DashboardScreen = ({ navigation }) => {
  const theme = useTheme();
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [dashboardData, setDashboardData] = useState({
    devices: [],
    alerts: [],
    performance: {
      cpu: 0,
      memory: 0,
      battery: 0,
      temperature: 0,
    },
    network: {
      bandwidth: 0,
      latency: 0,
      packetLoss: 0,
    },
    security: {
      threatLevel: 0,
      events: 0,
      blockedIPs: 0,
    },
    statistics: {
      connectedDevices: 0,
      activeAlerts: 0,
      monitoringSessions: 0,
      totalEvents: 0,
    },
  });

  useEffect(() => {
    loadDashboardData();
    startRealTimeUpdates();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);

      // Load all dashboard data in parallel
      const [
        devicesResponse,
        alertsResponse,
        monitoringStatusResponse,
        performanceDataResponse,
        networkDataResponse,
        securityDataResponse,
      ] = await Promise.all([
        ApiService.get('/api/devices'),
        ApiService.get('/api/alerts?limit=5'),
        ApiService.get('/api/monitoring/status'),
        ApiService.get('/api/monitoring/statistics'),
        ApiService.get('/api/data/recent?category=network&limit=1'),
        ApiService.get('/api/data/recent?category=security&limit=1'),
      ]);

      // Process devices data
      const devices = devicesResponse || [];
      const connectedDevices = devices.filter(device => device.is_connected);

      // Process alerts data
      const alerts = alertsResponse || [];
      const activeAlerts = alerts.filter(alert => !alert.resolved);

      // Process monitoring status
      const monitoringStatus = monitoringStatusResponse?.data || {};
      const monitoringSessions = monitoringStatus.active_sessions || 0;

      // Process performance data
      const performanceData = performanceDataResponse?.data?.performance || {};
      const latestPerformance = performanceDataResponse?.data?.performance?.slice(-1)[0] || {};

      // Process network data
      const networkData = networkDataResponse?.network || [];
      const latestNetwork = networkData.slice(-1)[0] || {};

      // Process security data
      const securityData = securityDataResponse?.security || [];
      const latestSecurity = securityData.slice(-1)[0] || {};

      setDashboardData({
        devices: devices,
        alerts: alerts,
        performance: {
          cpu: latestPerformance.cpu_usage || 0,
          memory: latestPerformance.memory_usage || 0,
          battery: latestPerformance.battery_level || 0,
          temperature: latestPerformance.temperature || 0,
        },
        network: {
          bandwidth: latestNetwork.bandwidth_usage || 0,
          latency: latestNetwork.latency || 0,
          packetLoss: latestNetwork.packet_loss || 0,
        },
        security: {
          threatLevel: latestSecurity.threat_level || 0,
          events: latestSecurity.total_events || 0,
          blockedIPs: latestSecurity.blocked_ips || 0,
        },
        statistics: {
          connectedDevices: connectedDevices.length,
          activeAlerts: activeAlerts.length,
          monitoringSessions: monitoringSessions,
          totalEvents: latestSecurity.total_events || 0,
        },
      });

    } catch (error) {
      console.error('Dashboard data loading error:', error);
      Alert.alert('خطأ', 'فشل في تحميل بيانات لوحة التحكم');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const startRealTimeUpdates = () => {
    // Update dashboard data every 30 seconds
    const interval = setInterval(() => {
      if (!isLoading) {
        loadDashboardData();
      }
    }, 30000);

    return () => clearInterval(interval);
  };

  const onRefresh = useCallback(() => {
    setIsRefreshing(true);
    loadDashboardData();
  }, []);

  const handleDevicePress = (device) => {
    navigation.navigate('Devices', { selectedDevice: device });
  };

  const handleAlertPress = (alert) => {
    navigation.navigate('Alerts', { selectedAlert: alert });
  };

  const handleStartMonitoring = () => {
    navigation.navigate('Monitoring', { action: 'start' });
  };

  const handleScanDevices = async () => {
    try {
      Alert.alert('فحص الأجهزة', 'جاري فحص الأجهزة في الشبكة...');
      
      const response = await ApiService.post('/api/discovery/scan');
      
      if (response.success) {
        Alert.alert('نجح', 'تم بدء فحص الأجهزة');
        loadDashboardData(); // Reload data after scan
      } else {
        Alert.alert('خطأ', 'فشل في فحص الأجهزة');
      }
    } catch (error) {
      console.error('Device scan error:', error);
      Alert.alert('خطأ', 'فشل في فحص الأجهزة');
    }
  };

  const handleGenerateReport = () => {
    navigation.navigate('Analytics', { action: 'generate_report' });
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getThreatLevelColor = (level) => {
    if (level >= 7) return theme.colors.danger;
    if (level >= 4) return theme.colors.warning;
    return theme.colors.success;
  };

  const getThreatLevelText = (level) => {
    if (level >= 7) return 'حرج';
    if (level >= 4) return 'متوسط';
    return 'منخفض';
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
      }
      showsVerticalScrollIndicator={false}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.headerTitle, { color: theme.colors.text }]}>
          لوحة التحكم
        </Text>
        <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>
          مراقبة شاملة للأجهزة والأنظمة
        </Text>
      </View>

      {/* Quick Stats */}
      <View style={styles.statsContainer}>
        <MetricCard
          title="الأجهزة المتصلة"
          value={dashboardData.statistics.connectedDevices}
          icon="devices"
          color={theme.colors.primary}
        />
        <MetricCard
          title="التنبيهات النشطة"
          value={dashboardData.statistics.activeAlerts}
          icon="notifications"
          color={theme.colors.warning}
        />
        <MetricCard
          title="جلسات المراقبة"
          value={dashboardData.statistics.monitoringSessions}
          icon="monitor"
          color={theme.colors.success}
        />
        <MetricCard
          title="مستوى التهديد"
          value={`${dashboardData.security.threatLevel}/10`}
          icon="security"
          color={getThreatLevelColor(dashboardData.security.threatLevel)}
        />
      </View>

      {/* Performance Monitoring */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
          مراقبة الأداء
        </Text>
        <View style={styles.performanceGrid}>
          <View style={styles.performanceItem}>
            <Icon name="memory" size={24} color={theme.colors.primary} />
            <Text style={[styles.performanceLabel, { color: theme.colors.textSecondary }]}>
              المعالج
            </Text>
            <Text style={[styles.performanceValue, { color: theme.colors.text }]}>
              {dashboardData.performance.cpu.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.performanceItem}>
            <Icon name="storage" size={24} color={theme.colors.warning} />
            <Text style={[styles.performanceLabel, { color: theme.colors.textSecondary }]}>
              الذاكرة
            </Text>
            <Text style={[styles.performanceValue, { color: theme.colors.text }]}>
              {dashboardData.performance.memory.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.performanceItem}>
            <Icon name="battery-full" size={24} color={theme.colors.success} />
            <Text style={[styles.performanceLabel, { color: theme.colors.textSecondary }]}>
              البطارية
            </Text>
            <Text style={[styles.performanceValue, { color: theme.colors.text }]}>
              {dashboardData.performance.battery.toFixed(1)}%
            </Text>
          </View>
          <View style={styles.performanceItem}>
            <Icon name="thermostat" size={24} color={theme.colors.danger} />
            <Text style={[styles.performanceLabel, { color: theme.colors.textSecondary }]}>
              الحرارة
            </Text>
            <Text style={[styles.performanceValue, { color: theme.colors.text }]}>
              {dashboardData.performance.temperature.toFixed(1)}°C
            </Text>
          </View>
        </View>
      </View>

      {/* Network Monitoring */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
          مراقبة الشبكة
        </Text>
        <View style={styles.networkGrid}>
          <View style={styles.networkItem}>
            <Icon name="network-check" size={24} color={theme.colors.primary} />
            <Text style={[styles.networkLabel, { color: theme.colors.textSecondary }]}>
              النطاق الترددي
            </Text>
            <Text style={[styles.networkValue, { color: theme.colors.text }]}>
              {formatBytes(dashboardData.network.bandwidth)}
            </Text>
          </View>
          <View style={styles.networkItem}>
            <Icon name="speed" size={24} color={theme.colors.warning} />
            <Text style={[styles.networkLabel, { color: theme.colors.textSecondary }]}>
              زمن الاستجابة
            </Text>
            <Text style={[styles.networkValue, { color: theme.colors.text }]}>
              {dashboardData.network.latency.toFixed(1)}ms
            </Text>
          </View>
          <View style={styles.networkItem}>
            <Icon name="error" size={24} color={theme.colors.danger} />
            <Text style={[styles.networkLabel, { color: theme.colors.textSecondary }]}>
              فقدان الحزم
            </Text>
            <Text style={[styles.networkValue, { color: theme.colors.text }]}>
              {dashboardData.network.packetLoss.toFixed(2)}%
            </Text>
          </View>
        </View>
      </View>

      {/* Security Status */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
          حالة الأمان
        </Text>
        <View style={[styles.securityCard, { backgroundColor: theme.colors.surface }]}>
          <View style={styles.securityHeader}>
            <Icon name="security" size={32} color={getThreatLevelColor(dashboardData.security.threatLevel)} />
            <View style={styles.securityInfo}>
              <Text style={[styles.threatLevel, { color: getThreatLevelColor(dashboardData.security.threatLevel) }]}>
                {getThreatLevelText(dashboardData.security.threatLevel)}
              </Text>
              <Text style={[styles.threatValue, { color: theme.colors.text }]}>
                مستوى التهديد: {dashboardData.security.threatLevel}/10
              </Text>
            </View>
          </View>
          <View style={styles.securityStats}>
            <View style={styles.securityStat}>
              <Text style={[styles.securityStatValue, { color: theme.colors.text }]}>
                {dashboardData.security.events}
              </Text>
              <Text style={[styles.securityStatLabel, { color: theme.colors.textSecondary }]}>
                الأحداث
              </Text>
            </View>
            <View style={styles.securityStat}>
              <Text style={[styles.securityStatValue, { color: theme.colors.text }]}>
                {dashboardData.security.blockedIPs}
              </Text>
              <Text style={[styles.securityStatLabel, { color: theme.colors.textSecondary }]}>
                IP محظور
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* Recent Alerts */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            التنبيهات الأخيرة
          </Text>
          <TouchableOpacity onPress={() => navigation.navigate('Alerts')}>
            <Text style={[styles.viewAll, { color: theme.colors.primary }]}>
              عرض الكل
            </Text>
          </TouchableOpacity>
        </View>
        {dashboardData.alerts.length > 0 ? (
          dashboardData.alerts.slice(0, 3).map((alert, index) => (
            <AlertCard
              key={alert.alert_id}
              alert={alert}
              onPress={() => handleAlertPress(alert)}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Icon name="notifications-none" size={48} color={theme.colors.textSecondary} />
            <Text style={[styles.emptyStateText, { color: theme.colors.textSecondary }]}>
              لا توجد تنبيهات حديثة
            </Text>
          </View>
        )}
      </View>

      {/* Connected Devices */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            الأجهزة المتصلة
          </Text>
          <TouchableOpacity onPress={() => navigation.navigate('Devices')}>
            <Text style={[styles.viewAll, { color: theme.colors.primary }]}>
              عرض الكل
            </Text>
          </TouchableOpacity>
        </View>
        {dashboardData.devices.filter(device => device.is_connected).length > 0 ? (
          dashboardData.devices
            .filter(device => device.is_connected)
            .slice(0, 3)
            .map((device, index) => (
              <DeviceCard
                key={device.device_id}
                device={device}
                onPress={() => handleDevicePress(device)}
              />
            ))
        ) : (
          <View style={styles.emptyState}>
            <Icon name="devices-none" size={48} color={theme.colors.textSecondary} />
            <Text style={[styles.emptyStateText, { color: theme.colors.textSecondary }]}>
              لا توجد أجهزة متصلة
            </Text>
          </View>
        )}
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
          إجراءات سريعة
        </Text>
        <View style={styles.actionsGrid}>
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: theme.colors.primary }]}
            onPress={handleStartMonitoring}
          >
            <Icon name="play-arrow" size={24} color="white" />
            <Text style={styles.actionButtonText}>بدء المراقبة</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: theme.colors.success }]}
            onPress={handleScanDevices}
          >
            <Icon name="search" size={24} color="white" />
            <Text style={styles.actionButtonText}>فحص الأجهزة</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: theme.colors.warning }]}
            onPress={handleGenerateReport}
          >
            <Icon name="assessment" size={24} color="white" />
            <Text style={styles.actionButtonText}>إنشاء تقرير</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: theme.colors.secondary }]}
            onPress={() => navigation.navigate('Settings')}
          >
            <Icon name="settings" size={24} color="white" />
            <Text style={styles.actionButtonText}>الإعدادات</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Bottom Spacing */}
      <View style={styles.bottomSpacing} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 20,
    paddingTop: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 15,
    marginBottom: 20,
  },
  section: {
    marginBottom: 25,
    paddingHorizontal: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  viewAll: {
    fontSize: 14,
    fontWeight: '500',
  },
  performanceGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  performanceItem: {
    width: '48%',
    backgroundColor: 'rgba(52, 152, 219, 0.1)',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    alignItems: 'center',
  },
  performanceLabel: {
    fontSize: 12,
    marginTop: 5,
    marginBottom: 3,
  },
  performanceValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  networkGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  networkItem: {
    flex: 1,
    backgroundColor: 'rgba(243, 156, 18, 0.1)',
    borderRadius: 12,
    padding: 15,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  networkLabel: {
    fontSize: 12,
    marginTop: 5,
    marginBottom: 3,
  },
  networkValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  securityCard: {
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  securityHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  securityInfo: {
    marginLeft: 15,
    flex: 1,
  },
  threatLevel: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  threatValue: {
    fontSize: 14,
  },
  securityStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  securityStat: {
    alignItems: 'center',
  },
  securityStatValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  securityStatLabel: {
    fontSize: 12,
    marginTop: 2,
  },
  emptyState: {
    alignItems: 'center',
    padding: 30,
  },
  emptyStateText: {
    fontSize: 14,
    marginTop: 10,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: '48%',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8,
  },
  bottomSpacing: {
    height: 20,
  },
});

export default DashboardScreen;