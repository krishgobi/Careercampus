// chatbot.js - Enhanced with Voice, TTS, and Model Cards

let currentChatId = null;
let currentDocumentId = null;
let currentModel = 'gemini-2.5-flash';
let currentModelName = 'Gemini 2.5 Flash';
let availableModels = [];
let voiceAccent = 'en-US';
let recognition = null;
let isRecording = false;
let isSpeaking = false;
let interimTranscript = '';

document.addEventListener('DOMContentLoaded', function () {
    loadChats();
    loadModels();
    setupVoiceInput();
    setupDropdownClose();
    setupTTSEventDelegation();
});

// Setup event delegation for TTS read buttons
function setupTTSEventDelegation() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.addEventListener('click', function (e) {
            const btn = e.target.closest('.msg-audio-btn');
            if (btn && btn.dataset.ttsText) {
                const text = decodeURIComponent(btn.dataset.ttsText);
                toggleSpeech(text, btn);
            }
        });
    }
}

// ===== 1. Voice Input (Speech Recognition) =====
function setupVoiceInput() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;  // Keep listening for continuous speech
        recognition.interimResults = true;  // Show words as they are spoken
        recognition.lang = 'en-US';

        recognition.onstart = function () {
            isRecording = true;
            interimTranscript = '';
            document.getElementById('voiceBtn').classList.add('recording');
            document.getElementById('messageInput').placeholder = 'Listening... (click again to stop)';
        };

        recognition.onend = function () {
            isRecording = false;
            document.getElementById('voiceBtn').classList.remove('recording');
            document.getElementById('messageInput').placeholder = 'Type your question or use voice input...';
        };

        recognition.onresult = function (event) {
            const input = document.getElementById('messageInput');
            let finalTranscript = '';
            interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }

            // Get the base text (what was there before interim results)
            const baseText = input.dataset.baseText || input.value;

            if (finalTranscript) {
                // Append final result and update base text
                input.value = baseText + finalTranscript;
                input.dataset.baseText = input.value;
            } else {
                // Show interim result (will be replaced on next result)
                input.value = baseText + interimTranscript;
            }

            autoResize(input);
        };

        recognition.onerror = function (event) {
            console.error('Speech recognition error', event.error);
            isRecording = false;
            document.getElementById('voiceBtn').classList.remove('recording');
            // Auto-restart on no-speech error if still recording
            if (event.error === 'no-speech' && isRecording) {
                setTimeout(() => recognition.start(), 100);
            }
        };
    } else {
        const btn = document.getElementById('voiceBtn');
        if (btn) btn.style.display = 'none';
        console.warn('Web Speech API not supported in this browser');
    }
}

function toggleVoiceInput() {
    if (!recognition) return;
    const input = document.getElementById('messageInput');

    if (isRecording) {
        recognition.stop();
        // Clear base text tracking
        delete input.dataset.baseText;
    } else {
        // Store current value as base text
        input.dataset.baseText = input.value;
        recognition.start();
    }
}

function changeVoiceAccent() {
    voiceAccent = document.getElementById('accentSelect').value;
    if (recognition) recognition.lang = voiceAccent;
}

// ===== 2. Text-to-Speech (TTS) with Stop Toggle =====
function toggleSpeech(text, btn) {
    if (!('speechSynthesis' in window)) return;

    // If currently speaking, stop it
    if (isSpeaking) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
        updateReadButtonUI(btn, false);
        return;
    }

    // Start speaking
    const utterance = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();

    let selectedVoice = voices.find(v => v.lang === voiceAccent);
    if (!selectedVoice && voiceAccent.includes('en')) {
        selectedVoice = voices.find(v => v.lang.includes('en'));
    }
    if (selectedVoice) utterance.voice = selectedVoice;

    utterance.onstart = function () {
        isSpeaking = true;
        updateReadButtonUI(btn, true);
    };

    utterance.onend = function () {
        isSpeaking = false;
        updateReadButtonUI(btn, false);
    };

    utterance.onerror = function () {
        isSpeaking = false;
        updateReadButtonUI(btn, false);
    };

    window.speechSynthesis.speak(utterance);
}

