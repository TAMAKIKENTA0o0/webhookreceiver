import os
import json
import re
import logging
import io
import zipfile
import pyperclip
import webbrowser
from urllib.parse import urlparse
from datetime import datetime
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, send_file

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "webhook-receiver-secret")

# Store received webhooks for history
webhook_history = []
MAX_HISTORY = 50  # Maximum number of webhooks to store in memory

def is_valid_url(url):
    """Check if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception as e:
        logger.error(f"Error validating URL: {e}")
        return False

def extract_urls(text):
    """Extract URLs from text content."""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.findall(url_pattern, text)

def copy_to_clipboard(content):
    """Copy content to clipboard."""
    try:
        if isinstance(content, (dict, list)):
            content = json.dumps(content, indent=2)
        else:
            content = str(content)
        
        pyperclip.copy(content)
        logger.info("Content copied to clipboard")
        return True
    except Exception as e:
        logger.error(f"Failed to copy to clipboard: {e}")
        return False

def open_url(url):
    """Open URL in the default browser."""
    try:
        if is_valid_url(url):
            webbrowser.open(url)
            logger.info(f"Opened URL: {url}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to open URL {url}: {e}")
        return False

def process_webhook_content(content):
    """Process webhook content and perform smart actions."""
    actions = []
    
    # Handle empty content
    if content is None:
        logger.warning("Received empty content")
        actions.append("⚠️ Empty content received")
        return actions
    
    # Copy to clipboard
    if copy_to_clipboard(content):
        actions.append("✓ Copied to clipboard")
    
    # Detect URLs but don't open them
    detected_urls = []
    
    if isinstance(content, dict):
        # Check for URLs in JSON values
        for key, value in content.items():
            if isinstance(value, str) and is_valid_url(value):
                detected_urls.append(value)
    elif isinstance(content, str):
        # Check if content itself is a URL
        if is_valid_url(content):
            detected_urls.append(content)
        else:
            # Extract URLs from text
            detected_urls.extend(extract_urls(content))
    
    # Add detected URLs to actions
    for url in detected_urls:
        actions.append(f"🔗 URL detected: {url}")
    
    return actions

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', webhooks=webhook_history)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive and process webhook data."""
    try:
        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine content type and extract data
        content_type = request.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # JSON payload
            content = request.json
            content_format = 'json'
        else:
            # Text or form data
            content = request.get_data(as_text=True)
            if not content and request.form:
                content = dict(request.form)
                content_format = 'form'
            else:
                content_format = 'text'
        
        # Process the content
        actions = process_webhook_content(content)
        
        # Save to history
        webhook_entry = {
            'timestamp': timestamp,
            'content': content,
            'content_format': content_format,
            'actions': actions
        }
        
        webhook_history.insert(0, webhook_entry)
        
        # Trim history if it's too long
        if len(webhook_history) > MAX_HISTORY:
            webhook_history.pop()
        
        # Return success response
        return jsonify({
            'status': 'success',
            'message': 'Webhook received and processed',
            'actions': actions
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        
        # Record the error in history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        webhook_entry = {
            'timestamp': timestamp,
            'content': f"Error: {str(e)}",
            'content_format': 'text',
            'actions': [],
            'is_error': True
        }
        webhook_history.insert(0, webhook_entry)
        
        return jsonify({
            'status': 'error',
            'message': f'Error processing webhook: {str(e)}'
        }), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear webhook history."""
    webhook_history.clear()
    flash('Webhook history cleared successfully')
    return redirect(url_for('index'))



@app.route('/test-webhook', methods=['POST'])
def test_webhook():
    """Endpoint to test webhook functionality."""
    try:
        test_content = request.form.get('content', '')
        actions = process_webhook_content(test_content)
        
        # Save to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        webhook_entry = {
            'timestamp': timestamp,
            'content': test_content,
            'content_format': 'text',
            'actions': actions,
            'is_test': True
        }
        
        webhook_history.insert(0, webhook_entry)
        
        # Trim history if it's too long
        if len(webhook_history) > MAX_HISTORY:
            webhook_history.pop()
        
        flash('Test webhook processed successfully')
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Error processing test webhook: {e}")
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download', methods=['GET'])
def download_files():
    """Create and download a ZIP file containing all application files."""
    try:
        # Create a BytesIO object to store ZIP file in memory
        memory_file = io.BytesIO()
        
        # Create the ZIP file in memory
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # List of files to include in the ZIP
            files_to_zip = [
                # Python files
                'main.py',
                'webhook_receiver.py',
                
                # Template files
                'templates/index.html',
                
                # Static files
                'static/css/custom.css',
                'static/js/app.js'
            ]
            
            # Add a requirements.txt file directly to the ZIP
            requirements_content = """flask==2.3.3
flask-sqlalchemy==3.1.1
gunicorn==21.2.0
pyperclip==1.8.2
psycopg2-binary==2.9.9
email-validator==2.0.0
zipfile36==0.1.3"""
            zf.writestr('requirements.txt', requirements_content)
            
            # Add a README.md with deployment instructions
            readme_content = """# Webhook Receiver

一个简单的webhook接收器应用，可以自动处理接收到的内容。

## 功能特点

- 接收webhook发送的内容
- 自动复制内容到剪贴板
- 自动检测URL（但不会自动打开）
- 支持JSON、表单数据和纯文本
- 保存webhook历史记录

## 部署指南

### 环境要求

- Python 3.8+
- 推荐使用虚拟环境

### 安装步骤

1. 创建并激活虚拟环境（可选但推荐）:
   ```
   python -m venv venv
   # 在Windows上
   venv\\Scripts\\activate
   # 在Linux/Mac上
   source venv/bin/activate
   ```

2. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

3. 运行应用:
   ```
   # 开发环境
   python main.py
   
   # 生产环境
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

4. 在浏览器中访问 http://localhost:5000

### 使用方法

1. 获取webhook URL: http://[你的服务器地址]:5000/webhook
2. 发送POST请求到该URL：
   ```
   # 发送JSON数据
   curl -X POST -H "Content-Type: application/json" -d '{"message":"test"}' http://[你的服务器地址]:5000/webhook
   
   # 或发送表单数据
   curl -X POST -d "message=Hello World" http://[你的服务器地址]:5000/webhook
   
   # 或发送纯文本
   curl -X POST -H "Content-Type: text/plain" -d "这是一条测试消息" http://[你的服务器地址]:5000/webhook
   ```
3. 应用会自动复制内容到剪贴板并检测其中的URL
4. 访问网页界面可查看请求历史记录和测试webhook

## 注意事项

- 在Linux环境中运行时，可能需要安装xclip或xsel才能使剪贴板功能正常工作:
  ```
  sudo apt-get install xclip
  ```
"""
            zf.writestr('README.md', readme_content)
            
            # Write files to the ZIP archive
            for file_path in files_to_zip:
                if os.path.exists(file_path):
                    # Read file and add to ZIP
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        zf.writestr(file_path, file_data)
        
        # Seek to beginning of the BytesIO object
        memory_file.seek(0)
        
        # Log download attempt
        logger.info("Files downloaded as webhook_receiver.zip")
        
        # Return the ZIP file
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='webhook_receiver.zip'
        )
        
    except Exception as e:
        logger.error(f"Error creating download: {e}")
        flash(f'Error creating download: {str(e)}')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
