FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建图片保存目录
RUN mkdir -p hunyuan_images

# 设置环境变量
ENV PORT=8080
ENV DEBUG=False

# 对外暴露端口
EXPOSE 8080

# 启动命令
CMD gunicorn --bind 0.0.0.0:$PORT server:app 