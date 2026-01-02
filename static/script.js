const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// Voice recording
voiceBtn.addEventListener('click', async () => {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Try to use audio/webm;codecs=opus or fallback to default
            const options = { mimeType: 'audio/webm;codecs=opus' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'audio/webm';
            }
            
            mediaRecorder = new MediaRecorder(stream, options);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await sendVoiceMessage(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            mediaRecorder.start();
            isRecording = true;
            voiceBtn.classList.add('recording');
            userInput.placeholder = 'Recording...';
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access microphone. Please check permissions.');
        }
    } else {
        mediaRecorder.stop();
        isRecording = false;
        voiceBtn.classList.remove('recording');
        userInput.placeholder = 'Message Carlo...';
    }
});

async function sendVoiceMessage(audioBlob) {
    // Add user voice message indicator
    addMessage('🎤 Voice message', 'user');
    
    // Disable input
    sendBtn.disabled = true;
    userInput.disabled = true;
    voiceBtn.disabled = true;
    
    // Add typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        
        const response = await fetch('/api/voice/chat', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        removeTypingIndicator(typingId);
        
        if (data.success) {
            // Show transcription
            addMessage(`"${data.transcription}"`, 'user');
            
            // Show Carlo's response
            addMessage(data.response.message, 'assistant', data.response);
            
            // Play audio response
            const audioResponse = await fetch('/api/voice/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: data.response.message })
            });
            
            const responseAudioBlob = await audioResponse.blob();
            const audioUrl = URL.createObjectURL(responseAudioBlob);
            const audio = new Audio(audioUrl);
            audio.play();
            
        } else {
            addMessage(`Sorry, I couldn't process that: ${data.error}`, 'assistant');
        }
        
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage(`Sorry, I encountered an error: ${error.message}`, 'assistant');
    } finally {
        sendBtn.disabled = false;
        userInput.disabled = false;
        voiceBtn.disabled = false;
        userInput.focus();
    }
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const message = userInput.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    userInput.value = '';

    // Disable input
    sendBtn.disabled = true;
    userInput.disabled = true;

    // Add typing indicator
    const typingId = addTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingId);

        if (data.success) {
            addMessage(data.response.message, 'assistant', data.response);
        } else {
            addMessage(`Sorry, I encountered an error: ${data.error}`, 'assistant');
        }

    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage(`Sorry, I encountered an error: ${error.message}`, 'assistant');
    } finally {
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }
});

function addMessage(content, type, data = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    // Add avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    
    if (type === 'user') {
        avatarDiv.textContent = 'You';
    } else {
        avatarDiv.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="8" fill="url(#gradient3)"/>
                <path d="M16 8L22 12V20L16 24L10 20V12L16 8Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>
                <defs>
                    <linearGradient id="gradient3" x1="0" y1="0" x2="32" y2="32">
                        <stop offset="0%" stop-color="#667eea"/>
                        <stop offset="100%" stop-color="#764ba2"/>
                    </linearGradient>
                </defs>
            </svg>
        `;
    }

    // Add content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (type === 'assistant') {
        let html = `<p>${content}</p>`;

        // Show task results if available
        if (data.tasks && data.tasks.length > 0) {
            data.tasks.forEach(task => {
                if (task.message && task.message !== content) {
                    html += `<p style="color: var(--text-secondary); font-size: 14px; margin-top: 8px;">${task.message}</p>`;
                }
            });
        }

        contentDiv.innerHTML = html;
    } else {
        contentDiv.textContent = content;
    }

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = id;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="url(#gradient4)"/>
            <path d="M16 8L22 12V20L16 24L10 20V12L16 8Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>
            <defs>
                <linearGradient id="gradient4" x1="0" y1="0" x2="32" y2="32">
                    <stop offset="0%" stop-color="#667eea"/>
                    <stop offset="100%" stop-color="#764ba2"/>
                </linearGradient>
            </defs>
        </svg>
    `;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

// Auto-focus input on load
userInput.focus();
