import json
import hmac
import hashlib
import datetime
import requests
import base64
import os
import time
from datetime import datetime, timezone
import uuid
import sys
import urllib.parse
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ========================= API密钥设置 =========================
# 从环境变量中获取API密钥，如果没有则使用默认值
# 部署到腾讯云时，可通过环境变量设置而无需修改代码
# ============================================================
secret_id = os.environ.get("SECRET_ID", "AKIDzpTt785oJdlfOwGOI0Xt2xgEbpy1tjU3")
secret_key = os.environ.get("SECRET_KEY", "QehaIn59zb2LWTDj292iDWccZP4jJkz2")

# API请求参数
service = "hunyuan"
host = "hunyuan.tencentcloudapi.com"
endpoint = "https://" + host
region = "ap-guangzhou"
submit_action = "SubmitHunyuanImageJob"  # 提交任务
query_action = "QueryHunyuanImageJob"    # 查询任务
version = "2023-09-01"
algorithm = "TC3-HMAC-SHA256"

# 创建保存图片的目录
download_dir = "hunyuan_images"
os.makedirs(download_dir, exist_ok=True)

# 风格映射，根据腾讯云API文档
# 参考文档：https://cloud.tencent.com/document/api/1729/105969
style_options = {
    "riman": "riman",       # 日漫风格
    "dongman": "dongman",   # 动漫风格
    "youhua": "youhua",     # 油画风格
    "shuimo": "shuimo",     # 水墨风格
    "chunmei": "chunmei"    # 国风Q版
}

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_auth_header(action, data):
    # 获取当前UTC时间并格式化
    timestamp = int(datetime.now(timezone.utc).timestamp())
    date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # 拼接规范请求串
    http_request_method = "POST"
    canonical_uri = "/"
    canonical_querystring = ""
    canonical_headers = f"content-type:application/json\nhost:{host}\nx-tc-action:{action.lower()}\n"
    signed_headers = "content-type;host;x-tc-action"
    payload = json.dumps(data)
    hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"
    
    # 拼接待签名字符串
    credential_scope = f"{date}/{service}/tc3_request"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
    
    # 计算签名
    secret_date = sign(('TC3' + secret_key).encode('utf-8'), date)
    secret_service = sign(secret_date, service)
    secret_signing = sign(secret_service, 'tc3_request')
    signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # 拼接Authorization
    authorization = f"{algorithm} Credential={secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    # 组装请求头
    headers = {
        'Content-Type': 'application/json',
        'Host': host,
        'X-TC-Action': action,
        'X-TC-Region': region,
        'X-TC-Timestamp': str(timestamp),
        'X-TC-Version': version,
        'Authorization': authorization,
    }
    return headers, payload

