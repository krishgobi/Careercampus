// Upload page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const documentsList = document.getElementById('documentsList');
    
    let selectedFiles = [];
    
    // Drag and drop handlers
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });
    
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });
    
    function handleFiles(files) {
        // Filter supported files
        const supportedFiles = files.filter(file => {
            const ext = file.name.split('.').pop().toLowerCase();
            return ['pdf', 'docx', 'pptx'].includes(ext);
        });
        
        selectedFiles = [...selectedFiles, ...supportedFiles];
        displayFileList();
    }
    
    function displayFileList() {
        fileList.innerHTML = '';
        
        if (selectedFiles.length === 0) return;
        
        selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const ext = file.name.split('.').pop().toLowerCase();
            let icon = 'fa-file';
            if (ext === 'pdf') icon = 'fa-file-pdf';
            else if (ext === 'docx') icon = 'fa-file-word';
            else if (ext === 'pptx') icon = 'fa-file-powerpoint';
            
            fileItem.innerHTML = `
                <div class="file-item-info">
                    <i class="fas ${icon}"></i>
                    <span>${file.name}</span>
                </div>
                <button class="remove-btn" onclick="removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            fileList.appendChild(fileItem);
        });
        
        // Add upload button
        if (selectedFiles.length > 0) {
            const uploadBtn = document.createElement('button');
            uploadBtn.className = 'btn-primary';
            uploadBtn.innerHTML = '<i class="fas fa-upload"></i> Upload Files';
            uploadBtn.onclick = uploadFiles;
            fileList.appendChild(uploadBtn);
        }
    }
    
    window.removeFile = function(index) {
        selectedFiles.splice(index, 1);
        displayFileList();
    };
    
    async function uploadFiles() {
        if (selectedFiles.length === 0) return;
        
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        // Show progress
        uploadProgress.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = 'Uploading and processing files...';
        
        try {
            progressFill.style.width = '50%';
            
            const response = await fetch('/api/upload/', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                progressFill.style.width = '100%';
                progressText.textContent = 'Upload complete!';
                
                // Clear file list
                selectedFiles = [];
                fileList.innerHTML = '';
                
                // Add new documents to the grid
                data.documents.forEach(doc => {
                    addDocumentCard(doc);
                });
                
                // Reset progress after 2 seconds
                setTimeout(() => {
                    uploadProgress.style.display = 'none';
                }, 2000);
            } else {
                throw new Error(data.message || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            progressText.textContent = 'Upload failed: ' + error.message;
            progressFill.style.width = '0%';
        }
    }
    
    function addDocumentCard(doc) {
        // Remove empty state if exists
        const emptyState = documentsList.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
        
        const card = document.createElement('div');
        card.className = 'document-card';
        
        let icon = 'fa-file';
        if (doc.file_type === 'pdf') icon = 'fa-file-pdf';
        else if (doc.file_type === 'docx') icon = 'fa-file-word';
        else if (doc.file_type === 'pptx') icon = 'fa-file-powerpoint';
        
        card.innerHTML = `
            <div class="doc-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="doc-info">
                <h4>${doc.title}</h4>
                <p>${doc.uploaded_at}</p>
            </div>
        `;
        
        documentsList.appendChild(card);
    }
});
