import requests
import os
import time
import threading
import json
from pathlib import Path
from flask import Flask, render_template_string, request, redirect, url_for, jsonify

# 请设置您的API密钥
DASHSCOPE_API_KEY = "sk-ce6d40e38d234ce8a1414f4be96868e6"  # 需要替换

app = Flask(__name__)
# 创建image目录只为了保持兼容性
image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image")
Path(image_dir).mkdir(exist_ok=True)

# 设置全局变量来存储当前任务状态
generation_status = {
    "in_progress": False,  # 初始状态设为False
    "message": "",
    "last_prompt": "",
    "image_url": None,  # 存储图片URL而不是本地文件
    "last_update": 0  # 上次状态更新的时间戳
}

def generate_image_task(prompt, size="1024*1024", n=1):
    """在后台线程中生成图片的任务"""
    global generation_status
    
    try:
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        headers = {
            "X-DashScope-Async": "enable",
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "wanx2.1-t2i-turbo",
            "input": {"prompt": prompt},
            "parameters": {"size": size, "n": n}
        }

        # 提交生成请求
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        task_id = response.json()["output"]["task_id"]
        print(f"任务已提交，任务ID: {task_id}")
        
        generation_status["message"] = "任务已提交，正在生成中..."
        generation_status["last_update"] = time.time()

        # 设置最大尝试次数和超时时间
        max_attempts = 30
        attempts = 0
        
        # 检查任务状态
        while attempts < max_attempts:
            status_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
            status_response = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_response.json()

            if status_data["output"]["task_status"] == "SUCCEEDED":
                print("图像生成成功！")
                image_url = status_data["output"]["results"][0]["url"]
                print("结果URL:", image_url)
                
                # 直接保存URL而不下载图片
                generation_status["image_url"] = image_url
                generation_status["message"] = "图片生成成功！"
                generation_status["last_update"] = time.time()
                break
                
            elif status_data["output"]["task_status"] == "FAILED":
                error_msg = status_data["output"].get("message", "未知错误")
                print(f"图像生成失败: {error_msg}")
                generation_status["message"] = f"图片生成失败: {error_msg}"
                generation_status["last_update"] = time.time()
                break

            print("任务处理中...")
            generation_status["message"] = f"任务处理中...({attempts+1}/{max_attempts})"
            generation_status["last_update"] = time.time()
            time.sleep(2)
            attempts += 1
            
        if attempts >= max_attempts:
            generation_status["message"] = "生成超时，请重试"
            generation_status["last_update"] = time.time()
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        generation_status["message"] = f"网络请求错误: {str(e)}"
        generation_status["last_update"] = time.time()
    except Exception as e:
        print(f"发生错误: {e}")
        generation_status["message"] = f"发生错误: {str(e)}"
        generation_status["last_update"] = time.time()
    finally:
        generation_status["in_progress"] = False
        generation_status["last_update"] = time.time()

def generate_image(prompt, size="1024*1024", n=1):
    """启动图片生成的后台任务"""
    global generation_status
    
    # 如果已经有任务在进行中，则返回
    if generation_status["in_progress"]:
        return False
        
    # 重置状态
    generation_status["in_progress"] = True
    generation_status["message"] = "准备生成图片..."
    generation_status["last_prompt"] = prompt
    generation_status["image_url"] = None
    generation_status["last_update"] = time.time()
    
    # 创建并启动后台线程
    thread = threading.Thread(
        target=generate_image_task, 
        args=(prompt, size, n)
    )
    thread.daemon = True
    thread.start()
    
    return True

@app.route('/status')
def status():
    """返回当前生成任务的状态"""
    return jsonify({
        "in_progress": generation_status["in_progress"],
        "message": generation_status["message"],
        "image_url": generation_status["image_url"],
        "last_update": generation_status["last_update"]
    })

