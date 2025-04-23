// 阿里云图像变体生成API代理
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
    const { imageUrl, prompt } = req.body;
    
    if (!imageUrl) {
      return res.status(400).json({ error: '缺少参考图片URL' });
    }
    
    // 阿里云API密钥 - 在生产环境中应该使用环境变量存储
    const API_KEY = "sk-ce6d40e38d234ce8a1414f4be96868e6";
    
    // 准备请求体
    const requestBody = {
      model: "wanx2.1-style-t2i",
      input: {
        image_url: imageUrl
      },
      parameters: { 
        size: "1024*1024", 
        n: 1
      }
    };
    
    // 如果提供了提示词，则添加到请求中
    if (prompt && prompt.trim()) {
      requestBody.input.prompt = prompt.trim();
    }
    
    // 调用阿里云API
    const response = await fetch('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
      method: 'POST',
      headers: {
        'X-DashScope-Async': 'enable',
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API调用失败:', errorText);
      return res.status(response.status).json({ 
        error: `API调用失败 (${response.status}): ${errorText}` 
      });
    }
    
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    console.error('API代理错误:', error);
    res.status(500).json({ error: `API调用失败: ${error.message}` });
  }
} 