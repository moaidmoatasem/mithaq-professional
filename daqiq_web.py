#!/usr/bin/env python3
"""
mithaq Web Dashboard
Simple Flask UI for running scans
"""

from flask import Flask, render_template, request, jsonify
from mithaq.scanners.header_scanner import SimpleScanner
from pathlib import Path
import json
from datetime import datetime

app = Flask(__name__)

# Store scan results
scan_history = []

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', history=scan_history)

@app.route('/api/scan', methods=['POST'])
def run_scan():
    """Run security scan"""
    data = request.json
    target_url = data.get('url')
    
    if not target_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Run scan
    scanner = SimpleScanner(target_url)
    scanner.scan_security_headers()
    scanner.scan_http_methods()
    scanner.scan_ssl_tls()
    
    # Store result
    result = {
        'id': len(scan_history) + 1,
        'timestamp': datetime.now().isoformat(),
        'target': target_url,
        'vulnerabilities': scanner.results['vulnerabilities'],
        'count': len(scanner.results['vulnerabilities'])
    }
    
    scan_history.append(result)
    
    return jsonify(result)

@app.route('/api/history')
def get_history():
    """Get scan history"""
    return jsonify(scan_history)

if __name__ == '__main__':
    # Create templates directory
    Path('templates').mkdir(exist_ok=True)
    
    # Create simple HTML template
    html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>mithaq Security Scanner</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1200px; 
            margin: 50px auto; 
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        h1 { color: #00ff88; }
        .scan-form { 
            background: #2a2a2a; 
            padding: 20px; 
            border-radius: 8px;
            margin-bottom: 30px;
        }
        input[type="text"] { 
            width: 60%; 
            padding: 10px; 
            font-size: 16px;
            background: #3a3a3a;
            border: 1px solid #555;
            color: #fff;
            border-radius: 4px;
        }
        button { 
            padding: 10px 20px; 
            font-size: 16px; 
            background: #00ff88;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            color: #000;
            font-weight: bold;
        }
        button:hover { background: #00cc66; }
        .results { 
            background: #2a2a2a; 
            padding: 20px;
            border-radius: 8px;
        }
        .vuln { 
            background: #3a3a3a; 
            padding: 10px; 
            margin: 10px 0;
            border-left: 4px solid #ff4444;
            border-radius: 4px;
        }
        .vuln.high { border-left-color: #ff4444; }
        .vuln.medium { border-left-color: #ffaa00; }
        .vuln.low { border-left-color: #ffff00; }
        .loading { display: none; color: #00ff88; }
    </style>
</head>
<body>
    <h1>🔍 mithaq Security Scanner</h1>
    
    <div class="scan-form">
        <h2>Run Scan</h2>
        <input type="text" id="url" placeholder="https://example.com" />
        <button onclick="runScan()">Scan Now</button>
        <p class="loading" id="loading">⏳ Scanning...</p>
    </div>
    
    <div class="results">
        <h2>Results</h2>
        <div id="results">No scans yet. Enter a URL above to start.</div>
    </div>
    
    <script>
        async function runScan() {
            const url = document.getElementById('url').value;
            if (!url) {
                alert('Please enter a URL');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '⏳ Scanning...';
            
            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                document.getElementById('results').innerHTML = 
                    '<p style="color: #ff4444;">Error: ' + error + '</p>';
            }
            
            document.getElementById('loading').style.display = 'none';
        }
        
        function displayResults(data) {
            let html = '<h3>Scan Results for ' + data.target + '</h3>';
            html += '<p>Vulnerabilities found: ' + data.count + '</p>';
            
            if (data.vulnerabilities.length > 0) {
                data.vulnerabilities.forEach(v => {
                    html += '<div class="vuln ' + v.severity.toLowerCase() + '">';
                    html += '<strong>' + v.type + '</strong> [' + v.severity + ']<br>';
                    html += v.description;
                    html += '</div>';
                });
            } else {
                html += '<p style="color: #00ff88;">✅ No vulnerabilities detected!</p>';
            }
            
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>
    '''
    
    with open('templates/index.html', 'w') as f:
        f.write(html_template)
    
    print("\n" + "="*70)
    print("🚀 mithaq Web Dashboard Starting...")
    print("="*70)
    print("\n📱 Open in browser: http://localhost:5000")
    print("\n✅ Ready to scan!\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

