import os
import sys
import subprocess
import json
import time
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='.')

# 确保图像保存目录存在
if not os.path.exists('hunyuan_images'):
    os.makedirs('hunyuan_images')

@app.route('/')
def index():
    return send_from_directory('.', 'display_image.html')

@app.route('/generate_image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        style = data.get('style', '纯美写实')
        size = data.get('size', '1024x1024')
        
        # 解析尺寸
        try:
            width, height = map(int, size.split('x'))
        except ValueError:
            width, height = 1024, 1024
            
        # 记录请求信息
        app.logger.info(f"请求生成图像: prompt='{prompt}', style='{style}', size='{width}x{height}'")
        
        # 构建命令
        cmd = [
            sys.executable,  # 使用当前Python解释器
            'hunyuan_complete.py',
            f'--prompt={prompt}',
            f'--style={style}',
            f'--width={width}',
            f'--height={height}'
        ]
        
        app.logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )
        
        # 打印完整的输出用于调试
        app.logger.info(f"命令输出: {result.stdout}")
        if result.stderr:
            app.logger.error(f"命令错误: {result.stderr}")
        
        # 检查执行结果
        if result.returncode != 0:
            error_msg = result.stderr or "未知错误"
            app.logger.error(f"命令执行失败，返回码: {result.returncode}, 错误: {error_msg}")
            return jsonify({
                'success': False,
                'error': f"图像生成失败: {error_msg}"
            }), 500
        
        app.logger.info("命令执行成功，正在查找生成的图像...")
        
        # 等待一小段时间，确保图像文件已写入磁盘
        time.sleep(1)
            
        # 找到最新生成的图像
        try:
            # 查找batch目录
            batch_dirs = [d for d in os.listdir('hunyuan_images') if d.startswith('batch_')]
            
            if not batch_dirs:
                app.logger.error("未找到生成的图像批次目录")
                return jsonify({
                    'success': False,
                    'error': "未找到生成的图像，请检查日志"
                }), 404
            
            # 按修改时间排序，获取最新的批次目录
            latest_batch = max(
                batch_dirs, 
                key=lambda d: os.path.getmtime(os.path.join('hunyuan_images', d))
            )
            
            batch_path = os.path.join('hunyuan_images', latest_batch)
            image_path = os.path.join(batch_path, 'image.jpg')
            
            # 检查文件是否实际存在
            if not os.path.exists(image_path):
                app.logger.error(f"文件路径存在但文件不存在: {image_path}")
                return jsonify({
                    'success': False,
                    'error': "找到的图像文件不存在"
                }), 404
                
            image_size = os.path.getsize(image_path)
            app.logger.info(f"找到最新图像: {image_path}, 大小: {image_size} 字节")
            
            if image_size == 0:
                app.logger.warning("警告: 图像文件大小为0")
                return jsonify({
                    'success': False,
                    'error': "生成的图像文件大小为0，可能是生成失败"
                }), 500
            
            # 返回相对URL路径
            url_path = f'/hunyuan_images/{latest_batch}/image.jpg'
            
            # 读取提示词信息
            prompt_info = None
            prompt_path = os.path.join(batch_path, 'prompt.txt')
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_info = f.read()
            
            app.logger.info(f"成功返回图像路径: {url_path}")
            return jsonify({
                'success': True,
                'message': '图像生成成功',
                'image_path': url_path,
                'prompt_info': prompt_info,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            app.logger.error(f"查找图像文件时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"查找生成的图像时出错: {str(e)}"
            }), 500
            
    except Exception as e:
        app.logger.error(f"服务器错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"服务器错误: {str(e)}"
        }), 500

@app.route('/hunyuan_images/<path:filename>')
def serve_image(filename):
    app.logger.info(f"请求访问图像: {filename}")
    
    # 从文件路径中提取路径部分和文件名部分
    parts = filename.split('/')
    if len(parts) > 1:
        directory = '/'.join(parts[:-1])
        file_name = parts[-1]
        return send_from_directory(os.path.join('hunyuan_images', directory), file_name)
    else:
        return send_from_directory('hunyuan_images', filename)

if __name__ == '__main__':
    # 获取环境变量中的端口，如果没有则使用5000
    port = int(os.environ.get('PORT', 5000))
    
    # 获取环境变量中的调试模式设置，默认为开发环境开启
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    app.logger.info(f"启动服务器, 端口: {port}, 调试模式: {'开启' if debug_mode else '关闭'}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode) 