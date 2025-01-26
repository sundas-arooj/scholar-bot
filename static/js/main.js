let currentSessionId = null;
let isProcessing = false;

// Initialize the chat
document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners
    document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
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

    // Set up file input change listener
    document.getElementById('fileInput').addEventListener('change', handleFileInputChange);
    
    // Set up stream toggle listener
    document.getElementById('streamToggle').addEventListener('change', (e) => {
        console.log('Streaming mode:', e.target.checked ? 'enabled' : 'disabled');
    });
    
    // Initial button states
    updateUploadButtonState();
    updateSendButtonState();
});

// Handle file input change
function handleFileInputChange() {
    updateUploadButtonState();
}

// Update upload button state
function updateUploadButtonState() {
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.querySelector('.upload-btn');
    
    // Disable both file input and upload button during processing
    fileInput.disabled = isProcessing;
    uploadButton.disabled = !fileInput.files.length || isProcessing;
    
    // Update visual states
    uploadButton.style.opacity = uploadButton.disabled ? '0.5' : '1';
    if (isProcessing) {
        fileInput.style.opacity = '0.5';
        fileInput.style.cursor = 'not-allowed';
    } else {
        fileInput.style.opacity = '1';
        fileInput.style.cursor = 'pointer';
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
    const statusDiv = document.getElementById('uploadStatus');
    
    if (!fileInput.files.length) {
        showStatus('Please select a file first.', 'error');
        return;
    }

    isProcessing = true;
    updateUploadButtonState();

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        statusDiv.textContent = 'Uploading and processing file...';
        const response = await fetch('/embeddings/upload-file', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (response.ok) {
            showStatus(`Success! Processed ${result.chunk_count} chunks of text.`, 'success');
            // Add a system message to chat
            addMessage('Knowledge base updated successfully! You can now ask questions about the uploaded document.', 'bot');
            // Clear file input
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

    // Add user message to chat
    addMessage(message, 'user');
    
    // Change input placeholder and clear value
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

        // Create bot message div only when we start receiving response
        const messagesDiv = document.getElementById('chatMessages');
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'message bot-message';

        if (isStream) {
            // For streaming, get session ID from headers
            const sessionId = response.headers.get('X-Session-ID');
            if (sessionId) {
                currentSessionId = sessionId;
                console.log('Session ID from headers:', sessionId);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let botResponse = '';

            // Add bot message div to chat when we get first chunk
            let isFirstChunk = true;

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const text = decoder.decode(value);
                if (text.trim()) {  // Only process non-empty text
                    if (isFirstChunk) {
                        messagesDiv.appendChild(botMessageDiv);
                        isFirstChunk = false;
                    }
                    botResponse += text;
                    botMessageDiv.textContent = botResponse;
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
            }
        } else {
            // Handle non-streaming response
            const data = await response.json();
            
            // For non-streaming, get session ID from response body
            if (data.session_id) {
                currentSessionId = data.session_id;
                console.log('Session ID from response:', data.session_id);
            }

            // Only add bot message div if we have a response
            if (data.response) {
                messagesDiv.appendChild(botMessageDiv);
                botMessageDiv.textContent = data.response;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        }

    } catch (error) {
        console.error('Error:', error);
        // Show error message in a new bot message
        const messagesDiv = document.getElementById('chatMessages');
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'message bot-message';
        botMessageDiv.textContent = 'Error: Unable to get response from the bot.';
        messagesDiv.appendChild(botMessageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
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
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Show status messages
function showStatus(message, type) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
}

// Add input listener for send button state
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('userInput');
    userInput.addEventListener('input', updateSendButtonState);
}); 