function updateReadButtonUI(btn, speaking) {
    if (!btn) return;
    if (speaking) {
        btn.innerHTML = '<i class="fas fa-stop"></i> Stop';
        btn.classList.add('speaking');
    } else {
        btn.innerHTML = '<i class="fas fa-volume-up"></i> Read';
        btn.classList.remove('speaking');
    }
}

// Legacy function for backward compatibility
function speakResponse(text) {
    toggleSpeech(text, null);
}

// ===== 3. Gemini-Style Inline Model Selector =====
let modelDropdownOpen = false;

async function loadModels() {
    try {
        const response = await fetch('/api/models/');
        const data = await response.json();
        availableModels = data.models;

        renderModelDropdown();
        updateCurrentModelDisplay();

    } catch (error) {
        console.error('Error loading models:', error);
    }
}

function renderModelDropdown() {
    const list = document.getElementById('modelDropdownList');
    if (!list) return;

    list.innerHTML = availableModels.map(model => `
        <div class="model-option ${model.model_id === currentModel ? 'selected' : ''}" 
             onclick="selectModelFromDropdown('${model.model_id}', '${model.name.replace(/'/g, "\\'")}')">
            <div class="model-option-header">
                <span class="model-option-name">${model.name}</span>
                ${model.model_id === currentModel ? '<i class="fas fa-check"></i>' : ''}
            </div>
            <p class="model-option-desc">${model.description}</p>
        </div>
    `).join('');
}

function selectModelFromDropdown(modelId, modelName) {
    currentModel = modelId;
    currentModelName = modelName;

    updateCurrentModelDisplay();
    renderModelDropdown();
    closeModelDropdown();
}

function updateCurrentModelDisplay() {
    const display = document.getElementById('currentModelDisplay');
    if (!display) return;

    // Show short name for display
    const shortName = currentModelName.includes('Flash') ? 'Fast' :
        currentModelName.includes('Pro') ? 'Pro' :
            currentModelName.split(' ')[0];
    display.textContent = shortName;
}

function toggleModelDropdown() {
    const dropdown = document.getElementById('modelDropdown');
    if (!dropdown) return;

    modelDropdownOpen = !modelDropdownOpen;
    dropdown.classList.toggle('open', modelDropdownOpen);
}

function closeModelDropdown() {
    const dropdown = document.getElementById('modelDropdown');
    if (dropdown) {
        dropdown.classList.remove('open');
        modelDropdownOpen = false;
    }
}

function setupDropdownClose() {
    document.addEventListener('click', function (e) {
        const selector = document.querySelector('.model-selector-inline');
        if (selector && !selector.contains(e.target)) {
            closeModelDropdown();
        }
    });
}

// Legacy support
function selectModel(modelId, modelName) {
    selectModelFromDropdown(modelId, modelName);
}

function updateModelDropdown() {
    // Legacy - not needed with new inline dropdown
}

// ===== 4. Messaging Logic =====
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    if (!message) return;

    if (!document.getElementById('documentSelect').value) {
        alert('Please select a document first.');
        return;
    }
    currentDocumentId = document.getElementById('documentSelect').value;

    messageInput.value = '';
    autoResize(messageInput);

    addMessage('user', message);

    // Show typing
    showTyping();

    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                document_id: currentDocumentId,
                chat_id: currentChatId,
                model_id: currentModel
            })
        });
        const data = await response.json();

        hideTyping();

        if (data.status === 'success') {
            currentChatId = data.chat_id;
            addMessage('assistant', data.answer);
            loadChats(); // Refresh history
        } else {
            addMessage('assistant', 'Error: ' + data.message);
        }
    } catch (e) {
        hideTyping();
        addMessage('assistant', 'Network error occurred.');
    }
}

