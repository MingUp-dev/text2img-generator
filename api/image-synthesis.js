// 阿里云图像生成API代理
import fetch from 'node-fetch';

export default async function handler(req, res) {
  // 设置CORS头，允许所有来源访问
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization'
  );
  
  // 处理预检请求
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  // 只允许POST请求
  if (req.method !== 'POST') {
    return res.status(405).json({ error: '只支持POST方法' });
  }
  
  try {
    const prompt = req.body.prompt;
    if (!prompt) {
      return res.status(400).json({ error: '缺少提示词参数' });
    }
    
    // 阿里云API密钥 - 在生产环境中应该使用环境变量存储
    const API_KEY = "sk-ce6d40e38d234ce8a1414f4be96868e6";
    
    // 调用阿里云API
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
      throw new Error(`API返回错误: ${response.status}`);
    }
    
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    console.error('API代理错误:', error);
    res.status(500).json({ error: `API调用失败: ${error.message}` });
  }
} 