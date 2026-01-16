/**
 * PreDrive File Picker for PreOffice Online
 * Allows browsing and selecting files from PreDrive
 */

class PreDrivePicker {
  constructor(options = {}) {
    this.options = {
      apiUrl: options.apiUrl || '/api',
      onSelect: options.onSelect || (() => {}),
      onCancel: options.onCancel || (() => {}),
      mode: options.mode || 'open', // 'open' or 'save'
      title: options.title || 'Select a file',
      ...options
    };

    this.currentFolderId = null;
    this.path = [{ id: null, name: 'My Files' }];
    this.selectedFile = null;
    this.accessToken = null;
    this.modal = null;
  }

  /**
   * Set access token for API requests
   */
  setAccessToken(token) {
    this.accessToken = token;
  }

  /**
   * Open the file picker modal
   */
  async open() {
    this.createModal();
    await this.loadFolder(null);
    this.modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }

  /**
   * Close the file picker modal
   */
  close() {
    if (this.modal) {
      this.modal.style.display = 'none';
      document.body.style.overflow = '';
    }
  }

  /**
   * Create the modal HTML
   */
  createModal() {
    if (this.modal) {
      document.body.removeChild(this.modal);
    }

    this.modal = document.createElement('div');
    this.modal.className = 'predrive-picker-overlay';
    this.modal.innerHTML = `
      <div class="predrive-picker-modal">
        <div class="predrive-picker-header">
          <h2 class="predrive-picker-title">${this.escapeHtml(this.options.title)}</h2>
          <button class="predrive-picker-close" title="Close">&times;</button>
        </div>

        <div class="predrive-picker-toolbar">
          <div class="predrive-picker-breadcrumb" id="predrive-breadcrumb"></div>
          <div class="predrive-picker-search">
            <input type="text" placeholder="Search files..." id="predrive-search-input">
          </div>
        </div>

        <div class="predrive-picker-content" id="predrive-content">
          <div class="predrive-picker-loading">Loading...</div>
        </div>

        <div class="predrive-picker-footer">
          <div class="predrive-picker-selected" id="predrive-selected">No file selected</div>
          <div class="predrive-picker-actions">
            <button class="predrive-picker-btn predrive-picker-btn-secondary" id="predrive-cancel">Cancel</button>
            <button class="predrive-picker-btn predrive-picker-btn-primary" id="predrive-select" disabled>
              ${this.options.mode === 'save' ? 'Save Here' : 'Open'}
            </button>
          </div>
        </div>
      </div>
    `;

    // Add styles
    this.addStyles();

    // Add event listeners
    this.modal.querySelector('.predrive-picker-close').addEventListener('click', () => {
      this.close();
      this.options.onCancel();
    });

    this.modal.querySelector('#predrive-cancel').addEventListener('click', () => {
      this.close();
      this.options.onCancel();
    });

    this.modal.querySelector('#predrive-select').addEventListener('click', () => {
      if (this.selectedFile) {
        this.close();
        this.options.onSelect(this.selectedFile);
      }
    });

    const searchInput = this.modal.querySelector('#predrive-search-input');
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        const query = e.target.value.trim();
        if (query.length >= 2) {
          this.search(query);
        } else if (query.length === 0) {
          this.loadFolder(this.currentFolderId);
        }
      }, 300);
    });

    document.body.appendChild(this.modal);
  }

  /**
   * Add CSS styles
   */
  addStyles() {
    if (document.getElementById('predrive-picker-styles')) return;

    const styles = document.createElement('style');
    styles.id = 'predrive-picker-styles';
    styles.textContent = `
      .predrive-picker-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: none;
        align-items: center;
        justify-content: center;
        z-index: 100000;
        animation: predrive-fade-in 0.2s ease;
      }

      @keyframes predrive-fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
      }

      .predrive-picker-modal {
        background: white;
        border-radius: 12px;
        width: 90%;
        max-width: 700px;
        max-height: 80vh;
        display: flex;
        flex-direction: column;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: predrive-slide-up 0.3s ease;
      }

      @keyframes predrive-slide-up {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .predrive-picker-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        border-bottom: 1px solid #E8EAED;
      }

      .predrive-picker-title {
        font-size: 18px;
        font-weight: 600;
        color: #191919;
        margin: 0;
      }

      .predrive-picker-close {
        background: none;
        border: none;
        font-size: 24px;
        color: #666;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
      }

      .predrive-picker-close:hover {
        background: #f0f0f0;
      }

      .predrive-picker-toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 20px;
        background: #F9FAFB;
        border-bottom: 1px solid #E8EAED;
        gap: 16px;
      }

      .predrive-picker-breadcrumb {
        display: flex;
        align-items: center;
        gap: 4px;
        flex: 1;
        overflow-x: auto;
        font-size: 14px;
      }

      .predrive-picker-breadcrumb-item {
        color: #2D8EFF;
        cursor: pointer;
        white-space: nowrap;
        padding: 4px 8px;
        border-radius: 4px;
      }

      .predrive-picker-breadcrumb-item:hover {
        background: rgba(45, 142, 255, 0.1);
      }

      .predrive-picker-breadcrumb-item.current {
        color: #191919;
        cursor: default;
      }

      .predrive-picker-breadcrumb-item.current:hover {
        background: none;
      }

      .predrive-picker-breadcrumb-sep {
        color: #999;
      }

      .predrive-picker-search input {
        padding: 8px 12px;
        border: 1px solid #E8EAED;
        border-radius: 8px;
        font-size: 14px;
        width: 200px;
      }

      .predrive-picker-search input:focus {
        outline: none;
        border-color: #2D8EFF;
      }

      .predrive-picker-content {
        flex: 1;
        overflow-y: auto;
        padding: 8px;
        min-height: 300px;
      }

      .predrive-picker-loading {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 200px;
        color: #666;
      }

      .predrive-picker-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 200px;
        color: #666;
      }

      .predrive-picker-empty-icon {
        font-size: 48px;
        margin-bottom: 12px;
        opacity: 0.5;
      }

      .predrive-picker-list {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }

      .predrive-picker-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.15s;
      }

      .predrive-picker-item:hover {
        background: #F3F4F6;
      }

      .predrive-picker-item.selected {
        background: rgba(45, 142, 255, 0.1);
      }

      .predrive-picker-item-icon {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        font-size: 18px;
      }

      .predrive-picker-item-icon.folder {
        background: #FEF3C7;
      }

      .predrive-picker-item-icon.document {
        background: #DBEAFE;
      }

      .predrive-picker-item-icon.spreadsheet {
        background: #D1FAE5;
      }

      .predrive-picker-item-icon.presentation {
        background: #FEE2E2;
      }

      .predrive-picker-item-info {
        flex: 1;
        min-width: 0;
      }

      .predrive-picker-item-name {
        font-size: 14px;
        font-weight: 500;
        color: #191919;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .predrive-picker-item-meta {
        font-size: 12px;
        color: #666;
      }

      .predrive-picker-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        border-top: 1px solid #E8EAED;
        background: #F9FAFB;
        border-radius: 0 0 12px 12px;
      }

      .predrive-picker-selected {
        font-size: 14px;
        color: #666;
      }

      .predrive-picker-actions {
        display: flex;
        gap: 8px;
      }

      .predrive-picker-btn {
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.15s;
      }

      .predrive-picker-btn-secondary {
        background: white;
        border: 1px solid #E8EAED;
        color: #191919;
      }

      .predrive-picker-btn-secondary:hover {
        background: #F3F4F6;
      }

      .predrive-picker-btn-primary {
        background: #2D8EFF;
        border: none;
        color: white;
      }

      .predrive-picker-btn-primary:hover:not(:disabled) {
        opacity: 0.9;
      }

      .predrive-picker-btn-primary:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    `;

    document.head.appendChild(styles);
  }

  /**
   * Load folder contents
   */
  async loadFolder(folderId) {
    this.currentFolderId = folderId;
    this.selectedFile = null;
    this.updateSelectedDisplay();

    const content = this.modal.querySelector('#predrive-content');
    content.innerHTML = '<div class="predrive-picker-loading">Loading...</div>';

    try {
      const headers = {};
      if (this.accessToken) {
        headers['Authorization'] = `Bearer ${this.accessToken}`;
      }

      const url = folderId
        ? `${this.options.apiUrl}/browse?folderId=${folderId}`
        : `${this.options.apiUrl}/browse`;

      const response = await fetch(url, { headers });
      const data = await response.json();

      this.path = data.path || [{ id: null, name: 'My Files' }];
      this.renderBreadcrumb();
      this.renderContent(data.folders || [], data.files || []);

    } catch (error) {
      console.error('Failed to load folder:', error);
      content.innerHTML = '<div class="predrive-picker-empty"><div class="predrive-picker-empty-icon">&#x26A0;</div><div>Failed to load files</div></div>';
    }
  }

  /**
   * Search files
   */
  async search(query) {
    const content = this.modal.querySelector('#predrive-content');
    content.innerHTML = '<div class="predrive-picker-loading">Searching...</div>';

    try {
      const headers = {};
      if (this.accessToken) {
        headers['Authorization'] = `Bearer ${this.accessToken}`;
      }

      const response = await fetch(`${this.options.apiUrl}/search?q=${encodeURIComponent(query)}`, { headers });
      const data = await response.json();

      this.renderContent([], data.results || []);

    } catch (error) {
      console.error('Search failed:', error);
      content.innerHTML = '<div class="predrive-picker-empty"><div>Search failed</div></div>';
    }
  }

  /**
   * Render breadcrumb
   */
  renderBreadcrumb() {
    const breadcrumb = this.modal.querySelector('#predrive-breadcrumb');
    breadcrumb.innerHTML = this.path.map((item, index) => {
      const isLast = index === this.path.length - 1;
      const sep = index < this.path.length - 1 ? '<span class="predrive-picker-breadcrumb-sep">/</span>' : '';

      return `
        <span class="predrive-picker-breadcrumb-item ${isLast ? 'current' : ''}"
              data-id="${item.id || ''}"
              ${isLast ? '' : `onclick="window._preDrivePicker.loadFolder('${item.id || ''}')"` }>
          ${this.escapeHtml(item.name)}
        </span>
        ${sep}
      `;
    }).join('');

    // Make picker accessible globally for breadcrumb clicks
    window._preDrivePicker = this;
  }

  /**
   * Render folder/file content
   */
  renderContent(folders, files) {
    const content = this.modal.querySelector('#predrive-content');

    if (folders.length === 0 && files.length === 0) {
      content.innerHTML = `
        <div class="predrive-picker-empty">
          <div class="predrive-picker-empty-icon">&#x1F4C2;</div>
          <div>This folder is empty</div>
        </div>
      `;
      return;
    }

    const items = [
      ...folders.map(f => this.renderItem(f, 'folder')),
      ...files.map(f => this.renderItem(f, 'file'))
    ];

    content.innerHTML = `<div class="predrive-picker-list">${items.join('')}</div>`;

    // Add click handlers
    content.querySelectorAll('.predrive-picker-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = item.dataset.id;
        const type = item.dataset.type;

        if (type === 'folder') {
          this.loadFolder(id);
        } else {
          this.selectFile({
            id,
            name: item.dataset.name,
            docType: item.dataset.doctype
          });
        }
      });

      // Double-click to open file
      item.addEventListener('dblclick', () => {
        if (item.dataset.type === 'file' && this.selectedFile) {
          this.close();
          this.options.onSelect(this.selectedFile);
        }
      });
    });
  }

  /**
   * Render a single item
   */
  renderItem(item, type) {
    const icons = {
      folder: '&#x1F4C1;',
      writer: '&#x1F4C4;',
      calc: '&#x1F4CA;',
      impress: '&#x1F4CA;',
      draw: '&#x1F3A8;',
      pdf: '&#x1F4C4;'
    };

    const iconClass = type === 'folder' ? 'folder' : (item.docType === 'calc' ? 'spreadsheet' : (item.docType === 'impress' ? 'presentation' : 'document'));
    const icon = type === 'folder' ? icons.folder : (icons[item.docType] || icons.writer);

    const meta = type === 'folder' ? 'Folder' : this.formatSize(item.size);

    return `
      <div class="predrive-picker-item"
           data-id="${item.id}"
           data-type="${type}"
           data-name="${this.escapeHtml(item.name)}"
           data-doctype="${item.docType || ''}">
        <div class="predrive-picker-item-icon ${iconClass}">${icon}</div>
        <div class="predrive-picker-item-info">
          <div class="predrive-picker-item-name">${this.escapeHtml(item.name)}</div>
          <div class="predrive-picker-item-meta">${meta}</div>
        </div>
      </div>
    `;
  }

  /**
   * Select a file
   */
  selectFile(file) {
    this.selectedFile = file;

    // Update UI
    this.modal.querySelectorAll('.predrive-picker-item').forEach(item => {
      item.classList.toggle('selected', item.dataset.id === file.id);
    });

    this.updateSelectedDisplay();
  }

  /**
   * Update selected file display
   */
  updateSelectedDisplay() {
    const selectedDiv = this.modal.querySelector('#predrive-selected');
    const selectBtn = this.modal.querySelector('#predrive-select');

    if (this.selectedFile) {
      selectedDiv.textContent = this.selectedFile.name;
      selectBtn.disabled = false;
    } else {
      selectedDiv.textContent = 'No file selected';
      selectBtn.disabled = true;
    }
  }

  /**
   * Format file size
   */
  formatSize(bytes) {
    if (!bytes) return '-';
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return `${size.toFixed(unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`;
  }

  /**
   * Escape HTML
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
  }
}

// Export
window.PreDrivePicker = PreDrivePicker;
