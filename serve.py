#!/usr/bin/env python3
"""
简单的HTTP服务器，用于本地测试AI图像生成器
"""

import http.server
import socketserver
import os
import webbrowser
import sys

# 设置服务器端口
PORT = 8000

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """处理CORS请求的HTTP请求处理程序"""
    
    def end_headers(self):
        # 添加CORS头信息
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        # 处理OPTIONS预检请求
        self.send_response(200)
        self.end_headers()

def main():
    """启动HTTP服务器并在浏览器中打开页面"""
    try:
        # 创建HTTP服务器
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print(f"启动服务器在 http://localhost:{PORT}")
            print("按下 Ctrl+C 停止服务器")
            
            # 在浏览器中打开URL
            webbrowser.open(f"http://localhost:{PORT}")
            
            # 开始服务
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 