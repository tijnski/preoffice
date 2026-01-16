/**
 * PrePanda AI Assistant for PreOffice Web
 * Web-specific version that uses server-side API proxy
 */

class PrePandaWeb {
  constructor(config = {}) {
    this.config = {
      apiUrl: config.apiUrl || '/api/ai',
      ...config
    };

    this.messages = [];
    this.isLoading = false;
    this.documentContext = null;
    this.container = null;
    this.darkMode = false;
    this.accessToken = null;

    // Bind methods
    this.handleSend = this.handleSend.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
  }

  /**
   * Set access token for authenticated requests
   */
  setAccessToken(token) {
    this.accessToken = token;
  }

  /**
   * Initialize the assistant UI
   */
  init(container) {
    this.container = container;
    this.render();
    this.attachEventListeners();
    this.showWelcome();
    this.checkAIStatus();
  }

  /**
   * Check if AI service is available
   */
  async checkAIStatus() {
    try {
      const response = await fetch(`${this.config.apiUrl}/status`);
      const data = await response.json();

      if (!data.enabled) {
        this.showServiceUnavailable();
      }
    } catch (error) {
      console.warn('Could not check AI status:', error);
    }
  }

  /**
   * Render the assistant UI
   */
  render() {
    const darkClass = this.darkMode ? 'prepanda-dark' : '';

    this.container.innerHTML = `
      <div class="prepanda-container prepanda-web ${darkClass}" id="prepanda-main">
        <!-- Header -->
        <div class="prepanda-header">
          <div class="prepanda-header-left">
            <span class="prepanda-logo">&#x1F43C;</span>
            <div>
              <div class="prepanda-header-title">PrePanda</div>
              <div class="prepanda-header-subtitle">AI Writing Assistant</div>
            </div>
          </div>
          <div class="prepanda-header-actions">
            <button class="prepanda-header-btn" id="prepanda-clear-btn" title="Clear Chat">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="prepanda-actions" id="prepanda-actions">
          <button class="prepanda-action-btn" data-action="summarize">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            Summarize
          </button>
          <button class="prepanda-action-btn" data-action="improve">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            Improve
          </button>
          <button class="prepanda-action-btn" data-action="translate">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"/>
            </svg>
            Translate
          </button>
          <button class="prepanda-action-btn" data-action="explain">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Explain
          </button>
        </div>

        <!-- Messages Container -->
        <div class="prepanda-messages" id="prepanda-messages">
          <!-- Messages will be inserted here -->
        </div>

        <!-- Document Context -->
        <div class="prepanda-context" id="prepanda-context" style="display: none;">
          <span class="prepanda-context-label">Selection:</span>
          <span id="prepanda-context-text"></span>
        </div>

        <!-- Input Area -->
        <div class="prepanda-input-area">
          <div class="prepanda-input-wrapper">
            <input
              type="text"
              class="prepanda-input"
              id="prepanda-input"
              placeholder="Ask PrePanda anything..."
              autocomplete="off"
            >
            <button class="prepanda-send-btn" id="prepanda-send-btn" title="Send">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    const sendBtn = document.getElementById('prepanda-send-btn');
    sendBtn?.addEventListener('click', this.handleSend);

    const input = document.getElementById('prepanda-input');
    input?.addEventListener('keypress', this.handleKeyPress);

    const clearBtn = document.getElementById('prepanda-clear-btn');
    clearBtn?.addEventListener('click', () => this.clearChat());

    const actionBtns = document.querySelectorAll('.prepanda-action-btn');
    actionBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const action = e.currentTarget.dataset.action;
        this.handleQuickAction(action);
      });
    });
  }

  /**
   * Show welcome message
   */
  showWelcome() {
    const messagesContainer = document.getElementById('prepanda-messages');
    if (!messagesContainer) return;

    messagesContainer.innerHTML = `
      <div class="prepanda-welcome">
        <div class="prepanda-welcome-icon">&#x1F43C;</div>
        <div class="prepanda-welcome-title">Hello! I'm PrePanda</div>
        <div class="prepanda-welcome-text">
          Your AI writing assistant. Select text in your document and use the quick actions above, or ask me anything!
        </div>
      </div>
    `;
  }

  /**
   * Show service unavailable message
   */
  showServiceUnavailable() {
    const messagesContainer = document.getElementById('prepanda-messages');
    if (!messagesContainer) return;

    messagesContainer.innerHTML = `
      <div class="prepanda-welcome">
        <div class="prepanda-welcome-icon">&#x26A0;</div>
        <div class="prepanda-welcome-title">AI Service Unavailable</div>
        <div class="prepanda-welcome-text">
          The AI assistant is not configured on this server. Please contact your administrator.
        </div>
      </div>
    `;

    // Disable inputs
    const input = document.getElementById('prepanda-input');
    const sendBtn = document.getElementById('prepanda-send-btn');
    const actionBtns = document.querySelectorAll('.prepanda-action-btn');

    if (input) input.disabled = true;
    if (sendBtn) sendBtn.disabled = true;
    actionBtns.forEach(btn => btn.disabled = true);
  }

  /**
   * Handle enter key press
   */
  handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.handleSend();
    }
  }

  /**
   * Handle send message
   */
  async handleSend() {
    const input = document.getElementById('prepanda-input');
    if (!input) return;

    const message = input.value.trim();
    if (!message || this.isLoading) return;

    input.value = '';
    await this.sendMessage(message);
  }

  /**
   * Send a message to the AI
   */
  async sendMessage(message) {
    this.addMessage('user', message);
    this.setLoading(true);

    try {
      const headers = {
        'Content-Type': 'application/json'
      };

      if (this.accessToken) {
        headers['Authorization'] = `Bearer ${this.accessToken}`;
      }

      const response = await fetch(`${this.config.apiUrl}/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          messages: [
            ...this.messages.map(m => ({ role: m.role, content: m.content })),
            { role: 'user', content: message }
          ],
          context: this.documentContext
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      this.addMessage('assistant', data.content);

      this.messages.push(
        { role: 'user', content: message },
        { role: 'assistant', content: data.content }
      );

    } catch (error) {
      console.error('PrePanda API Error:', error);
      this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Handle quick actions
   */
  async handleQuickAction(action) {
    if (!this.documentContext) {
      this.addMessage('assistant', 'Please select some text in your document first, then try the action again.');
      return;
    }

    this.addMessage('user', `[${action.charAt(0).toUpperCase() + action.slice(1)}] ${this.documentContext.substring(0, 100)}...`);
    this.setLoading(true);

    try {
      const headers = {
        'Content-Type': 'application/json'
      };

      if (this.accessToken) {
        headers['Authorization'] = `Bearer ${this.accessToken}`;
      }

      const response = await fetch(`${this.config.apiUrl}/action`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          action,
          text: this.documentContext
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      this.addMessage('assistant', data.content);

    } catch (error) {
      console.error('PrePanda Action Error:', error);
      this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Set document context (selected text)
   */
  setDocumentContext(text) {
    this.documentContext = text;

    const contextDiv = document.getElementById('prepanda-context');
    const contextText = document.getElementById('prepanda-context-text');

    if (contextDiv && text) {
      contextDiv.style.display = 'block';
      if (contextText) {
        contextText.textContent = text.length > 50 ? text.substring(0, 50) + '...' : text;
      }
    } else if (contextDiv) {
      contextDiv.style.display = 'none';
    }
  }

  /**
   * Add message to UI
   */
  addMessage(role, content) {
    const messagesContainer = document.getElementById('prepanda-messages');
    if (!messagesContainer) return;

    const welcome = messagesContainer.querySelector('.prepanda-welcome');
    if (welcome) welcome.remove();

    const messageDiv = document.createElement('div');
    messageDiv.className = `prepanda-message prepanda-message-${role}`;

    const avatar = role === 'assistant' ? '&#x1F43C;' : '&#x1F464;';
    const avatarClass = role === 'assistant' ? 'prepanda-avatar-assistant' : 'prepanda-avatar-user';
    const bubbleClass = role === 'assistant' ? 'prepanda-bubble-assistant' : 'prepanda-bubble-user';

    const displayContent = role === 'assistant' ? this.parseMarkdown(content) : this.escapeHtml(content);

    messageDiv.innerHTML = `
      <div class="prepanda-avatar ${avatarClass}">${avatar}</div>
      <div class="prepanda-bubble ${bubbleClass}">${displayContent}</div>
    `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  /**
   * Parse simple markdown
   */
  parseMarkdown(text) {
    if (!text) return '';

    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }

  /**
   * Escape HTML
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Set loading state
   */
  setLoading(loading) {
    this.isLoading = loading;

    const sendBtn = document.getElementById('prepanda-send-btn');
    if (sendBtn) sendBtn.disabled = loading;

    const messagesContainer = document.getElementById('prepanda-messages');
    if (!messagesContainer) return;

    const existingLoader = messagesContainer.querySelector('.prepanda-loading-container');
    if (existingLoader) existingLoader.remove();

    if (loading) {
      const loaderDiv = document.createElement('div');
      loaderDiv.className = 'prepanda-message prepanda-message-assistant prepanda-loading-container';
      loaderDiv.innerHTML = `
        <div class="prepanda-avatar prepanda-avatar-assistant">&#x1F43C;</div>
        <div class="prepanda-bubble prepanda-bubble-assistant prepanda-loading">
          <div class="prepanda-loading-dot"></div>
          <div class="prepanda-loading-dot"></div>
          <div class="prepanda-loading-dot"></div>
        </div>
      `;
      messagesContainer.appendChild(loaderDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  /**
   * Clear chat history
   */
  clearChat() {
    this.messages = [];
    this.showWelcome();
  }

  /**
   * Set dark mode
   */
  setDarkMode(enabled) {
    this.darkMode = enabled;
    const container = document.getElementById('prepanda-main');
    if (container) {
      container.classList.toggle('prepanda-dark', enabled);
    }
  }
}

// Export for use
window.PrePandaWeb = PrePandaWeb;
