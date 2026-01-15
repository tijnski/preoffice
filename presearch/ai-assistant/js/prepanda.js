/**
 * PrePanda AI Assistant for PreOffice
 * Based on Presearch PreGPT architecture
 * Uses Venice.ai API for AI responses
 */

class PrePandaAssistant {
  constructor(config = {}) {
    this.config = {
      apiUrl: config.apiUrl || 'https://api.venice.ai/api/v1',
      apiKey: config.apiKey || '',
      model: config.model || 'llama-3.2-3b',
      modelAsk: config.modelAsk || 'llama-3.3-70b',
      maxTokens: config.maxTokens || 500,
      temperature: config.temperature || 0.7,
      ...config
    };

    this.messages = [];
    this.isLoading = false;
    this.documentContext = null;
    this.container = null;
    this.darkMode = false;

    // Bind methods
    this.handleSend = this.handleSend.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
  }

  /**
   * Initialize the assistant UI
   * @param {HTMLElement} container - Container element
   */
  init(container) {
    this.container = container;
    this.render();
    this.attachEventListeners();
    this.showWelcome();
  }

  /**
   * Render the assistant UI
   */
  render() {
    const darkClass = this.darkMode ? 'prepanda-dark' : '';

    this.container.innerHTML = `
      <div class="prepanda-container ${darkClass}" id="prepanda-main">
        <!-- Header -->
        <div class="prepanda-header">
          <div class="prepanda-header-left">
            <span style="font-size: 24px;">🐼</span>
            <div>
              <div class="prepanda-header-title">Ask PrePanda</div>
              <div class="prepanda-header-subtitle">AI Writing Assistant</div>
            </div>
          </div>
          <div class="prepanda-header-actions">
            <button class="prepanda-header-btn" id="prepanda-settings-btn" title="Settings">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </button>
            <button class="prepanda-header-btn" id="prepanda-clear-btn" title="Clear Chat">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Settings Panel (hidden by default) -->
        <div class="prepanda-settings" id="prepanda-settings-panel" style="display: none;">
          <div class="prepanda-settings-title">Settings</div>
          <div class="prepanda-settings-row">
            <span class="prepanda-settings-label">Dark Mode</span>
            <label class="prepanda-toggle">
              <input type="checkbox" id="prepanda-dark-toggle" ${this.darkMode ? 'checked' : ''}>
              <span class="prepanda-toggle-slider"></span>
            </label>
          </div>
          <div class="prepanda-settings-row">
            <span class="prepanda-settings-label">Response Style</span>
            <select class="prepanda-select" id="prepanda-style-select">
              <option value="concise">Concise</option>
              <option value="detailed">Detailed</option>
              <option value="creative">Creative</option>
            </select>
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
          <span class="prepanda-context-label">Document:</span>
          <span id="prepanda-doc-name">Untitled</span>
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
    // Send button
    const sendBtn = document.getElementById('prepanda-send-btn');
    sendBtn?.addEventListener('click', this.handleSend);

    // Input enter key
    const input = document.getElementById('prepanda-input');
    input?.addEventListener('keypress', this.handleKeyPress);

    // Settings toggle
    const settingsBtn = document.getElementById('prepanda-settings-btn');
    settingsBtn?.addEventListener('click', () => this.toggleSettings());

    // Clear button
    const clearBtn = document.getElementById('prepanda-clear-btn');
    clearBtn?.addEventListener('click', () => this.clearChat());

    // Dark mode toggle
    const darkToggle = document.getElementById('prepanda-dark-toggle');
    darkToggle?.addEventListener('change', (e) => this.setDarkMode(e.target.checked));

    // Quick action buttons
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
        <div class="prepanda-welcome-icon">🐼</div>
        <div class="prepanda-welcome-title">Hello! I'm PrePanda</div>
        <div class="prepanda-welcome-text">
          Your AI writing assistant. I can help you summarize, improve, translate,
          or explain your documents. Just select text and ask me anything!
        </div>
      </div>
    `;
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
   * @param {string} message - User message
   */
  async sendMessage(message) {
    // Add user message to UI
    this.addMessage('user', message);

    // Show loading
    this.setLoading(true);

    try {
      // Build context
      const systemPrompt = this.buildSystemPrompt();
      const messages = this.buildMessages(message);

      // Call Venice.ai API
      const response = await this.callAPI(systemPrompt, messages);

      // Add assistant response
      this.addMessage('assistant', response);

      // Store in history
      this.messages.push(
        { role: 'user', content: message },
        { role: 'assistant', content: response }
      );

    } catch (error) {
      console.error('PrePanda API Error:', error);
      this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Build system prompt based on context
   */
  buildSystemPrompt() {
    let prompt = `You are PrePanda, an AI writing assistant for PreOffice (part of the Presearch Pre-suite).
You help users with document writing, editing, summarizing, and improving their text.
Be helpful, concise, and professional. Use markdown formatting when appropriate.`;

    if (this.documentContext) {
      prompt += `\n\nDocument context:\n${this.documentContext}`;
    }

    return prompt;
  }

  /**
   * Build messages array for API
   */
  buildMessages(currentMessage) {
    // Include recent history (last 6 messages)
    const history = this.messages.slice(-6);
    return [
      ...history,
      { role: 'user', content: currentMessage }
    ];
  }

  /**
   * Call Venice.ai API
   */
  async callAPI(systemPrompt, messages) {
    const response = await fetch(`${this.config.apiUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKey}`
      },
      body: JSON.stringify({
        model: this.config.modelAsk,
        messages: [
          { role: 'system', content: systemPrompt },
          ...messages
        ],
        temperature: this.config.temperature,
        max_tokens: this.config.maxTokens
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content || 'No response generated.';
  }

  /**
   * Add message to UI
   */
  addMessage(role, content) {
    const messagesContainer = document.getElementById('prepanda-messages');
    if (!messagesContainer) return;

    // Clear welcome message if present
    const welcome = messagesContainer.querySelector('.prepanda-welcome');
    if (welcome) welcome.remove();

    const messageDiv = document.createElement('div');
    messageDiv.className = `prepanda-message prepanda-message-${role}`;

    const avatar = role === 'assistant' ? '🐼' : '👤';
    const avatarClass = role === 'assistant' ? 'prepanda-avatar-assistant' : 'prepanda-avatar-user';
    const bubbleClass = role === 'assistant' ? 'prepanda-bubble-assistant' : 'prepanda-bubble-user';

    // Parse markdown for assistant messages
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
      // Escape HTML first
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Code
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      // Line breaks
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

    // Remove existing loading indicator
    const existingLoader = messagesContainer.querySelector('.prepanda-loading-container');
    if (existingLoader) existingLoader.remove();

    if (loading) {
      const loaderDiv = document.createElement('div');
      loaderDiv.className = 'prepanda-message prepanda-message-assistant prepanda-loading-container';
      loaderDiv.innerHTML = `
        <div class="prepanda-avatar prepanda-avatar-assistant">🐼</div>
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
   * Handle quick actions
   */
  handleQuickAction(action) {
    const prompts = {
      summarize: 'Please summarize the selected text concisely.',
      improve: 'Please improve the writing of the selected text, making it clearer and more professional.',
      translate: 'Please translate the selected text to English (or specify the target language).',
      explain: 'Please explain the selected text in simple terms.'
    };

    const prompt = prompts[action] || 'How can I help with the selected text?';

    // If we have document context, prepend it
    let message = prompt;
    if (this.documentContext) {
      message = `${prompt}\n\nText:\n${this.documentContext}`;
    }

    this.sendMessage(message);
  }

  /**
   * Set document context (selected text or full document)
   */
  setDocumentContext(text, docName = 'Document') {
    this.documentContext = text;

    const contextDiv = document.getElementById('prepanda-context');
    const docNameSpan = document.getElementById('prepanda-doc-name');

    if (contextDiv && text) {
      contextDiv.style.display = 'block';
      if (docNameSpan) {
        docNameSpan.textContent = docName + (text.length > 100 ? ' (selection)' : '');
      }
    } else if (contextDiv) {
      contextDiv.style.display = 'none';
    }
  }

  /**
   * Toggle settings panel
   */
  toggleSettings() {
    const panel = document.getElementById('prepanda-settings-panel');
    if (panel) {
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
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

  /**
   * Clear chat history
   */
  clearChat() {
    this.messages = [];
    this.showWelcome();
  }

  /**
   * Update API configuration
   */
  setConfig(config) {
    this.config = { ...this.config, ...config };
  }
}

// Export for use in PreOffice
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PrePandaAssistant;
}

// Global instance
window.PrePandaAssistant = PrePandaAssistant;