@app.route('/', methods=['GET', 'POST'])
def home():
    global generation_status
    
    if request.method == 'POST':
        prompt = request.form.get('prompt', '')
        if prompt and not generation_status["in_progress"]:
            generate_image(prompt)
            # 重定向以避免表单重复提交
            return redirect(url_for('home'))
    
    # 如果没有当前提示词，使用默认值
    prompt = generation_status["last_prompt"] or "芙莉莲"
    message = generation_status["message"]
    image_url = generation_status["image_url"]
    is_generating = generation_status["in_progress"]
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI图像生成</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                text-align: center;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #333;
                margin-bottom: 30px;
            }}
            .form-container {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            input[type="text"] {{
                width: 70%;
                padding: 10px;
                margin-right: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }}
            button {{
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                {{"opacity: 0.7; cursor: not-allowed;" if is_generating else ""}}
            }}
            button:hover {{
                background-color: {{"#45a049" if not is_generating else "#4CAF50"}};
            }}
            .image-container {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                min-height: 400px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                position: relative;
            }}
            .image-wrapper {{
                position: relative;
                display: inline-block;
                margin-top: 20px;
            }}
            img {{
                max-width: 100%;
                max-height: 500px;
                display: block;
            }}
            .download-btn {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                cursor: pointer;
                transition: 0.3s;
                display: flex;
                align-items: center;
                font-size: 14px;
            }}
            .download-btn:hover {{
                background-color: rgba(0, 0, 0, 0.9);
            }}
            .download-icon {{
                margin-right: 6px;
                width: 16px;
                height: 16px;
                fill: white;
            }}
            .message {{
                color: #666;
                margin: 10px 0;
                font-weight: bold;
            }}
            .placeholder {{
                width: 300px;
                height: 300px;
                border: 2px dashed #ddd;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #aaa;
            }}
            .status {{
                margin-top: 10px;
                font-size: 14px;
                color: {{"#4CAF50" if message and "成功" in message else "#f44336" if message and ("失败" in message or "错误" in message) else "#2196F3"}};
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                min-height: 30px;
            }}
            /* 添加动画 */
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .loader {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                animation: spin 1s linear infinite;
                display: none; /* 初始隐藏，通过JS控制 */
            }}
            #result-image {{
                display: {{"block" if image_url else "none"}};
            }}
        </style>
        <script>
            // 页面加载完成后立即执行
            document.addEventListener('DOMContentLoaded', function() {{
                const loader = document.getElementById('loading-indicator');
                const statusText = document.getElementById('status-text');
                const resultImage = document.getElementById('result-image');
                const downloadButton = document.getElementById('download-button');
                const imageContainer = document.querySelector('.image-container');
                const placeholder = document.querySelector('.placeholder');
                
                // 检查初始状态
                checkStatus();
                
                // 定期检查状态
                function checkStatus() {{
                    fetch('/status')
                        .then(response => response.json())
                        .then(data => {{
                            // 更新加载状态
                            if (data.in_progress) {{
                                loader.style.display = 'inline-block';
                                if (statusText) statusText.textContent = data.message;
                                // 任务进行中时继续检查状态
                                setTimeout(checkStatus, 1000);
                            }} else {{
                                // 任务完成后
                                loader.style.display = 'none';
                                if (statusText) statusText.textContent = data.message;
                                
                                // 如果有图片URL，显示图片
                                if (data.image_url) {{
                                    if (resultImage) {{
                                        resultImage.src = data.image_url;
                                        resultImage.style.display = 'none'; // 先隐藏图片，等onload事件触发再显示
                                        resultImage.onload = function() {{
                                            resultImage.style.display = 'block';
                                            if (downloadButton) {{
                                                downloadButton.style.display = 'flex';
                                                downloadButton.onclick = function() {{ downloadImage(data.image_url); }};
                                            }}
                                        }};
                                    }}
                                    if (placeholder) placeholder.style.display = 'none';
                                }} else {{
                                    if (downloadButton) downloadButton.style.display = 'none';
                                }}
                            }}
                        }})
                        .catch(error => {{
                            console.error('Error fetching status:', error);
                            setTimeout(checkStatus, 3000); // 出错时稍后重试
                        }});
                }}
            }});
            
            // 下载图片的函数
            function downloadImage(imageUrl) {{
                if (!imageUrl) return;
                
                // 创建一个临时链接元素
                const link = document.createElement('a');
                link.href = imageUrl;
                
                // 从URL中提取文件名
                const filename = imageUrl.split('/').pop().split('?')[0];
                link.download = "{prompt}_" + filename;
                
                // 模拟点击下载
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
        </script>
    </head>
    <body>
        <h1>AI图像生成器</h1>
        
        <div class="form-container">
            <form method="POST">
                <input type="text" name="prompt" placeholder="输入提示词..." value="{prompt}" required {{"disabled" if is_generating else ""}}>
                <button type="submit" {{"disabled" if is_generating else ""}}>生成图片</button>
            </form>
            <div class="status">
                <div class="loader" id="loading-indicator"></div>
                <span id="status-text">{message}</span>
            </div>
        </div>
        
        <div class="image-container">
            <h2>生成结果</h2>
            <div class="image-wrapper" style="display: {{'inline-block' if image_url else 'none'}}">
                <img id="result-image" src="{image_url or ''}" alt="生成的图片" onload="this.style.display='block'; document.getElementById('download-button').style.display='flex';" style="display: none;">
                <button id="download-button" class="download-btn" style="display: none;" onclick="downloadImage('{image_url or ''}')">
                    <svg class="download-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                    </svg>
                    下载
                </button>
            </div>
            <div class="placeholder" style="display: {{'none' if image_url else 'flex'}}">尚未生成图片</div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == "__main__":
    # 本地运行模式
    print(f"启动网页服务器，请访问 http://127.0.0.1:5000")
    app.run(debug=True, threaded=True)
else:
    # Vercel部署模式
    # 确保应用可以作为WSGI应用程序被Vercel导入
    # 不要在这里启动服务器
    pass