function addMessage(role, content) {
    const container = document.getElementById('chatMessages');
    const welcome = container.querySelector('.welcome-screen');
    if (welcome) welcome.style.display = 'none';

    const div = document.createElement('div');
    div.className = `message ${role}`;

    // Markdown parsing (simplified)
    let formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');

    let audioBtnHTML = '';
    if (role === 'assistant') {
        // Use data attribute to safely store content for TTS (avoids issues with quotes, newlines, special chars)
        audioBtnHTML = `
            <button class="msg-audio-btn" data-tts-text="${encodeURIComponent(content.substring(0, 1000))}">
                <i class="fas fa-volume-up"></i> Read
            </button>
        `;
    }

    div.innerHTML = `
        <div class="message-wrapper">
            <div class="message-avatar">
                <i class="fas ${role === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-bubble">
                ${formattedContent}
                ${audioBtnHTML}
            </div>
        </div>
    `;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// ===== 5. Chat History =====
async function loadChats() {
    try {
        const res = await fetch('/api/chats/');
        const data = await res.json();
        const list = document.getElementById('chatList');

        if (data.chats && data.chats.length) {
            list.innerHTML = data.chats.map(chat => `
                <div class="chat-item ${chat.id === currentChatId ? 'active' : ''}" onclick="loadChat(${chat.id})">
                    <div class="chat-item-content">
                        <h4>${chat.name}</h4>
                        <p>${chat.updated_at}</p>
                    </div>
                    <div class="chat-actions">
                        <button onclick="event.stopPropagation(); renameChat(${chat.id})" title="Rename"><i class="fas fa-pen"></i></button>
                        <button onclick="event.stopPropagation(); downloadChatAsPDF(${chat.id})" title="Download PDF"><i class="fas fa-file-pdf"></i></button>
                        <button onclick="event.stopPropagation(); deleteChat(${chat.id})" title="Delete"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            `).join('');
        } else {
            list.innerHTML = '<div class="empty-history"><p>No chats</p></div>';
        }
    } catch (error) {
        console.error('Error loading chats:', error);
    }
}

async function loadChat(chatId) {
    currentChatId = chatId;
    const res = await fetch(`/api/chat/${chatId}/messages/`);
    const data = await res.json();

    // Clear current view
    document.getElementById('chatMessages').innerHTML = '';

    // Load messages
    if (data.messages && data.messages.length > 0) {
        data.messages.forEach(msg => {
            addMessage(msg.role, msg.content);
        });
    }

    // Update active state in sidebar
    loadChats();
}

function createNewChat() {
    currentChatId = null;
    document.getElementById('chatMessages').innerHTML = `
        <div class="welcome-screen">
            <div class="welcome-icon"><i class="fas fa-graduation-cap"></i></div>
            <h2>Welcome to <span class="brand-text">கற்றல் AI</span></h2>
            <p>Select a document and an AI model to begin your learning journey.</p>
        </div>
    `;
    loadChats();
}

// Helpers
function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

function showTyping() {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.id = 'typingIndicator';
    div.className = 'message assistant';
    div.innerHTML = `
       <div class="message-wrapper">
           <div class="message-avatar"><i class="fas fa-robot"></i></div>
           <div class="message-bubble">
               <div class="typing-indicator"><span></span><span></span><span></span></div>
           </div>
       </div>
   `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}

function switchDocument() {
    // handled in sendMessage primarily, but could clear chat or alert user
    createNewChat();
}

// ===== 6. Chat History Actions (Rename, Download PDF, Delete) =====
async function renameChat(chatId) {
    const newName = prompt('Enter new chat name:');
    if (!newName || !newName.trim()) return;

    try {
        const response = await fetch('/api/chat/rename/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId, name: newName.trim() })
        });
        const data = await response.json();
        if (data.status === 'success') {
            loadChats();
        } else {
            alert('Failed to rename chat: ' + data.message);
        }
    } catch (error) {
        console.error('Error renaming chat:', error);
        alert('Error renaming chat');
    }
}

