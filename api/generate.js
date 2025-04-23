// api/generate.js - 处理图像生成请求的无服务器函数
import fetch from 'node-fetch';

// API密钥 - 在Vercel中作为环境变量使用
const API_KEY = process.env.DASHSCOPE_API_KEY || 'sk-ce6d40e38d234ce8a1414f4be96868e6';

export default async function handler(req, res) {
  // 只允许POST请求
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, message: '只允许POST请求' });
  }

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
} 
