# Webhook Receiver

一个简单的webhook接收器应用，可以自动处理接收到的内容。

## 功能特点

- 接收webhook发送的内容
- 自动复制内容到剪贴板
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
   venv\Scripts\activate
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
