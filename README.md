# AI图像生成器

一个基于阿里云DashScope API的AI图像生成应用，使用纯前端实现。

## 功能

- 根据文本提示生成AI图像
- 实时查询图像生成任务状态
- 下载生成的图像

## 技术栈

- 纯前端：HTML, CSS, JavaScript
- API：阿里云DashScope

## 部署到GitHub Pages

### 步骤1: 创建GitHub仓库

1. 在GitHub上创建一个新仓库
2. 克隆仓库到本地：
   ```
   git clone https://github.com/你的用户名/你的仓库名.git
   ```

### 步骤2: 添加项目文件

将以下文件添加到仓库中：
- index.html
- style.css
- script.js
- README.md
- 404.html (可选)

### 步骤3: 提交并推送代码

```bash
git add .
git commit -m "初始提交"
git push origin main
```

### 步骤4: 启用GitHub Pages

1. 在GitHub仓库页面，点击"Settings"
2. 在左侧菜单中点击"Pages"
3. 在"Source"部分，选择"Deploy from a branch"
4. 在"Branch"下拉菜单中选择"main"，文件夹选择"/ (root)"
5. 点击"Save"保存设置

几分钟后，您的网站将在`https://你的用户名.github.io/你的仓库名`上线。

## 注意事项

- **安全警告**：此实现将API密钥直接暴露在前端代码中，仅供学习和测试使用。不建议在生产环境中使用此方法。
- 图像生成是异步的，可能需要几秒到几十秒不等的处理时间。
- 建议将API密钥替换为您自己的密钥，以避免超出配额限制。

## 本地测试

最简单的方法是使用VS Code的Live Server扩展或Python的SimpleHTTPServer：

```bash
# 使用Python 3启动简单HTTP服务器
python -m http.server 8000
```

然后在浏览器中访问 http://localhost:8000 