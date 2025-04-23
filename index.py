from flask import Flask, Request
import sys
import os

# 添加项目根目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入主应用但不运行
from Text2img import app as flask_app

# Vercel无服务器函数入口点 - 这是Vercel的特定格式
def handler(request, response):
    # 将请求转发给Flask应用
    return flask_app(request.environ, start_response)

# 这是Vercel使用的标准WSGI接口
def start_response(status, headers):
    return [status, headers]

# Vercel使用此文件作为无服务器函数入口
# 这种方式更好地支持Vercel的无服务器函数架构 