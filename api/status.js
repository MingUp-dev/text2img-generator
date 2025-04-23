// api/status.js - 查询任务状态的无服务器函数
import fetch from 'node-fetch';

// API密钥 - 在Vercel中作为环境变量使用
const API_KEY = process.env.DASHSCOPE_API_KEY || 'sk-ce6d40e38d234ce8a1414f4be96868e6';

export default async function handler(req, res) {
  // 只允许GET请求
  if (req.method !== 'GET') {
    return res.status(405).json({ success: false, message: '只允许GET请求' });
  }

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
}