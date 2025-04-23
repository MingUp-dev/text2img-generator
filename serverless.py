from http.server import BaseHTTPRequestHandler
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入Flask应用
from Text2img import app

# Vercel无服务器函数处理类
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # 使用Flask应用处理请求
        response = app.dispatch_request()
        self.wfile.write(response.data)
        return 