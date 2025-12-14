// Chatbot page JavaScript
let currentChatId = null;
let currentDocumentId = null;

document.addEventListener('DOMContentLoaded', function () {
    loadChats();
});

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (!message) return;

    const documentSelect = document.getElementById('documentSelect');
    const documentId = documentSelect.value;

    if (!documentId) {
        alert('Please select a document first');
        return;
    }

    currentDocumentId = documentId;

    // Clear input
    messageInput.value = '';

    // Add user message to chat
    addMessage('user', message);

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                document_id: documentId,
                chat_id: currentChatId
            })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator();

        if (data.status === 'success') {
            // Update current chat ID
            currentChatId = data.chat_id;

            // Add assistant message
            addMessage('assistant', data.answer);

            // Reload chat list
            loadChats();
        } else {
            throw new Error(data.message || 'Failed to get response');
        }
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator();
        addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    }
}

function addMessage(role, content) {
    const chatMessages = document.getElementById('chatMessages');

    // Remove welcome message if exists
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

    messageDiv.innerHTML = `
        <div class="message-wrapper">
            <div class="message-avatar">
                ${avatar}
            </div>
            <div class="message-content">
                ${content}
            </div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant typing-message';
    typingDiv.innerHTML = `
        <div class="message-wrapper">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;

    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingMessage = document.querySelector('.typing-message');
    if (typingMessage) {
        typingMessage.remove();
    }
}

async function loadChats() {
    try {
        const response = await fetch('/api/chats/');
        const data = await response.json();

        const chatList = document.getElementById('chatList');

        if (data.chats.length === 0) {
            chatList.innerHTML = '<p class="empty-state">No chats yet. Start a conversation!</p>';
            return;
        }

        chatList.innerHTML = '';

        data.chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-item';
            chatItem.setAttribute('data-chat-id', chat.id);
            chatItem.onclick = () => loadChat(chat.id);

            chatItem.innerHTML = `
                <div class="chat-item-content">
                    <h4>${chat.name}</h4>
                    <p>${chat.updated_at}</p>
                </div>
                <div class="chat-actions">
                    <button onclick="event.stopPropagation(); renameChat(${chat.id})" title="Rename">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="event.stopPropagation(); exportChat(${chat.id})" title="Download PDF">
                        <i class="fas fa-download"></i>
                    </button>
                    <button onclick="event.stopPropagation(); deleteChat(${chat.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;

            chatList.appendChild(chatItem);
        });
    } catch (error) {
        console.error('Error loading chats:', error);
    }
}

async function loadChat(chatId) {
    try {
        const response = await fetch(`/api/chat/${chatId}/messages/`);
        const data = await response.json();

        currentChatId = chatId;

        // Update chat title
        document.getElementById('chatTitle').textContent = data.chat_name;

        // Clear messages
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';

        // Add all messages
        data.messages.forEach(msg => {
            addMessage(msg.role, msg.content);
        });

        // Highlight active chat
        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-chat-id="${chatId}"]`)?.classList.add('active');
    } catch (error) {
        console.error('Error loading chat:', error);
    }
}

function createNewChat() {
    currentChatId = null;

    // Clear messages
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <i class="fas fa-graduation-cap"></i>
            <h2>Welcome to Smart Campus Assistant!</h2>
            <p>Select a document from the dropdown above and start asking questions about your course materials.</p>
        </div>
    `;

    // Clear selection
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.remove('active');
    });

    // Reset title
    document.getElementById('chatTitle').textContent = 'AI Assistant';
}

async function renameChat(chatId) {
    const newName = prompt('Enter new chat name:');

    if (!newName) return;

    try {
        const response = await fetch('/api/chat/rename/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat_id: chatId,
                name: newName
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            loadChats();
            if (currentChatId === chatId) {
                document.getElementById('chatTitle').textContent = newName;
            }
        }
    } catch (error) {
        console.error('Error renaming chat:', error);
        alert('Failed to rename chat');
    }
}

function exportChat(chatId) {
    window.open(`/api/chat/${chatId}/export/`, '_blank');
}

async function deleteChat(chatId) {
    if (!confirm('Are you sure you want to delete this chat?')) return;

    try {
        const response = await fetch('/api/chat/delete/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat_id: chatId
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            if (currentChatId === chatId) {
                createNewChat();
            }
            loadChats();
        }
    } catch (error) {
        console.error('Error deleting chat:', error);
        alert('Failed to delete chat');
    }
}

function switchDocument() {
    const documentSelect = document.getElementById('documentSelect');
    const documentId = documentSelect.value;

    if (documentId) {
        currentDocumentId = documentId;
        // Start a new chat for the selected document
        createNewChat();
    }
}
