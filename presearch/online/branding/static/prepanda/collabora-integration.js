/**
 * PrePanda Collabora Online Integration
 * Adds AI assistant sidebar to Collabora Online editor
 */

(function() {
  'use strict';

  // Configuration
  const PREPANDA_URL = '/static/prepanda/index.html';
  const SIDEBAR_WIDTH = 380;

  // State
  let sidebarOpen = false;
  let prepandaFrame = null;
  let prepandaReady = false;
  let currentSelection = '';

  /**
   * Initialize PrePanda integration
   */
  function init() {
    // Wait for Collabora to be ready
    if (typeof window.map === 'undefined') {
      setTimeout(init, 500);
      return;
    }

    console.log('[PrePanda] Initializing integration...');

    // Create sidebar
    createSidebar();

    // Add toolbar button
    addToolbarButton();

    // Listen for selection changes
    setupSelectionListener();

    // Listen for messages from PrePanda iframe
    window.addEventListener('message', handleMessage);

    console.log('[PrePanda] Integration ready');
  }

  /**
   * Create the sidebar container and iframe
   */
  function createSidebar() {
    // Create sidebar container
    const sidebar = document.createElement('div');
    sidebar.id = 'prepanda-sidebar';
    sidebar.style.cssText = `
      position: fixed;
      top: 0;
      right: -${SIDEBAR_WIDTH}px;
      width: ${SIDEBAR_WIDTH}px;
      height: 100%;
      background: #ffffff;
      box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
      z-index: 10000;
      transition: right 0.3s ease;
      display: flex;
      flex-direction: column;
    `;

    // Create header
    const header = document.createElement('div');
    header.style.cssText = `
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 12px;
      background: #2D8EFF;
      color: white;
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 14px;
      font-weight: 600;
    `;
    header.innerHTML = `
      <span>&#x1F43C; PrePanda AI</span>
      <button id="prepanda-close-btn" style="
        background: transparent;
        border: none;
        color: white;
        cursor: pointer;
        font-size: 18px;
        padding: 4px 8px;
        opacity: 0.8;
      ">&times;</button>
    `;
    sidebar.appendChild(header);

    // Create iframe
    prepandaFrame = document.createElement('iframe');
    prepandaFrame.id = 'prepanda-frame';
    prepandaFrame.style.cssText = `
      flex: 1;
      width: 100%;
      border: none;
      background: #f4f4f4;
    `;
    sidebar.appendChild(prepandaFrame);

    document.body.appendChild(sidebar);

    // Close button handler
    document.getElementById('prepanda-close-btn').addEventListener('click', toggleSidebar);
  }

  /**
   * Add PrePanda button to toolbar
   */
  function addToolbarButton() {
    // Try to find the toolbar
    const toolbar = document.querySelector('.notebookbar') ||
                   document.querySelector('#toolbar-up') ||
                   document.querySelector('.toolbar');

    if (!toolbar) {
      // Retry if toolbar not found yet
      setTimeout(addToolbarButton, 1000);
      return;
    }

    // Create button container
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'prepanda-toolbar-btn';
    buttonContainer.style.cssText = `
      display: inline-flex;
      align-items: center;
      margin-left: 8px;
    `;

    // Create button
    const button = document.createElement('button');
    button.id = 'prepanda-toggle-btn';
    button.title = 'PrePanda AI Assistant';
    button.style.cssText = `
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      background: #2D8EFF;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 13px;
      font-weight: 500;
      transition: opacity 0.15s;
    `;
    button.innerHTML = `
      <span style="font-size: 16px;">&#x1F43C;</span>
      <span>PrePanda</span>
    `;
    button.addEventListener('click', toggleSidebar);
    button.addEventListener('mouseenter', () => button.style.opacity = '0.8');
    button.addEventListener('mouseleave', () => button.style.opacity = '1');

    buttonContainer.appendChild(button);

    // Try to insert at a good position
    const insertPoint = toolbar.querySelector('.unoSave') ||
                       toolbar.querySelector('.unoUndo') ||
                       toolbar.firstChild;

    if (insertPoint && insertPoint.parentNode) {
      insertPoint.parentNode.insertBefore(buttonContainer, insertPoint.nextSibling);
    } else {
      toolbar.appendChild(buttonContainer);
    }

    console.log('[PrePanda] Toolbar button added');
  }

  /**
   * Toggle sidebar visibility
   */
  function toggleSidebar() {
    const sidebar = document.getElementById('prepanda-sidebar');
    if (!sidebar) return;

    sidebarOpen = !sidebarOpen;

    if (sidebarOpen) {
      sidebar.style.right = '0';

      // Load iframe if not loaded
      if (!prepandaFrame.src) {
        // Get access token from URL
        const urlParams = new URLSearchParams(window.location.search);
        const accessToken = urlParams.get('access_token') || '';
        prepandaFrame.src = `${PREPANDA_URL}?access_token=${accessToken}`;
      }

      // Send current selection if any
      if (currentSelection && prepandaReady) {
        sendSelectionToPrePanda();
      }
    } else {
      sidebar.style.right = `-${SIDEBAR_WIDTH}px`;
    }
  }

  /**
   * Setup listener for text selection changes
   */
  function setupSelectionListener() {
    // Collabora uses postMessage for selection events
    // We also poll the selection periodically

    setInterval(() => {
      try {
        const selection = window.getSelection();
        const text = selection ? selection.toString().trim() : '';

        if (text && text !== currentSelection) {
          currentSelection = text;
          if (sidebarOpen && prepandaReady) {
            sendSelectionToPrePanda();
          }
        }
      } catch (e) {
        // Ignore cross-origin errors
      }
    }, 1000);

    // Also listen for Collabora's selection events
    if (window.map) {
      window.map.on('textselectioncontent', function(e) {
        if (e.text) {
          currentSelection = e.text;
          if (sidebarOpen && prepandaReady) {
            sendSelectionToPrePanda();
          }
        }
      });
    }
  }

  /**
   * Send selection to PrePanda iframe
   */
  function sendSelectionToPrePanda() {
    if (!prepandaFrame || !prepandaFrame.contentWindow) return;

    prepandaFrame.contentWindow.postMessage({
      type: 'setContext',
      text: currentSelection
    }, '*');
  }

  /**
   * Handle messages from PrePanda iframe
   */
  function handleMessage(event) {
    const data = event.data;

    if (data.type === 'prepandaReady') {
      prepandaReady = true;
      console.log('[PrePanda] Iframe ready');

      // Send current selection if any
      if (currentSelection) {
        sendSelectionToPrePanda();
      }

      // Send dark mode preference
      const isDark = document.body.classList.contains('dark') ||
                    window.matchMedia('(prefers-color-scheme: dark)').matches;
      prepandaFrame.contentWindow.postMessage({
        type: 'setDarkMode',
        enabled: isDark
      }, '*');
    }

    if (data.type === 'insertText' && data.text) {
      // Insert text into document (if Collabora supports it)
      if (window.map && window.map._docLayer) {
        window.map._docLayer._postKeyboardEvent('input', 0, 0);
        // Note: Full text insertion requires UNO command
        console.log('[PrePanda] Insert text requested:', data.text.substring(0, 50));
      }
    }
  }

  /**
   * Keyboard shortcut handler
   */
  function handleKeyboard(e) {
    // Ctrl+Shift+P to toggle PrePanda
    if (e.ctrlKey && e.shiftKey && e.key === 'P') {
      e.preventDefault();
      toggleSidebar();
    }
  }

  // Add keyboard listener
  document.addEventListener('keydown', handleKeyboard);

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
