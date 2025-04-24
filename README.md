# 腾讯云文生图API调用示例

本项目包含两个调用腾讯云文生图API的Python脚本示例：
1. `text_to_image.py` - 调用文生图轻量版API (TextToImageLite)
2. `hunyuan_image.py` - 调用混元生图API (SubmitHunyuanImageJob)

## 开通腾讯云文生图服务

### 开通文生图轻量版服务
1. 登录腾讯云官网(https://cloud.tencent.com/)
2. 搜索"文生图轻量版"或直接访问AIGC服务页面
3. 找到文生图轻量版服务并点击开通
4. 阅读并同意服务协议
5. 可能需要完成实名认证（如果尚未完成）
6. 选择合适的付费方案（按调用次数计费）

### 开通混元生图服务
1. 登录腾讯云官网(https://cloud.tencent.com/)
2. 搜索"混元生图"或直接访问混元大模型服务页面
3. 找到混元生图服务并点击开通
4. 阅读并同意服务协议
5. 完成实名认证（如果尚未完成）
6. 选择合适的付费方案

## 获取API密钥

两个脚本都需要使用您的腾讯云API密钥进行认证：
1. 登录[腾讯云控制台](https://console.cloud.tencent.com/)
2. 前往【访问管理】>【API密钥管理】
3. 获取或创建您的SecretId和SecretKey
4. 将获取到的密钥复制到脚本中对应位置

## 使用文生图轻量版API (text_to_image.py)

文生图轻量版是一个同步API，调用后会直接返回生成的图片。

使用步骤：
1. 编辑`text_to_image.py`文件，替换以下内容：
   - 将`secret_id`和`secret_key`替换为您的实际密钥
   - 根据需要修改`prompt`为您想要生成的图片描述

2. 运行脚本：
```
python text_to_image.py
```

## 使用混元生图API (hunyuan_image.py)

混元生图是一个异步API，需要先提交任务获取JobId，然后查询任务状态获取结果。

使用步骤：
1. 编辑`hunyuan_image.py`文件，替换以下内容：
   - 将`secret_id`和`secret_key`替换为您的实际密钥
   - 根据需要修改`prompt`为您想要生成的图片描述
   - 可选：修改风格、分辨率等参数

2. 运行脚本：
```
python hunyuan_image.py
```

脚本会自动提交任务，然后定期查询任务状态，直到任务完成并下载生成的图片。

## 相关文档

- [文生图轻量版API文档](https://cloud.tencent.com/document/product/1729/108738)
- [混元生图API文档](https://cloud.tencent.com/document/product/1729/105969)
- [混元生图风格列表](https://cloud.tencent.com/document/product/1729/105846)

## 注意事项

- 使用API会产生相应的费用，请确保账户中有足够的余额
- 系统时间应与标准时间同步，以避免签名过期错误
- 确保网络连接正常
- 生成的图片可能有版权和使用限制，请遵守腾讯云的服务条款

# 腾讯混元图像生成应用

基于腾讯混元大模型的AI图像生成Web应用，提供简单易用的用户界面，让用户可以通过文字描述生成各种风格的图片。

## 项目特点

- 简洁美观的Web界面
- 支持多种图片风格（日漫、动漫、油画、水墨、国风Q版）
- 实时生成和显示图片
- 自动保存生成历史

## 在线体验

访问：[https://你的腾讯云Web托管URL](#)

## 本地运行

### 1. 克隆仓库

```bash
git clone https://github.com/你的用户名/hunyuan-image-generator.git
cd hunyuan-image-generator
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

编辑`hunyuan_complete.py`和`server.py`文件，替换以下内容：
- 将`secret_id`和`secret_key`替换为您的腾讯云API密钥

### 4. 运行服务器

```bash
python server.py
```

访问 http://localhost:5000 即可使用应用。

## 部署到GitHub

### 1. 创建GitHub仓库

1. 登录GitHub账号
2. 点击右上角"+"图标，选择"New repository"
3. 填写仓库名称（例如：hunyuan-image-generator）
4. 选择仓库可见性（公开或私有）
5. 点击"Create repository"

### 2. 推送代码到GitHub

```bash
# 初始化Git仓库（如果尚未初始化）
git init

# 添加远程仓库
git remote add origin https://github.com/你的用户名/hunyuan-image-generator.git

# 添加所有文件到暂存区
git add .

# 提交更改
git commit -m "初始提交"

# 推送到GitHub
git push -u origin main
```

## 部署到腾讯云Web托管

### 1. 准备工作

- 注册腾讯云账号并实名认证
- 开通腾讯云[Web应用托管](https://console.cloud.tencent.com/webify)服务

### 2. 创建新应用

1. 登录腾讯云控制台
2. 进入Web应用托管服务
3. 点击"新建应用"
4. 选择"GitHub仓库"作为部署来源
5. 授权并选择你刚刚创建的GitHub仓库
6. 设置应用名称和地域

### 3. 配置部署设置

1. 框架设置选择"Flask"
2. 填写启动命令：`gunicorn server:app -b 0.0.0.0:$PORT`
3. 填写构建命令：`pip install -r requirements.txt`
4. 将环境变量中加入API密钥:
   - SECRET_ID: 你的腾讯云SECRET_ID
   - SECRET_KEY: 你的腾讯云SECRET_KEY

### 4. 部署应用

1. 点击"开始部署"
2. 等待部署完成
3. 部署成功后，点击应用URL即可访问

## 常见问题

**Q: 图片无法生成或显示？**
A: 请确保您的API密钥正确且有效，并且账户中有足够的额度。

**Q: 部署到腾讯云后报错？**
A: 检查环境变量是否正确设置，确保应用有足够的内存配额。

## 相关文档

- [腾讯混元生图API文档](https://cloud.tencent.com/document/product/1729/105969)
- [Flask文档](https://flask.palletsprojects.com/)
- [腾讯云Web应用托管文档](https://cloud.tencent.com/document/product/1724) 