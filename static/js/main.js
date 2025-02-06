let currentSessionId = null;
let isProcessing = false;

// Initialize the chat
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
    document.getElementById('fileInput').addEventListener('change', () => {
        const fileInput = document.getElementById('fileInput');
        const uploadButton = document.querySelector('button[type="submit"]');
        
        // Enable upload button if file is selected
        uploadButton.disabled = !fileInput.files.length;
        
        // Update the file name display
        const fileName = fileInput.files[0]?.name || 'No file chosen';
        document.getElementById('fileLabel').textContent = fileName;
    });

    document.getElementById('sendButton').addEventListener('click', () => {
        const isStream = document.getElementById('streamToggle').checked;
        sendMessage(isStream);
    });
    
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isProcessing) {
            const isStream = document.getElementById('streamToggle').checked;
            sendMessage(isStream);
        }
    });

    // Set up stream toggle listener
    document.getElementById('streamToggle').addEventListener('change', (e) => {
        console.log('Streaming mode:', e.target.checked ? 'enabled' : 'disabled');
    });
    
    // Initial button states
    updateUploadButtonState();
    updateSendButtonState();
});

// Update upload button state
function updateUploadButtonState() {
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.querySelector('button[type="submit"]');
    
    // Disable both file input and upload button during processing
    fileInput.disabled = isProcessing;
    uploadButton.disabled = !fileInput.files.length || isProcessing;
    
    // Update visual states
    if (isProcessing) {
        uploadButton.classList.add('opacity-50', 'cursor-not-allowed');
        fileInput.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        uploadButton.classList.remove('opacity-50', 'cursor-not-allowed');
        fileInput.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

// Update send button state
function updateSendButtonState() {
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    sendButton.disabled = !userInput.value.trim() || isProcessing;
    sendButton.style.opacity = sendButton.disabled ? '0.5' : '1';
}

// Handle file upload
async function handleFileUpload(e) {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    
    if (!fileInput.files.length) {
        showStatus('Please select a file first.', 'error');
        return;
    }

    isProcessing = true;
    updateUploadButtonState();
    showStatus('Uploading and processing file...');

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/embeddings/upload-file', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (response.ok) {
            showStatus(`Success! Processed ${result.chunk_count} chunks of text.`, 'success');
            addMessage('Knowledge base updated successfully! You can now ask questions about the uploaded document.', 'bot');
            fileInput.value = '';
        } else {
            showStatus(`Error: ${result.detail}`, 'error');
        }
    } catch (error) {
        showStatus('Error uploading file: ' + error.message, 'error');
    } finally {
        isProcessing = false;
        updateUploadButtonState();
    }
}

// Send a message to the chat
async function sendMessage(isStream = true) {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message || isProcessing) return;

    isProcessing = true;
    updateSendButtonState();

    // Add user message
    addMessage(message, 'user');
    
    userInput.value = '';
    userInput.placeholder = 'Processing...';
    userInput.disabled = true;

    try {
        const response = await fetch('/chat/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId,
                is_stream: isStream
            })
        });

        const sessionId = response.headers.get('X-Session-ID');
        if (sessionId) {
            currentSessionId = sessionId;
            console.log('Session ID:', sessionId);
        }

        const messagesDiv = document.getElementById('chatMessages');
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'mb-4 animate-fade-in';
        botMessageDiv.innerHTML = `
            <div class="flex justify-start">
                <div class="bg-[#2a2a3f] text-gray-200 max-w-[80%] px-5 py-3 
                           rounded-[18px] rounded-bl-none shadow-md">
                    <div class="bot-response"></div>
                </div>
            </div>
        `;
        
        const botTextDiv = botMessageDiv.querySelector('.bot-response');
        let isFirstChunk = true;

        if (isStream) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let botResponse = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const text = decoder.decode(value);
                if (text.trim()) {
                    if (isFirstChunk) {
                        messagesDiv.appendChild(botMessageDiv);
                        isFirstChunk = false;
                    }
                    botResponse += text;
                    botTextDiv.textContent = botResponse;
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
            }
        } else {
            const data = await response.json();
            if (data.session_id) {
                currentSessionId = data.session_id;
                console.log('Session ID from response:', data.session_id);
            }
            
            if (data.response?.trim()) {
                botTextDiv.textContent = data.response;
                messagesDiv.appendChild(botMessageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Error: Unable to get response from the bot.', 'bot');
    } finally {
        isProcessing = false;
        userInput.disabled = false;
        userInput.placeholder = 'Type your message...';
        updateSendButtonState();
    }
}

// Add a message to the chat interface
function addMessage(text, sender) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="flex justify-end">
                <div class="bg-[#7289da] text-white max-w-[80%] px-5 py-3 
                           rounded-[18px] rounded-br-none shadow-md">
                    ${text}
                </div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="flex justify-start">
                <div class="bg-[#2a2a3f] text-gray-200 max-w-[80%] px-5 py-3 
                           rounded-[18px] rounded-bl-none shadow-md">
                    ${text}
                </div>
            </div>
        `;
    }
    
    messageDiv.className = 'mb-4 animate-fade-in';
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.textContent = message;
    statusDiv.classList.remove('hidden');
    
    if (type === 'success') {
        statusDiv.className = 'mt-4 p-3 rounded-lg bg-[#1e4620] text-[#4ade80] animate-fade-in';
    } else if (type === 'error') {
        statusDiv.className = 'mt-4 p-3 rounded-lg bg-[#441a1d] text-[#f87171] animate-fade-in';
    } else {
        statusDiv.className = 'mt-4 p-3 rounded-lg bg-[#1e1e2e] text-gray-300 animate-fade-in';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('userInput');
    userInput.addEventListener('input', updateSendButtonState);
});

document.getElementById('fileInput').addEventListener('change', function() {
    const label = document.getElementById('fileLabel');
    label.textContent = this.files[0]?.name || 'Choose File';
}); 