def submit_job(prompt, style="riman", resolution="1024:1024"):
    """提交混元生图任务，固定只生成一张图片"""
    
    request_data = {
        "Prompt": prompt,
        "Style": style,          # 图片风格
        "Resolution": resolution,  # 图片分辨率
        "Num": 1                # 固定只生成1张图片
    }
    
    headers, payload = get_auth_header(submit_action, request_data)
    
    print(f"正在提交生成图片任务，提示词: {prompt}")
    response = requests.post(endpoint, headers=headers, data=payload)
    
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if "Response" in result and "JobId" in result["Response"]:
            job_id = result["Response"]["JobId"]
            print(f"\n任务提交成功，任务ID: {job_id}")
            return job_id
        else:
            print(f"API调用成功但未返回预期结果: {result}")
    else:
        print(f"API调用失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
    return None

def query_job_status(job_id):
    """查询任务状态"""
    query_data = {
        "JobId": job_id
    }
    
    headers, payload = get_auth_header(query_action, query_data)
    print(f"正在查询任务状态，任务ID: {job_id}")
    
    try:
        response = requests.post(endpoint, headers=headers, data=payload)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # 检查是否有错误
            if "Response" in result and "Error" in result["Response"]:
                print(f"查询出错: {result['Response']['Error']['Message']}")
                return None, None, "ERROR"
            
            # 提取任务状态和图片URL
            if "Response" in result:
                response_data = result["Response"]
                job_status = response_data.get("JobStatusMsg", "Unknown")
                job_status_code = response_data.get("JobStatusCode", "0")
                
                # 提取图片URL
                image_urls = response_data.get("ResultImage", [])
                revised_prompts = response_data.get("RevisedPrompt", [])
                
                print(f"任务状态: {job_status} (代码: {job_status_code})")
                if image_urls:
                    print(f"找到 {len(image_urls)} 张生成的图片")
                
                if revised_prompts:
                    print(f"提示词被扩展为: {revised_prompts[0]}")
                
                return image_urls, revised_prompts, job_status_code
            else:
                print("响应结构不符合预期")
                return None, None, "UNKNOWN"
        else:
            print(f"查询失败: {response.text}")
            return None, None, "FAILED"
    except Exception as e:
        print(f"查询异常: {str(e)}")
        return None, None, "ERROR"

def download_image(url, save_path):
    """下载图片到本地"""
    try:
        print(f"正在下载图片: {save_path}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"图片已保存到: {save_path}")
            return True
        else:
            print(f"下载图片失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"下载异常: {str(e)}")
        return False

def generate_and_download(prompt, style="riman", resolution="1024:1024", wait_time=10, max_retries=30):
    """生成并下载图片的主函数，固定只生成一张图片"""
    # 检查密钥是否有效
    if not secret_id or not secret_key or secret_id == "YOUR_SECRET_ID" or secret_key == "YOUR_SECRET_KEY":
        print("请先设置您的SecretId和SecretKey！可通过环境变量SECRET_ID和SECRET_KEY设置")
        return

    # 1. 提交任务
    job_id = submit_job(prompt, style, resolution)
    if not job_id:
        print("任务提交失败")
        return

    # 创建带时间戳的目录用于保存图片
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    batch_dir = f"{download_dir}/batch_{timestamp}"
    os.makedirs(batch_dir, exist_ok=True)
    
    # 2. 轮询任务状态
    print("\n开始等待任务完成，轮询间隔: {}秒".format(wait_time))
    for retry in range(1, max_retries + 1):
        print(f"\n第{retry}次查询任务状态...")
        image_urls, revised_prompts, status_code = query_job_status(job_id)
        
        # 处理完成
        if status_code == "5":
            print("\n任务已完成！")
            if image_urls and len(image_urls) > 0:
                # 3. 下载图片 (只下载第一张)
                url = image_urls[0]
                save_path = f"{batch_dir}/image.jpg"
                print("\n开始下载图片...")
                if download_image(url, save_path):
                    print(f"图片下载成功")
                else:
                    print(f"图片下载失败")
                
                # 保存扩展后的提示词到文本文件
                if revised_prompts and len(revised_prompts) > 0:
                    prompt_file = f"{batch_dir}/prompt.txt"
                    with open(prompt_file, 'w', encoding='utf-8') as f:
                        f.write(f"原始提示词: {prompt}\n\n")
                        f.write("扩展后的提示词:\n")
                        f.write(f"{revised_prompts[0]}\n")
                    print(f"提示词信息已保存到: {prompt_file}")
                
                print(f"\n图片已下载到: {save_path}")
                return save_path
            else:
                print("任务完成但未找到图片URL")
                return None
        
        # 处理失败
        elif status_code == "6":
            print("\n任务处理失败")
            return None
        
        # 其他状态，继续等待
        else:
            wait_msg = ""
            if status_code == "1":
                wait_msg = "任务已提交，等待处理"
            elif status_code == "2":
                wait_msg = "任务排队中"
            elif status_code == "3":
                wait_msg = "任务处理中"
            else:
                wait_msg = f"未知状态 (代码: {status_code})"
            
            print(f"{wait_msg}，将在 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    # 超过最大重试次数
    print(f"\n超过最大查询次数 ({max_retries})，任务可能仍在处理中")
    print("请稍后使用任务ID查询结果:")
    print(f"任务ID: {job_id}")
    return None

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='腾讯混元大模型图像生成工具')
    parser.add_argument('--prompt', type=str, help='图片描述（提示词）')
    parser.add_argument('--style', type=str, default='riman', 
                        choices=['riman', 'dongman', 'youhua', 'shuimo', 'chunmei'],
                        help='图片风格 (默认: riman)')
    parser.add_argument('--width', type=int, default=1024, help='图片宽度 (默认: 1024)')
    parser.add_argument('--height', type=int, default=1024, help='图片高度 (默认: 1024)')
    return parser.parse_args()

def main():
    """主函数"""
    print("=" * 60)
    print("腾讯混元大模型图像生成工具")
    print("=" * 60)
    
    # 解析命令行参数
    args = parse_args()
    
    # 用户输入提示词
    if args.prompt:
        prompt = args.prompt
    elif len(sys.argv) >= 2 and not sys.argv[1].startswith('--'):
        prompt = sys.argv[1]
    else:
        prompt = input("请输入图片描述 (提示词): ")
    
    # 获取风格
    if args.style and args.style in style_options:
        style = args.style
    else:
        # 如果命令行没有指定风格，则使用默认值或交互式选择
        print("\n可用的图片风格:")
        print("1: riman - 日漫风格")
        print("2: dongman - 动漫风格")
        print("3: youhua - 油画风格")
        print("4: shuimo - 水墨风格")
        print("5: chunmei - 国风Q版")
        style_choice = input("请选择图片风格 (输入数字，默认1): ")
        
        style_map = {
            "1": "riman",
            "2": "dongman",
            "3": "youhua",
            "4": "shuimo",
            "5": "chunmei"
        }
        
        if style_choice in style_map:
            style = style_map[style_choice]
            print(f"已选择图片风格: {style}")
        else:
            style = "riman"
            print(f"选择无效，使用默认风格: {style}")
    
    # 生成分辨率
    width = args.width
    height = args.height
    resolution = f"{width}:{height}"
    
    # 生成并下载图片（固定只生成一张）
    print("\n开始生成图片...")
    output_path = generate_and_download(prompt, style, resolution)
    
    if output_path:
        print("\n所有操作已完成！")
        print(f"图片已保存到: {output_path}")
    else:
        print("\n操作未完成，请检查错误信息")

if __name__ == "__main__":
    main() 