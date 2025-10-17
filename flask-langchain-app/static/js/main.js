document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = uploadProgress.querySelector('div > div');
    const chatContainer = document.getElementById('chatContainer');
    const queryInput = document.getElementById('queryInput');
    const sendButton = document.getElementById('sendButton');
    const documentList = document.getElementById('documentList');

    // Initialize document list
    loadDocuments();

    // Drag and drop handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('drop-zone-active');
    }

    function unhighlight(e) {
        dropZone.classList.remove('drop-zone-active');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        uploadProgress.classList.remove('hidden');
        progressBar.style.width = '0%';

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                progressBar.style.width = '100%';
                setTimeout(() => {
                    uploadProgress.classList.add('hidden');
                    progressBar.style.width = '0%';
                }, 1000);
                loadDocuments();
                addMessage('System', 'Document uploaded successfully! You can now ask questions about it.', 'bot-message');
            }
        })
        .catch(error => {
            showError('Upload failed. Please try again.');
        });
    }

    function showError(message) {
        addMessage('System', message, 'bot-message');
        uploadProgress.classList.add('hidden');
        progressBar.style.width = '0%';
    }

    // Chat functionality
    sendButton.addEventListener('click', sendMessage);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const query = queryInput.value.trim();
        if (!query) return;

        addMessage('You', query, 'user-message');
        queryInput.value = '';

        // Show loading message
        const loadingId = 'loading-' + Date.now();
        addMessage('Bot', '<span class="loading-dots">Thinking</span>', 'bot-message', loadingId);

        fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading message
            const loadingMessage = document.getElementById(loadingId);
            if (loadingMessage) {
                loadingMessage.remove();
            }

            if (data.error) {
                addMessage('Bot', data.error, 'bot-message');
            } else {
                const response = data.results[0] || 'No relevant information found.';
                addMessage('Bot', response, 'bot-message');
            }
        })
        .catch(error => {
            const loadingMessage = document.getElementById(loadingId);
            if (loadingMessage) {
                loadingMessage.remove();
            }
            addMessage('Bot', 'Sorry, there was an error processing your request.', 'bot-message');
        });
    }

    function addMessage(sender, message, className, id = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${className}`;
        if (id) messageDiv.id = id;
        
        const senderSpan = document.createElement('span');
        senderSpan.className = 'font-semibold text-gray-700';
        senderSpan.textContent = sender + ': ';
        
        const contentSpan = document.createElement('span');
        contentSpan.innerHTML = message;
        
        messageDiv.appendChild(senderSpan);
        messageDiv.appendChild(contentSpan);
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function loadDocuments() {
        fetch('/documents')
            .then(response => response.json())
            .then(data => {
                documentList.innerHTML = '';
                data.documents.forEach(doc => {
                    const card = createDocumentCard(doc);
                    documentList.appendChild(card);
                });
            })
            .catch(error => {
                console.error('Error loading documents:', error);
            });
    }

    function createDocumentCard(doc) {
        const card = document.createElement('div');
        card.className = 'document-card bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow';
        
        const fileName = doc.source.split('_').slice(2).join('_');
        const uploadDate = new Date(doc.source.split('_')[0] + doc.source.split('_')[1]).toLocaleDateString();
        
        card.innerHTML = `
            <div class="flex items-center space-x-3">
                <svg class="h-8 w-8 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <div>
                    <h3 class="font-semibold text-gray-800">${fileName}</h3>
                    <p class="text-sm text-gray-500">Uploaded on ${uploadDate}</p>
                </div>
            </div>
        `;
        
        return card;
    }
}); 