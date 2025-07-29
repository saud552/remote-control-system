/**
 * Metric Card Component
 * Displays a metric with icon and value
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { useTheme } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';

const MetricCard = ({ 
  title, 
  value, 
  icon, 
  color, 
  onPress, 
  subtitle,
  trend,
  trendValue,
  size = 'medium' 
}) => {
  const theme = useTheme();

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return {
          container: styles.smallContainer,
          title: styles.smallTitle,
          value: styles.smallValue,
          icon: 20,
        };
      case 'large':
        return {
          container: styles.largeContainer,
          title: styles.largeTitle,
          value: styles.largeValue,
          icon: 32,
        };
      default:
        return {
          container: styles.mediumContainer,
          title: styles.mediumTitle,
          value: styles.mediumValue,
          icon: 24,
        };
    }
  };

  const sizeStyles = getSizeStyles();

  const getTrendColor = () => {
    if (!trend) return theme.colors.textSecondary;
    return trend === 'up' ? theme.colors.success : theme.colors.danger;
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    return trend === 'up' ? 'trending-up' : 'trending-down';
  };

  const Container = onPress ? TouchableOpacity : View;

  return (
    <Container
      style={[
        styles.container,
        sizeStyles.container,
        { backgroundColor: theme.colors.surface },
        onPress && styles.pressable,
      ]}
      onPress={onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      <View style={styles.header}>
        <View style={[styles.iconContainer, { backgroundColor: color + '20' }]}>
          <Icon name={icon} size={sizeStyles.icon} color={color} />
        </View>
        {trend && (
          <View style={styles.trendContainer}>
            <Icon 
              name={getTrendIcon()} 
              size={16} 
              color={getTrendColor()} 
            />
            <Text style={[styles.trendValue, { color: getTrendColor() }]}>
              {trendValue}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.content}>
        <Text style={[styles.title, sizeStyles.title, { color: theme.colors.text }]}>
          {title}
        </Text>
        <Text style={[styles.value, sizeStyles.value, { color: theme.colors.text }]}>
          {value}
        </Text>
        {subtitle && (
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            {subtitle}
          </Text>
        )}
      </View>
    </Container>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    padding: 16,
    margin: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  pressable: {
    // Additional styles for pressable cards
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  trendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trendValue: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  content: {
    flex: 1,
  },
  title: {
    fontSize: 12,
    fontWeight: '500',
    marginBottom: 4,
  },
  value: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  subtitle: {
    fontSize: 10,
    fontWeight: '400',
  },
  // Small size
  smallContainer: {
    padding: 12,
    minWidth: 120,
  },
  smallTitle: {
    fontSize: 10,
  },
  smallValue: {
    fontSize: 14,
  },
  // Medium size
  mediumContainer: {
    padding: 16,
    minWidth: 140,
  },
  mediumTitle: {
    fontSize: 12,
  },
  mediumValue: {
    fontSize: 18,
  },
  // Large size
  largeContainer: {
    padding: 20,
    minWidth: 160,
  },
  largeTitle: {
    fontSize: 14,
  },
  largeValue: {
    fontSize: 24,
  },
});

export default MetricCard;