async function deleteChat(chatId) {
    if (!confirm('Are you sure you want to delete this chat?')) return;

    try {
        const response = await fetch('/api/chat/delete/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId })
        });
        const data = await response.json();
        if (data.status === 'success') {
            if (currentChatId === chatId) {
                createNewChat();
            }
            loadChats();
        } else {
            alert('Failed to delete chat: ' + data.message);
        }
    } catch (error) {
        console.error('Error deleting chat:', error);
        alert('Error deleting chat');
    }
}

async function downloadChatAsPDF(chatId) {
    try {
        const res = await fetch(`/api/chat/${chatId}/messages/`);
        const data = await res.json();

        if (!data.messages || data.messages.length === 0) {
            alert('No messages to download');
            return;
        }

        // Create simple text content for PDF
        let content = 'Kattral AI - Chat Transcript\n';
        content += '================================\n\n';

        data.messages.forEach(msg => {
            const role = msg.role === 'user' ? 'You' : 'AI';
            content += `${role}:\n${msg.content}\n\n`;
        });

        // Download as text file (PDF requires library)
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_${chatId}_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading chat:', error);
        alert('Error downloading chat');
    }
}

// ===== 7. Document Upload from Chatbot with Drag & Drop =====
let chatUploadInstance = null;

function triggerFileUpload() {
    // Open upload modal
    document.getElementById('uploadModal').classList.add('active');

    // Initialize drag & drop if not already done
    if (!chatUploadInstance) {
        chatUploadInstance = new DragDropUpload('chatDropZone', 'chatFileInput', {
            multiple: false,
            acceptedTypes: ['.pdf', '.docx', '.pptx'],
            maxSize: 50 * 1024 * 1024
        });
    }
}

function closeUploadModal() {
    document.getElementById('uploadModal').classList.remove('active');
    if (chatUploadInstance) {
        chatUploadInstance.clearFiles();
    }
}

async function uploadChatDocument() {
    if (!chatUploadInstance || chatUploadInstance.getFiles().length === 0) {
        alert('Please select a file to upload');
        return;
    }

    const files = chatUploadInstance.getFiles();
    const formData = new FormData();

    for (let file of files) {
        formData.append('files', file);
    }

    try {
        // Show loading state
        const uploadBtn = document.querySelector('#uploadModal .btn-primary');
        if (uploadBtn) {
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
            uploadBtn.disabled = true;
        }

        const response = await fetch('/api/upload/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.status === 'success') {
            // Add new documents to the dropdown
            const select = document.getElementById('documentSelect');
            if (select && data.documents) {
                data.documents.forEach(doc => {
                    const option = document.createElement('option');
                    option.value = doc.id;
                    option.textContent = doc.title;
                    select.appendChild(option);
                    // Auto-select the newly uploaded document
                    select.value = doc.id;
                });
            }

            closeUploadModal();
            alert('Document uploaded successfully!');
        } else {
            alert('Upload failed: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error uploading file');
    } finally {
        // Reset button state
        const uploadBtn = document.querySelector('#uploadModal .btn-primary');
        if (uploadBtn) {
            uploadBtn.innerHTML = 'Upload';
            uploadBtn.disabled = false;
        }
    }
}

// Legacy function for backward compatibility
async function handleChatFileUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    try {
        const response = await fetch('/api/upload/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.status === 'success') {
            const select = document.getElementById('documentSelect');
            if (select && data.documents) {
                data.documents.forEach(doc => {
                    const option = document.createElement('option');
                    option.value = doc.id;
                    option.textContent = doc.title;
                    select.appendChild(option);
                    select.value = doc.id;
                });
            }
            alert('Document uploaded successfully!');
        } else {
            alert('Upload failed: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error uploading file');
    } finally {
        event.target.value = '';
    }
}

// ===== 8. Edit Current Chat Title =====
function editCurrentChatTitle() {
    if (!currentChatId) {
        alert('Please start a conversation first');
        return;
    }
    renameChat(currentChatId);
}
