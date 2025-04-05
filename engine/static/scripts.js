document.getElementById('send-button').addEventListener('click', async function() {
    // 获取输入框中的消息（即问题）
    var question = document.getElementById('message-input').value;

    if (!question) {
        alert("请输入您的问题！");
        return;
    }

    var requestBody = {
        question: question
    };

    // 添加用户消息到聊天窗口
    addMessage(question, 'user');

    try {
        const response = await fetch('{PYTHON_UPLOAD_URL_ADDRESS}/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        if (!response.body) {
            throw new Error('ReadableStream not available in this environment');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let partialMessage = '';

        // 创建一个新的AI消息元素
        let aiMessageElement = document.createElement('div');
        aiMessageElement.classList.add('chat-message');
        let aiTextElement = document.createElement('div');
        aiTextElement.classList.add('ai-message');
        aiMessageElement.appendChild(aiTextElement);
        document.getElementById('chat-window').appendChild(aiMessageElement);
        document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            partialMessage += chunk;

            // 假设每条消息以换行符分隔
            const messages = partialMessage.split('\n');

            // 如果partialMessage不以换行符结尾，则保留最后一部分作为下一个循环的开始
            partialMessage = messages.pop();

            for (const message of messages) {
                if (message.trim()) {  // 忽略空字符串
                    try {
                        const parsedMessage = JSON.parse(message);
                        console.log('Received:', parsedMessage.message.content);
                        // 截取message.content并更新UI
                        if (parsedMessage && parsedMessage.message.content) {
                            // 移除重复内容
                            let content = parsedMessage.message.content;
                            if (aiTextElement.textContent) {
                                content = content.replace(aiTextElement.textContent, '');
                            }
                            aiTextElement.textContent += content;
                            document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;
                        }
                    } catch (e) {
                        console.error('Failed to parse message:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Failed to send message', 'ai');
    }
});

function addMessage(text, sender) {
    var chatWindow = document.getElementById('chat-window');
    var messageElement = document.createElement('div');
    messageElement.classList.add('chat-message');
    var textElement = document.createElement('div');
    textElement.textContent = text;
    textElement.classList.add(sender + '-message');
    messageElement.appendChild(textElement);
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
