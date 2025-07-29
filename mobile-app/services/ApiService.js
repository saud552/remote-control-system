/**
 * API Service
 * Handles all API communication for the mobile app
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

class ApiService {
  constructor() {
    this.baseURL = 'http://192.168.1.100:8000';
    this.token = null;
    this.isOnline = true;
    this.requestQueue = [];
    this.retryAttempts = 3;
    this.retryDelay = 1000;
  }

  /**
   * Set base URL for API
   */
  setBaseURL(url) {
    this.baseURL = url;
  }

  /**
   * Set authentication token
   */
  setToken(token) {
    this.token = token;
  }

  /**
   * Clear authentication token
   */
  clearToken() {
    this.token = null;
  }

  /**
   * Check network connectivity
   */
  async checkConnectivity() {
    const netInfo = await NetInfo.fetch();
    this.isOnline = netInfo.isConnected && netInfo.isInternetReachable;
    return this.isOnline;
  }

  /**
   * Get request headers
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': 'RemoteControlApp/1.0.0',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  /**
   * Make HTTP request with retry logic
   */
  async makeRequest(method, endpoint, data = null, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = this.getHeaders();
    const config = {
      method,
      headers,
      ...options,
    };

    if (data && method !== 'GET') {
      config.body = JSON.stringify(data);
    }

    // Check connectivity first
    const isOnline = await this.checkConnectivity();
    if (!isOnline) {
      throw new Error('No internet connection');
    }

    let lastError;
    
    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        const response = await fetch(url, config);
        
        // Handle different response types
        const contentType = response.headers.get('content-type');
        let responseData;
        
        if (contentType && contentType.includes('application/json')) {
          responseData = await response.json();
        } else {
          responseData = await response.text();
        }

        // Handle successful response
        if (response.ok) {
          return responseData;
        }

        // Handle specific error codes
        switch (response.status) {
          case 401:
            // Unauthorized - clear token and throw error
            this.clearToken();
            await AsyncStorage.removeItem('token');
            throw new Error('Authentication failed');
          
          case 403:
            throw new Error('Access denied');
          
          case 404:
            throw new Error('Resource not found');
          
          case 500:
            throw new Error('Server error');
          
          default:
            throw new Error(`HTTP ${response.status}: ${responseData.message || 'Unknown error'}`);
        }

      } catch (error) {
        lastError = error;
        
        // Don't retry on certain errors
        if (error.message === 'Authentication failed' || 
            error.message === 'Access denied' ||
            error.message === 'Resource not found') {
          break;
        }

        // Wait before retry (except for last attempt)
        if (attempt < this.retryAttempts) {
          await new Promise(resolve => setTimeout(resolve, this.retryDelay * attempt));
        }
      }
    }

    throw lastError;
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.makeRequest('GET', endpoint, null, options);
  }

  /**
   * POST request
   */
  async post(endpoint, data = null, options = {}) {
    return this.makeRequest('POST', endpoint, data, options);
  }

  /**
   * PUT request
   */
  async put(endpoint, data = null, options = {}) {
    return this.makeRequest('PUT', endpoint, data, options);
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.makeRequest('DELETE', endpoint, null, options);
  }

  /**
   * PATCH request
   */
  async patch(endpoint, data = null, options = {}) {
    return this.makeRequest('PATCH', endpoint, data, options);
  }

  /**
   * Upload file
   */
  async uploadFile(endpoint, fileUri, fileType = 'application/octet-stream', options = {}) {
    const formData = new FormData();
    formData.append('file', {
      uri: fileUri,
      type: fileType,
      name: 'file',
    });

    const headers = {
      ...this.getHeaders(),
      'Content-Type': 'multipart/form-data',
    };

    return this.makeRequest('POST', endpoint, formData, {
      ...options,
      headers,
    });
  }

  /**
   * Download file
   */
  async downloadFile(endpoint, options = {}) {
    const response = await this.makeRequest('GET', endpoint, null, {
      ...options,
      responseType: 'blob',
    });
    
    return response;
  }

  /**
   * Stream data (for real-time updates)
   */
  async streamData(endpoint, onData, onError) {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const headers = this.getHeaders();
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          ...headers,
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onData(data);
            } catch (error) {
              console.error('Error parsing stream data:', error);
            }
          }
        }
      }
    } catch (error) {
      onError(error);
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await this.get('/health');
      return response.success;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get API statistics
   */
  async getApiStats() {
    return this.get('/api/stats');
  }

  /**
   * Get system information
   */
  async getSystemInfo() {
    return this.get('/api/system/info');
  }

  /**
   * Get system logs
   */
  async getSystemLogs(limit = 100) {
    return this.get(`/api/system/logs?limit=${limit}`);
  }

  // Device Management
  async getDevices() {
    return this.get('/api/devices');
  }

  async getDevice(deviceId) {
    return this.get(`/api/devices/${deviceId}`);
  }

  async connectDevice(deviceId) {
    return this.post(`/api/devices/${deviceId}/connect`);
  }

  async disconnectDevice(deviceId) {
    return this.post(`/api/devices/${deviceId}/disconnect`);
  }

  // Device Discovery
  async scanNetwork() {
    return this.post('/api/discovery/scan');
  }

  async getDiscoveryResults() {
    return this.get('/api/discovery/results');
  }

  // Monitoring
  async startMonitoring(deviceId, monitoringTypes = ['performance', 'network', 'security'], interval = 5) {
    return this.post('/api/monitoring/start', {
      device_id: deviceId,
      monitoring_types: monitoringTypes,
      interval: interval,
    });
  }

  async stopMonitoring(sessionId) {
    return this.post('/api/monitoring/stop', { session_id: sessionId });
  }

  async getMonitoringStatus() {
    return this.get('/api/monitoring/status');
  }

  async getMonitoringStatistics() {
    return this.get('/api/monitoring/statistics');
  }

  async getRecentData(category, limit = 100) {
    return this.get(`/api/data/recent?category=${category}&limit=${limit}`);
  }

  // Alerts
  async getAlerts(limit = 50, severity = null) {
    let endpoint = `/api/alerts?limit=${limit}`;
    if (severity) {
      endpoint += `&severity=${severity}`;
    }
    return this.get(endpoint);
  }

  async acknowledgeAlert(alertId) {
    return this.post(`/api/alerts/${alertId}/acknowledge`);
  }

  async resolveAlert(alertId) {
    return this.post(`/api/alerts/${alertId}/resolve`);
  }

  // Analytics
  async getRecentAnalyses(limit = 10) {
    return this.get(`/api/analytics/recent?limit=${limit}`);
  }

  async analyzePerformanceData(deviceId, hours = 24) {
    return this.get(`/api/analytics/performance?device_id=${deviceId}&hours=${hours}`);
  }

  // Configuration
  async configureAlerts(rules) {
    return this.post('/api/config/alerts', rules);
  }

  async configureNotifications(channels) {
    return this.post('/api/config/notifications', channels);
  }

  // Security
  async blockIP(ipAddress, reason = 'Security threat') {
    return this.post('/api/security/block-ip', {
      ip_address: ipAddress,
      reason: reason,
    });
  }

  async unblockIP(ipAddress) {
    return this.post('/api/security/unblock-ip', {
      ip_address: ipAddress,
    });
  }

  async getSecurityEvents(limit = 100, severity = null) {
    let endpoint = `/api/security/events?limit=${limit}`;
    if (severity) {
      endpoint += `&severity=${severity}`;
    }
    return this.get(endpoint);
  }

  // Export
  async exportMonitoringData(sessionId = null, formatType = 'json') {
    return this.post('/api/export/monitoring', {
      session_id: sessionId,
      format_type: formatType,
    });
  }

  /**
   * Error handler
   */
  handleError(error) {
    console.error('API Error:', error);
    
    // Map error messages to user-friendly Arabic messages
    const errorMessages = {
      'No internet connection': 'لا يوجد اتصال بالإنترنت',
      'Authentication failed': 'فشل في المصادقة',
      'Access denied': 'تم رفض الوصول',
      'Resource not found': 'المورد غير موجود',
      'Server error': 'خطأ في الخادم',
      'Network request failed': 'فشل في طلب الشبكة',
      'Timeout': 'انتهت مهلة الاتصال',
    };

    const userMessage = errorMessages[error.message] || error.message;
    
    return {
      error: true,
      message: userMessage,
      originalError: error,
    };
  }

  /**
   * Request interceptor for logging
   */
  logRequest(method, endpoint, data = null) {
    console.log(`API Request: ${method} ${endpoint}`, data);
  }

  /**
   * Response interceptor for logging
   */
  logResponse(response) {
    console.log('API Response:', response);
  }

  /**
   * Clear request queue
   */
  clearQueue() {
    this.requestQueue = [];
  }

  /**
   * Get queue status
   */
  getQueueStatus() {
    return {
      length: this.requestQueue.length,
      isOnline: this.isOnline,
    };
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;