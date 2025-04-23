// server.js - 本地开发服务器和云服务部署
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fetch from 'node-fetch';

// 获取当前文件的目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 创建Express应用
const app = express();
const PORT = process.env.PORT || 5000;

// API密钥
const API_KEY = process.env.DASHSCOPE_API_KEY || 'sk-ce6d40e38d234ce8a1414f4be96868e6';

// 中间件设置
app.use(express.json());
app.use(express.static(__dirname)); // 提供静态文件

// 添加健康检查路由（云平台通常需要）
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// 确保根路径能正确响应
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// API路由 - 生成图片
app.post('/api/generate', async (req, res) => {
  console.log("收到生成请求:", req.body);
  try {
    const { prompt } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ success: false, message: '缺少提示词参数' });
    }

    // 调用阿里云DashScope API
    const response = await fetch('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
      method: 'POST',
      headers: {
        'X-DashScope-Async': 'enable',
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: "wanx2.1-t2i-turbo",
        input: { prompt: prompt },
        parameters: { size: "1024*1024", n: 1 }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API调用失败:', errorText);
      return res.status(response.status).json({ 
        success: false, 
        message: `API调用失败 (${response.status}): ${errorText}` 
      });
    }

    const data = await response.json();
    console.log("API响应:", data);
    const taskId = data.output.task_id;

    return res.status(200).json({
      success: true,
      taskId: taskId,
      message: '任务已提交，正在生成中...'
    });
  } catch (error) {
    console.error('处理请求时出错:', error);
    return res.status(500).json({
      success: false,
      message: `服务器错误: ${error.message}`
    });
  }
});

// API路由 - 查询状态
app.get('/api/status', async (req, res) => {
  console.log("收到状态查询请求:", req.query);
  try {
    const { taskId } = req.query;
    
    if (!taskId) {
      return res.status(400).json({ success: false, message: '缺少taskId参数' });
    }

    // 调用阿里云DashScope API查询任务状态
    const response = await fetch(`https://dashscope.aliyuncs.com/api/v1/tasks/${taskId}`, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('查询状态失败:', errorText);
      return res.status(response.status).json({ 
        success: false, 
        message: `查询状态失败 (${response.status}): ${errorText}`,
        status: 'FAILED'
      });
    }

    const apiData = await response.json();
    console.log("状态查询响应:", apiData);
    const taskStatus = apiData.output.task_status;
    let statusMessage = '任务处理中...';
    let imageUrl = null;

    // 处理不同任务状态
    if (taskStatus === 'SUCCEEDED') {
      statusMessage = '图片生成成功！';
      imageUrl = apiData.output.results[0].url;
    } else if (taskStatus === 'FAILED') {
      statusMessage = `图片生成失败: ${apiData.output.message || '未知错误'}`;
    }

    return res.status(200).json({
      success: true,
      status: taskStatus,
      message: statusMessage,
      imageUrl: imageUrl
    });
  } catch (error) {
    console.error('处理状态查询时出错:', error);
    return res.status(500).json({
      success: false,
      message: `服务器错误: ${error.message}`,
      status: 'FAILED'
    });
  }
});

// 处理所有其他路由返回index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// 启动服务器并监听指定端口
// 不再使用条件启动，确保在任何环境都会启动服务器
app.listen(PORT, '0.0.0.0', () => {
  console.log(`服务器启动在端口 ${PORT}`);
});

// 为了兼容性保留Vercel导出
export default app;