document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('generate-form');
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const loader = document.getElementById('loading-indicator');
    const statusText = document.getElementById('status-text');
    const resultImage = document.getElementById('result-image');
    const downloadButton = document.getElementById('download-button');
    const imageWrapper = document.getElementById('image-wrapper');
    const placeholder = document.getElementById('placeholder');

    // 默认提示词
    promptInput.value = '芙莉莲';

    let taskId = null;
    let checkStatusInterval = null;
    
    // API密钥 - 注意：在前端暴露API密钥存在安全风险
    const API_KEY = "sk-ce6d40e38d234ce8a1414f4be96868e6";

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const prompt = promptInput.value.trim();
        
        if (!prompt) {
            statusText.textContent = '请输入提示词';
            statusText.style.color = '#f44336';
            return;
        }

        // 禁用表单
        generateBtn.disabled = true;
        promptInput.disabled = true;
        
        // 显示加载状态
        loader.style.display = 'inline-block';
        statusText.textContent = '提交任务中...';
        statusText.style.color = '#2196F3';
        
        try {
            // 直接调用阿里云DashScope API
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
                throw new Error(`API调用失败 (${response.status}): ${await response.text()}`);
            }
            
            const data = await response.json();
            taskId = data.output.task_id;
            statusText.textContent = '任务已提交，正在生成中...';
            
            // 开始轮询检查任务状态
            startCheckingStatus();
        } catch (error) {
            console.error('错误:', error);
            statusText.textContent = `发生错误: ${error.message}`;
            statusText.style.color = '#f44336';
            
            // 恢复表单
            generateBtn.disabled = false;
            promptInput.disabled = false;
            loader.style.display = 'none';
        }
    });

    function startCheckingStatus() {
        // 清除现有的定时器
        if (checkStatusInterval) {
            clearInterval(checkStatusInterval);
        }
        
        // 设置新的定时器，每3秒检查一次状态
        checkStatusInterval = setInterval(checkTaskStatus, 3000);
    }

    async function checkTaskStatus() {
        if (!taskId) return;
        
        try {
            // 直接调用阿里云API检查状态
            const response = await fetch(`https://dashscope.aliyuncs.com/api/v1/tasks/${taskId}`, {
                headers: {
                    'Authorization': `Bearer ${API_KEY}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`检查状态失败 (${response.status}): ${await response.text()}`);
            }
            
            const apiData = await response.json();
            const taskStatus = apiData.output.task_status;
            let statusMessage = '任务处理中...';
            let imageUrl = null;
            
            if (taskStatus === 'SUCCEEDED') {
                statusMessage = '图片生成成功！';
                imageUrl = apiData.output.results[0].url;
            } else if (taskStatus === 'FAILED') {
                statusMessage = `图片生成失败: ${apiData.output.message || '未知错误'}`;
            }
            
            const data = {
                status: taskStatus,
                message: statusMessage,
                imageUrl: imageUrl
            };
            
            // 更新状态文本
            statusText.textContent = data.message;
            
            if (data.status === 'SUCCEEDED') {
                // 任务成功
                statusText.style.color = '#4CAF50';
                
                // 显示图片
                resultImage.src = data.imageUrl;
                resultImage.onload = function() {
                    imageWrapper.style.display = 'inline-block';
                    placeholder.style.display = 'none';
                    downloadButton.style.display = 'flex';
                    downloadButton.onclick = function() { downloadImage(data.imageUrl, promptInput.value); };
                };
                
                // 停止检查状态
                clearInterval(checkStatusInterval);
                
                // 恢复表单
                generateBtn.disabled = false;
                promptInput.disabled = false;
                loader.style.display = 'none';
                
            } else if (data.status === 'FAILED') {
                // 任务失败
                statusText.style.color = '#f44336';
                
                // 停止检查状态
                clearInterval(checkStatusInterval);
                
                // 恢复表单
                generateBtn.disabled = false;
                promptInput.disabled = false;
                loader.style.display = 'none';
                
            } else {
                // 任务仍在进行中
                statusText.style.color = '#2196F3';
            }
        } catch (error) {
            console.error('检查状态错误:', error);
            statusText.textContent = `检查任务状态出错: ${error.message}`;
            statusText.style.color = '#f44336';
            
            // 停止检查状态
            clearInterval(checkStatusInterval);
            
            // 恢复表单
            generateBtn.disabled = false;
            promptInput.disabled = false;
            loader.style.display = 'none';
        }
    }

    function downloadImage(imageUrl, promptText) {
        if (!imageUrl) return;
        
        // 创建一个临时链接元素
        const link = document.createElement('a');
        link.href = imageUrl;
        
        // 从URL中提取文件名，使用提示词和时间戳
        const timestamp = new Date().getTime();
        const filename = `${promptText}_${timestamp}.png`;
        link.download = filename;
        
        // 模拟点击下载
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}); 