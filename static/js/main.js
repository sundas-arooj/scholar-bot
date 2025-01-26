let currentSessionId = null;
let isProcessing = false;

// Initialize the chat
document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners
    document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isProcessing) sendMessage();
    });

    // Set up file input change listener
    document.getElementById('fileInput').addEventListener('change', handleFileInputChange);
    
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
async function sendMessage() {
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
                session_id: currentSessionId
            })
        });

        const result = await response.json();
        currentSessionId = result.session_id;
        
        // Add bot response to chat
        addMessage(result.response, 'bot');
    } catch (error) {
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