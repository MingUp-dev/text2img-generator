document.addEventListener('DOMContentLoaded', function() {
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const loader = document.getElementById('loading-indicator');
    const statusText = document.getElementById('status-text');
    const resultImage = document.getElementById('result-image');
    const downloadButton = document.getElementById('download-button');
    const imageWrapper = document.getElementById('image-wrapper');
    const placeholder = document.getElementById('placeholder');

    let taskId = null;
    let pollingInterval = null;
    let isGenerating = false;
    
    // 获取当前网站的基础URL
    const baseUrl = window.location.origin;
    
    // 生成图片按钮点击事件
    generateBtn.addEventListener('click', function() {
        if (isGenerating) return;

        const prompt = promptInput.value.trim();
        if (!prompt) {
            statusText.textContent = "请输入提示词";
            statusText.style.color = "#f44336";
            return;
        }

        startGeneration(prompt);
    });
    
    // 开始生成图片
    function startGeneration(prompt) {
        isGenerating = true;
        generateBtn.disabled = true;
        loader.style.display = 'inline-block';
        statusText.textContent = "准备生成图片...";
        statusText.style.color = "#2196F3";
        
        // 清除之前的图片结果
        imageWrapper.style.display = 'none';
        placeholder.style.display = 'flex';
        downloadButton.style.display = 'none';
        
        // 添加错误处理和调试信息
        console.log("发送生成请求到:", baseUrl + '/api/generate');
        
        // 调用API开始生成
        fetch(baseUrl + '/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
            body: JSON.stringify({ prompt: prompt })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                taskId = data.taskId;
                statusText.textContent = "任务已提交，正在生成中...";
                // 开始轮询检查状态
                startPolling();
            } else {
                handleError(data.message || "生成请求失败");
            }
        })
        .catch(error => {
            console.error("API请求错误:", error);
            handleError("网络请求错误: " + error.message);
        });
    }
    
    // 轮询检查生成状态
    function startPolling() {
        if (pollingInterval) clearInterval(pollingInterval);
        
        let attempts = 0;
        const maxAttempts = 30;
        
        pollingInterval = setInterval(() => {
            attempts++;
            statusText.textContent = `任务处理中...(${attempts}/${maxAttempts})`;
            
            console.log("发送状态查询请求到:", baseUrl + `/api/status?taskId=${taskId}`);
            
            fetch(baseUrl + `/api/status?taskId=${taskId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP错误: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'SUCCEEDED') {
                        clearInterval(pollingInterval);
                        handleSuccess(data.imageUrl);
                    } else if (data.status === 'FAILED') {
                        clearInterval(pollingInterval);
                        handleError(data.message || "图片生成失败");
                    } else if (attempts >= maxAttempts) {
                        clearInterval(pollingInterval);
                        handleError("生成超时，请重试");
                    }
                })
                .catch(error => {
                    console.error("状态查询错误:", error);
                    clearInterval(pollingInterval);
                    handleError("获取状态失败: " + error.message);
                });
        }, 2000); // 每2秒检查一次
    }
    
    // 处理生成成功
    function handleSuccess(imageUrl) {
        loader.style.display = 'none';
        statusText.textContent = "图片生成成功！";
        statusText.style.color = "#4CAF50";
                
        resultImage.src = imageUrl;
        resultImage.onload = function() {
            imageWrapper.style.display = 'inline-block';
            placeholder.style.display = 'none';
            downloadButton.style.display = 'flex';
            downloadButton.onclick = function() { 
                downloadImage(imageUrl, promptInput.value); 
            };
        };
                
        // 重置生成状态
        isGenerating = false;
        generateBtn.disabled = false;
    }
    
    // 处理错误
    function handleError(message) {
        loader.style.display = 'none';
        statusText.textContent = message;
        statusText.style.color = "#f44336";
            
        // 重置生成状态
        isGenerating = false;
        generateBtn.disabled = false;
    }

    // 下载图片
    function downloadImage(imageUrl, promptText) {
        if (!imageUrl) return;
        
        const filename = `${promptText}_${new Date().getTime()}.jpg`;
        
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}); 