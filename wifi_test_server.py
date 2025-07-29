#!/usr/bin/env python3
"""
WiFi Test Server - يستمع على جميع الواجهات
"""

from flask import Flask, request
import socket
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    client_ip = request.remote_addr
    server_ip = request.host.split(':')[0]
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WiFi Test Server</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{ 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px; 
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }}
            .status {{ color: #4CAF50; font-weight: bold; font-size: 1.2em; }}
            .info {{ 
                background: rgba(255,255,255,0.2); 
                padding: 15px; 
                border-radius: 10px; 
                margin: 15px 0;
                border: 1px solid rgba(255,255,255,0.3);
            }}
            .link {{ 
                color: #FFD700; 
                text-decoration: none; 
                font-weight: bold;
            }}
            .link:hover {{ color: #FFA500; }}
            h1 {{ text-align: center; margin-bottom: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 WiFi Test Server Working!</h1>
            <div class="info">
                <p><strong>✅ Server Status:</strong> <span class="status">RUNNING</span></p>
                <p><strong>🖥️ Server Host:</strong> {socket.gethostname()}</p>
                <p><strong>🌍 Server IP:</strong> {server_ip}</p>
                <p><strong>📱 Client IP:</strong> {client_ip}</p>
                <p><strong>🔌 Port:</strong> 8082</p>
                <p><strong>⏰ Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <h2>🔗 Available Services:</h2>
            <ul>
                <li><a href="http://{server_ip}:8081" class="link">📊 Dashboard (Port 8081)</a></li>
                <li><a href="http://{server_ip}:3000" class="link">🎣 Phishing Site (Port 3000)</a></li>
                <li><a href="http://{server_ip}:8080" class="link">⚙️ Command Server (Port 8080)</a></li>
                <li><a href="http://{server_ip}:5000" class="link">🧪 Test Server (Port 5000)</a></li>
            </ul>
            <div class="info">
                <p><strong>📡 Network Info:</strong></p>
                <p>• Internal IP: 172.30.0.2</p>
                <p>• External IP: 3.12.82.200</p>
                <p>• If you can see this, WiFi access is working!</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/status')
def status():
    return {
        'status': 'running',
        'server_ip': request.host.split(':')[0],
        'client_ip': request.remote_addr,
        'time': datetime.now().isoformat()
    }

if __name__ == '__main__':
    print("🌐 Starting WiFi test server on port 8082...")
    print("🔗 Local: http://localhost:8082")
    print("🔗 Internal: http://172.30.0.2:8082")
    print("🔗 External: http://3.12.82.200:8082")
    print("📱 Access from other devices on same WiFi network!")
    app.run(host='0.0.0.0', port=8082, debug=False)