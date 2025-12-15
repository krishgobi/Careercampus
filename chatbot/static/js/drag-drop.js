/**
 * Drag & Drop File Upload Component
 * Reusable JavaScript for file upload with drag & drop
 */

class DragDropUpload {
    constructor(dropZoneId, fileInputId, options = {}) {
        this.dropZone = document.getElementById(dropZoneId);
        this.fileInput = document.getElementById(fileInputId);
        this.files = [];

        this.options = {
            maxFiles: options.maxFiles || 10,
            maxSize: options.maxSize || 50 * 1024 * 1024, // 50MB default
            acceptedTypes: options.acceptedTypes || ['.pdf', '.docx', '.pptx'],
            multiple: options.multiple !== false,
            onFilesChanged: options.onFilesChanged || null,
            ...options
        };

        this.init();
    }

    init() {
        if (!this.dropZone || !this.fileInput) {
            console.error('Drop zone or file input not found');
            return;
        }

        // Set up event listeners
        this.dropZone.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag & drop events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => this.highlight(), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => this.unhighlight(), false);
        });

        this.dropZone.addEventListener('drop', (e) => this.handleDrop(e), false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight() {
        this.dropZone.classList.add('dragover');
    }

    unhighlight() {
        this.dropZone.classList.remove('dragover');
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        this.handleFiles(files);
    }

    handleFileSelect(e) {
        const files = e.target.files;
        this.handleFiles(files);
    }

    handleFiles(fileList) {
        const filesArray = Array.from(fileList);

        // Validate files
        const validFiles = filesArray.filter(file => this.validateFile(file));

        if (this.options.multiple) {
            // Add to existing files
            this.files = [...this.files, ...validFiles].slice(0, this.options.maxFiles);
        } else {
            // Replace with new file
            this.files = validFiles.slice(0, 1);
        }

        // Update file input
        this.updateFileInput();

        // Callback
        if (this.options.onFilesChanged) {
            this.options.onFilesChanged(this.files);
        }

        // Render file list
        this.renderFileList();
    }

    validateFile(file) {
        // Check file size
        if (file.size > this.options.maxSize) {
            alert(`File "${file.name}" is too large. Maximum size is ${this.formatBytes(this.options.maxSize)}`);
            return false;
        }

        // Check file type
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (this.options.acceptedTypes.length > 0 && !this.options.acceptedTypes.includes(extension)) {
            alert(`File "${file.name}" type not supported. Accepted types: ${this.options.acceptedTypes.join(', ')}`);
            return false;
        }

        return true;
    }

    updateFileInput() {
        // Create a new DataTransfer object
        const dt = new DataTransfer();
        this.files.forEach(file => dt.items.add(file));
        this.fileInput.files = dt.files;
    }

    renderFileList() {
        // Find or create file list container
        let fileListContainer = this.dropZone.querySelector('.file-list');
        if (!fileListContainer) {
            fileListContainer = document.createElement('div');
            fileListContainer.className = 'file-list';
            this.dropZone.appendChild(fileListContainer);
        }

        // Clear existing list
        fileListContainer.innerHTML = '';

        // Render each file
        this.files.forEach((file, index) => {
            const fileItem = this.createFileItem(file, index);
            fileListContainer.appendChild(fileItem);
        });
    }

    createFileItem(file, index) {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file-${this.getFileIcon(file)} file-icon"></i>
                <div class="file-details">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${this.formatBytes(file.size)}</div>
                </div>
            </div>
            <button type="button" class="file-remove" data-index="${index}">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add remove handler
        div.querySelector('.file-remove').addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeFile(index);
        });

        return div;
    }

    removeFile(index) {
        this.files.splice(index, 1);
        this.updateFileInput();
        this.renderFileList();

        if (this.options.onFilesChanged) {
            this.options.onFilesChanged(this.files);
        }
    }

    getFileIcon(file) {
        const extension = file.name.split('.').pop().toLowerCase();
        const iconMap = {
            'pdf': 'pdf',
            'doc': 'word',
            'docx': 'word',
            'ppt': 'powerpoint',
            'pptx': 'powerpoint',
            'xls': 'excel',
            'xlsx': 'excel',
            'txt': 'alt',
            'zip': 'archive'
        };
        return iconMap[extension] || 'alt';
    }

    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    getFiles() {
        return this.files;
    }

    clearFiles() {
        this.files = [];
        this.updateFileInput();
        this.renderFileList();
    }
}

// Export for use in other scripts
window.DragDropUpload = DragDropUpload;
