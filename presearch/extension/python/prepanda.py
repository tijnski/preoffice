#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PrePanda AI Assistant for LibreOffice
Main extension module that registers all UNO services

Copyright (c) 2024 Presearch
Licensed under MIT License
"""

import uno
import unohelper
from com.sun.star.task import XJobExecutor
from com.sun.star.lang import XServiceInfo
from com.sun.star.awt import XActionListener, XDialogEventHandler, XMouseListener, XWindowListener
from com.sun.star.ui import XUIElementFactory, XUIElement, XToolPanel
from com.sun.star.ui.UIElementType import TOOLPANEL as unoTOOLPANEL

import os
import json
import urllib.request
import urllib.error
import ssl

# Extension identifier
EXTENSION_ID = "com.presearch.prepanda"

# Configuration
CONFIG_FILE = "prepanda_config.json"

def get_config_path():
    """Get the path to the configuration file."""
    ctx = uno.getComponentContext()
    path_sub = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.util.PathSubstitution", ctx)
    user_url = path_sub.substituteVariables("$(user)", True)
    # Convert file:// URL to system path
    user_path = uno.fileUrlToSystemPath(user_url)
    return os.path.join(user_path, CONFIG_FILE)

def load_config():
    """Load configuration from file."""
    config_path = get_config_path()
    default_config = {
        "api_key": "",
        "api_url": "https://api.venice.ai/api/v1/chat/completions",
        "model": "llama-3.3-70b",
        "language": "English",
        "streaming": True,
        "remember_history": True
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**default_config, **config}
    except Exception:
        pass

    return default_config

def save_config(config):
    """Save configuration to file."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False

def call_venice_api(messages, config):
    """Call Venice.ai API and return the response."""
    if not config.get("api_key"):
        return "Error: API key not configured. Please set your Venice.ai API key in PrePanda Settings."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}"
    }

    data = json.dumps({
        "model": config.get("model", "llama-3.3-70b"),
        "messages": messages,
        "stream": False,
        "max_tokens": 4096
    }).encode('utf-8')

    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            config.get("api_url", "https://api.venice.ai/api/v1/chat/completions"),
            data=data,
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

    except urllib.error.HTTPError as e:
        return f"API Error: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Connection Error: {e.reason}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_selected_text(doc):
    """Get the currently selected text from the document."""
    try:
        controller = doc.getCurrentController()
        selection = controller.getSelection()

        if selection is None:
            return ""

        # Handle different selection types
        if hasattr(selection, 'getString'):
            return selection.getString()
        elif hasattr(selection, 'getCount'):
            # Multiple selections
            texts = []
            for i in range(selection.getCount()):
                item = selection.getByIndex(i)
                if hasattr(item, 'getString'):
                    texts.append(item.getString())
            return "\n".join(texts)

        return ""
    except Exception:
        return ""

def insert_text(doc, text):
    """Insert text at the current cursor position."""
    try:
        controller = doc.getCurrentController()
        selection = controller.getSelection()

        if hasattr(selection, 'setString'):
            selection.setString(text)
        else:
            # Fallback: insert at cursor
            text_obj = doc.getText()
            cursor = text_obj.createTextCursor()
            cursor.gotoEnd(False)
            text_obj.insertString(cursor, "\n" + text, False)
    except Exception as e:
        show_message(f"Could not insert text: {e}")

def update_sidebar(status_text, response_text):
    """Update the PrePanda sidebar panel with status and response text."""
    try:
        import prepanda_panel
        if prepanda_panel._panel_window:
            # Update status
            try:
                lbl = prepanda_panel._panel_window.getControl("lblStatus")
                if lbl:
                    lbl.setText(status_text)
            except:
                pass
            # Update output (renamed from txtResponse to txtOutput)
            try:
                txt = prepanda_panel._panel_window.getControl("txtOutput")
                if txt:
                    txt.setText(response_text)
            except:
                pass
            # Update global response for Apply
            prepanda_panel._current_response = response_text
            return True
    except Exception as e:
        try:
            with open("/tmp/prepanda_sidebar_update.log", "a") as f:
                f.write(f"Sidebar update error: {e}\n")
        except:
            pass
    return False

def show_message(message, title="PrePanda"):
    """Route message to sidebar instead of popup dialog."""
    # Try to update sidebar first
    if update_sidebar(title, message):
        return

    # Fallback: show brief notification only if sidebar update failed
    # In the future, this could be replaced with a toast notification
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    frame = desktop.getCurrentFrame()
    if frame:
        # Try to open the sidebar
        try:
            dispatcher = smgr.createInstanceWithContext(
                "com.sun.star.frame.DispatchHelper", ctx)
            # Open the sidebar
            dispatcher.executeDispatch(frame, ".uno:Sidebar", "", 0, ())
        except:
            pass


# =============================================================================
# Job Executor Services
# =============================================================================

class AskJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Open the Ask PrePanda dialog."""

    IMPLEMENTATION_NAME = "com.presearch.prepanda.Ask"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return AskJob(ctx)

    def trigger(self, args):
        """Handle Ask action - send to sidebar."""
        config = load_config()

        smgr = self.ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()

        selected = get_selected_text(doc)

        # Update sidebar with processing status
        update_sidebar("Processing: Ask...", "Thinking...")

        if selected:
            messages = [
                {"role": "system", "content": "You are PrePanda, a helpful AI assistant integrated into PreOffice. Help the user with their document."},
                {"role": "user", "content": f"The user has selected the following text:\n\n{selected}\n\nPlease help with this text."}
            ]
        else:
            messages = [
                {"role": "system", "content": "You are PrePanda, a helpful AI assistant integrated into PreOffice. Help the user with their document."},
                {"role": "user", "content": "Hello! How can you help me with my document?"}
            ]

        response = call_venice_api(messages, config)
        update_sidebar("Ask complete", response)

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


class SummarizeJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Summarize the selected text."""

    IMPLEMENTATION_NAME = "com.presearch.prepanda.Summarize"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return SummarizeJob(ctx)

    def trigger(self, args):
        config = load_config()

        smgr = self.ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()

        selected = get_selected_text(doc)

        if not selected:
            update_sidebar("No text selected", "Please select some text to summarize.")
            return

        update_sidebar("Processing: Summarize...", "Thinking...")

        messages = [
            {"role": "system", "content": "You are a concise summarizer. Provide a clear, brief summary of the text."},
            {"role": "user", "content": f"Summarize the following text:\n\n{selected}"}
        ]

        response = call_venice_api(messages, config)
        update_sidebar("Summarize complete", response)

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


class ImproveJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Improve the selected text."""

    IMPLEMENTATION_NAME = "com.presearch.prepanda.Improve"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return ImproveJob(ctx)

    def trigger(self, args):
        config = load_config()

        smgr = self.ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()

        selected = get_selected_text(doc)

        if not selected:
            update_sidebar("No text selected", "Please select some text to improve.")
            return

        update_sidebar("Processing: Improve...", "Thinking...")

        messages = [
            {"role": "system", "content": "You are a professional editor. Improve the text for clarity, style, and readability. Return only the improved text without explanations."},
            {"role": "user", "content": f"Improve this text:\n\n{selected}"}
        ]

        response = call_venice_api(messages, config)
        update_sidebar("Improve complete - click Apply to replace text", response)

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


class TranslateJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Translate the selected text."""

    IMPLEMENTATION_NAME = "com.presearch.prepanda.Translate"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return TranslateJob(ctx)

    def trigger(self, args):
        config = load_config()
        target_language = config.get("language", "English")

        smgr = self.ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()

        selected = get_selected_text(doc)

        if not selected:
            update_sidebar("No text selected", "Please select some text to translate.")
            return

        update_sidebar(f"Processing: Translate to {target_language}...", "Thinking...")

        messages = [
            {"role": "system", "content": f"You are a translator. Translate the text to {target_language}. Return only the translation without explanations."},
            {"role": "user", "content": f"Translate to {target_language}:\n\n{selected}"}
        ]

        response = call_venice_api(messages, config)
        update_sidebar(f"Translation to {target_language} complete", response)

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


class ExplainJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Explain the selected text."""

    IMPLEMENTATION_NAME = "com.presearch.prepanda.Explain"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return ExplainJob(ctx)

    def trigger(self, args):
        config = load_config()

        smgr = self.ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()

        selected = get_selected_text(doc)

        if not selected:
            update_sidebar("No text selected", "Please select some text to explain.")
            return

        update_sidebar("Processing: Explain...", "Thinking...")

        messages = [
            {"role": "system", "content": "You are a helpful teacher. Explain the text in simple, easy-to-understand terms."},
            {"role": "user", "content": f"Explain this:\n\n{selected}"}
        ]

        response = call_venice_api(messages, config)
        update_sidebar("Explanation complete", response)

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


class ProofreadJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Proofread the selected text."""

    IMPLEMENTATION_NAME = "com.presearch.prepanda.Proofread"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return ProofreadJob(ctx)

    def trigger(self, args):
        config = load_config()

        smgr = self.ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()

        selected = get_selected_text(doc)

        if not selected:
            update_sidebar("No text selected", "Please select some text to proofread.")
            return

        update_sidebar("Processing: Proofread...", "Thinking...")

        messages = [
            {"role": "system", "content": "You are a professional proofreader. Check for grammar, spelling, punctuation, and style issues. List the issues found and suggest corrections."},
            {"role": "user", "content": f"Proofread this text:\n\n{selected}"}
        ]

        response = call_venice_api(messages, config)
        update_sidebar("Proofreading complete", response)

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


class SettingsJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Open the PrePanda settings dialog."""

    IMPLEMENTATION_NAME = "com.presearch.prepanda.Settings"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return SettingsJob(ctx)

    def trigger(self, args):
        """Open PreOffice Preferences to PrePanda settings."""
        smgr = self.ctx.ServiceManager
        dispatcher = smgr.createInstanceWithContext(
            "com.sun.star.frame.DispatchHelper", self.ctx)
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        frame = desktop.getCurrentFrame()

        # Open the Options dialog - user can navigate to PreOffice > PrePanda AI
        dispatcher.executeDispatch(frame, ".uno:OptionsTreeDialog", "", 0, ())

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


# =============================================================================
# Options Dialog Handler
# =============================================================================

from com.sun.star.awt import XContainerWindowEventHandler

class OptionsHandler(unohelper.Base, XContainerWindowEventHandler):
    """Handler for the PrePanda options dialog in Preferences."""

    IMPLEMENTATION_NAME = "com.presearch.prepanda.OptionsHandler"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx
        self.config = load_config()

    @staticmethod
    def createInstance(ctx):
        return OptionsHandler(ctx)

    def getSupportedMethodNames(self):
        return ("external_event",)

    def callHandlerMethod(self, window, eventObject, method):
        if method == "external_event":
            return self._handleExternalEvent(window, eventObject)
        return False

    def _handleExternalEvent(self, window, event):
        if event == "ok":
            self._saveSettings(window)
            return True
        elif event == "back":
            self._saveSettings(window)
            return True
        elif event == "initialize":
            self._loadSettings(window)
            return True
        return False

    def _getControl(self, window, name):
        """Get a control from the window, handling different container types."""
        try:
            # Try direct access first
            ctrl = window.getControl(name)
            if ctrl:
                return ctrl
        except:
            pass

        # Try accessing through the peer/model
        try:
            model = window.getModel()
            if model:
                ctrl_model = model.getByName(name)
                if ctrl_model:
                    # Get the control from the container
                    return window.getControl(name)
        except:
            pass

        return None

    def _loadSettings(self, window):
        """Load current settings into dialog controls."""
        try:
            self.config = load_config()

            # Get the API key text field
            api_key_field = self._getControl(window, "txtApiKey")
            if api_key_field:
                api_key_field.setText(self.config.get("api_key", ""))

            # Get the model dropdown
            model_list = self._getControl(window, "lstModel")
            if model_list:
                models = ["llama-3.3-70b", "llama-3.1-405b", "deepseek-r1-671b"]
                current_model = self.config.get("model", "llama-3.3-70b")
                try:
                    idx = models.index(current_model)
                    model_list.selectItemPos(idx, True)
                except ValueError:
                    model_list.selectItemPos(0, True)

            # Get the language dropdown
            lang_list = self._getControl(window, "lstLanguage")
            if lang_list:
                languages = ["English", "Dutch", "German", "French", "Spanish", "Auto-detect"]
                current_lang = self.config.get("language", "English")
                try:
                    idx = languages.index(current_lang)
                    lang_list.selectItemPos(idx, True)
                except ValueError:
                    lang_list.selectItemPos(0, True)

        except Exception as e:
            # Log error to temp file for debugging
            try:
                with open("/tmp/prepanda_options_error.log", "a") as f:
                    f.write(f"Load error: {str(e)}\n")
            except:
                pass

    def _saveSettings(self, window):
        """Save dialog settings to config file."""
        try:
            # Reload config to preserve any values we're not editing
            self.config = load_config()

            # Get API key
            api_key_field = self._getControl(window, "txtApiKey")
            if api_key_field:
                text = api_key_field.getText()
                if text is not None:
                    self.config["api_key"] = text

            # Get model
            model_list = self._getControl(window, "lstModel")
            if model_list:
                models = ["llama-3.3-70b", "llama-3.1-405b", "deepseek-r1-671b"]
                idx = model_list.getSelectedItemPos()
                if 0 <= idx < len(models):
                    self.config["model"] = models[idx]

            # Get language
            lang_list = self._getControl(window, "lstLanguage")
            if lang_list:
                languages = ["English", "Dutch", "German", "French", "Spanish", "Auto-detect"]
                idx = lang_list.getSelectedItemPos()
                if 0 <= idx < len(languages):
                    self.config["language"] = languages[idx]

            result = save_config(self.config)

            # Log for debugging
            try:
                with open("/tmp/prepanda_options_error.log", "a") as f:
                    f.write(f"Save called. API key length: {len(self.config.get('api_key', ''))}, Result: {result}\n")
            except:
                pass

        except Exception as e:
            # Log error to temp file for debugging
            try:
                with open("/tmp/prepanda_options_error.log", "a") as f:
                    f.write(f"Save error: {str(e)}\n")
            except:
                pass

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


# =============================================================================
# Floating PrePanda Assistant (Clippy-style)
# =============================================================================

# Global reference to keep the assistant alive
_panda_assistant = None

class PandaMouseListener(unohelper.Base, XMouseListener):
    """Mouse listener for the floating panda icon."""

    def __init__(self, ctx, parent_frame):
        self.ctx = ctx
        self.parent_frame = parent_frame

    def mousePressed(self, event):
        """Handle click on the panda icon - open sidebar."""
        try:
            smgr = self.ctx.ServiceManager
            desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
            doc = desktop.getCurrentComponent()
            if doc:
                frame = doc.getCurrentController().getFrame()
                dispatcher = smgr.createInstanceWithContext(
                    "com.sun.star.frame.DispatchHelper", self.ctx)
                # Open the sidebar to show PrePanda panel
                dispatcher.executeDispatch(frame, ".uno:Sidebar", "", 0, ())
                update_sidebar("Ready", "Select text in your document and click an action button above, or use the PrePanda menu.")
        except Exception as e:
            pass

    def mouseReleased(self, event):
        pass

    def mouseEntered(self, event):
        pass

    def mouseExited(self, event):
        pass

    def disposing(self, event):
        pass


class PandaWindowListener(unohelper.Base, XWindowListener):
    """Window listener to reposition panda when parent window resizes."""

    def __init__(self, panda_dialog, parent_window):
        self.panda_dialog = panda_dialog
        self.parent_window = parent_window

    def windowResized(self, event):
        """Reposition panda dialog when window is resized."""
        try:
            self._reposition()
        except:
            pass

    def windowMoved(self, event):
        pass

    def windowShown(self, event):
        try:
            self._reposition()
        except:
            pass

    def windowHidden(self, event):
        pass

    def disposing(self, event):
        pass

    def _reposition(self):
        """Reposition the panda to bottom-right corner."""
        try:
            parent_rect = self.parent_window.getPosSize()
            dialog_width = 250
            dialog_height = 280
            margin = 50
            new_x = parent_rect.Width - dialog_width - margin
            new_y = parent_rect.Height - dialog_height - margin - 80  # Extra margin for status bar
            if new_x > 0 and new_y > 0:
                # Get absolute position
                abs_x = parent_rect.X + new_x
                abs_y = parent_rect.Y + new_y
                dialog_window = self.panda_dialog.getPeer().queryInterface(uno.getTypeByName("com.sun.star.awt.XWindow"))
                if dialog_window:
                    dialog_window.setPosSize(abs_x, abs_y, dialog_width, dialog_height, 15)
        except:
            pass


class PandaAssistant:
    """Floating PrePanda assistant icon manager."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.dialog = None
        self.visible = False
        self.frame = None

    def _get_extension_path(self):
        """Get the path to the extension directory."""
        try:
            pip = self.ctx.getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
            ext_path = pip.getPackageLocation(EXTENSION_ID)
            return uno.fileUrlToSystemPath(ext_path)
        except:
            return None

    def show(self, frame):
        """Show the floating panda assistant dialog."""
        if self.visible and self.dialog:
            return

        self.frame = frame

        try:
            smgr = self.ctx.ServiceManager

            # Create dialog provider
            dp = smgr.createInstanceWithContext("com.sun.star.awt.DialogProvider", self.ctx)

            # Create a simple dialog programmatically
            dialog_model = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", self.ctx)

            # Set dialog properties - much larger floating window
            dialog_model.Width = 200
            dialog_model.Height = 220
            dialog_model.Title = "PrePanda"
            dialog_model.Closeable = True
            dialog_model.Moveable = True
            dialog_model.DesktopAsParent = False

            # Try to set background
            try:
                dialog_model.BackgroundColor = 0xFFFFFF
            except:
                pass

            # Add a large button with panda emoji
            button_model = dialog_model.createInstance("com.sun.star.awt.UnoControlButtonModel")
            button_model.Name = "PandaButton"
            button_model.PositionX = 20
            button_model.PositionY = 20
            button_model.Width = 160
            button_model.Height = 140
            button_model.Label = "🐼\nClick me!"

            # Try to set font size for emoji
            try:
                button_model.FontHeight = 72
                button_model.MultiLine = True
            except:
                pass

            dialog_model.insertByName("PandaButton", button_model)

            # Add a label
            label_model = dialog_model.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
            label_model.Name = "HelpLabel"
            label_model.PositionX = 20
            label_model.PositionY = 170
            label_model.Width = 160
            label_model.Height = 40
            label_model.Label = "PrePanda AI Assistant"
            label_model.Align = 1  # Center

            try:
                label_model.FontHeight = 14
            except:
                pass

            dialog_model.insertByName("HelpLabel", label_model)

            # Create the dialog control
            dialog = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", self.ctx)
            dialog.setModel(dialog_model)

            # Get parent window for positioning
            parent_window = frame.getContainerWindow()
            parent_rect = parent_window.getPosSize()

            # Position in bottom-right corner (use pixels for window positioning)
            dialog_width = 250  # pixels
            dialog_height = 280  # pixels
            margin = 50
            pos_x = parent_rect.Width - dialog_width - margin
            pos_y = parent_rect.Height - dialog_height - margin - 80

            # Create peer - use None for a top-level floating window
            toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
            dialog.createPeer(toolkit, None)

            # Get the dialog window and position it
            dialog_window = dialog.getPeer().queryInterface(uno.getTypeByName("com.sun.star.awt.XWindow"))
            if dialog_window:
                # Get screen position of parent window
                parent_pos = parent_window.getPosSize()
                abs_x = parent_pos.X + pos_x
                abs_y = parent_pos.Y + pos_y
                dialog_window.setPosSize(abs_x, abs_y, dialog_width, dialog_height, 15)

            # Add click handler to button
            button = dialog.getControl("PandaButton")
            if button:
                button.addActionListener(PandaButtonListener(self.ctx, frame))

            # Add window listener for repositioning
            window_listener = PandaWindowListener(dialog, parent_window)
            parent_window.addWindowListener(window_listener)

            dialog.setVisible(True)
            self.dialog = dialog
            self.visible = True

        except Exception as e:
            # Log error for debugging
            try:
                with open("/tmp/prepanda_assistant.log", "a") as f:
                    import traceback
                    f.write(f"Show error: {str(e)}\n{traceback.format_exc()}\n")
            except:
                pass

    def hide(self):
        """Hide the floating panda dialog."""
        if self.dialog:
            try:
                self.dialog.setVisible(False)
                self.dialog.dispose()
                self.dialog = None
                self.visible = False
            except:
                pass

    def toggle(self, frame):
        """Toggle the floating panda visibility."""
        if self.visible:
            self.hide()
        else:
            self.show(frame)


class PandaButtonListener(unohelper.Base, XActionListener):
    """Action listener for the panda button click."""

    def __init__(self, ctx, frame):
        self.ctx = ctx
        self.frame = frame

    def actionPerformed(self, event):
        """Handle panda button click - open sidebar."""
        try:
            smgr = self.ctx.ServiceManager
            dispatcher = smgr.createInstanceWithContext(
                "com.sun.star.frame.DispatchHelper", self.ctx)
            # Open the sidebar to show PrePanda panel
            dispatcher.executeDispatch(self.frame, ".uno:Sidebar", "", 0, ())
            update_sidebar("Ready", "Hi! I'm PrePanda, your AI writing assistant.\n\nSelect text in your document and click an action button above:\n• Ask - Ask any question\n• Improve - Enhance your writing\n• Proofread - Check for errors\n• Summarize - Get a summary\n• Translate - Convert to another language\n• Explain - Get an explanation")
        except Exception as e:
            pass

    def disposing(self, event):
        pass


class ToggleAssistantJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Job to launch the standalone PrePanda Helper overlay application."""

    IMPLEMENTATION_NAME = "com.presearch.prepanda.ToggleAssistantJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return ToggleAssistantJob(ctx)

    def _get_helper_path(self):
        """Get the path to the helper script."""
        try:
            pip = self.ctx.getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
            ext_url = pip.getPackageLocation(EXTENSION_ID)
            ext_path = uno.fileUrlToSystemPath(ext_url)
            return os.path.join(ext_path, "python", "prepanda_helper.py")
        except:
            return None

    def trigger(self, args):
        """Launch the PrePanda Helper overlay app."""
        import subprocess

        try:
            helper_path = self._get_helper_path()

            if helper_path and os.path.exists(helper_path):
                # Launch the helper as a separate process
                # Use pythonw on macOS to avoid terminal window
                python_exe = sys.executable

                # Check if helper is already running (simple check via PID file)
                pid_file = os.path.expanduser("~/Library/Application Support/PrePanda/helper.pid")
                os.makedirs(os.path.dirname(pid_file), exist_ok=True)

                helper_running = False
                if os.path.exists(pid_file):
                    try:
                        with open(pid_file, 'r') as f:
                            pid = int(f.read().strip())
                        # Check if process is running
                        os.kill(pid, 0)
                        helper_running = True
                    except (OSError, ValueError):
                        # Process not running or invalid PID
                        helper_running = False

                if helper_running:
                    # Helper is running, bring it to front (via AppleScript on macOS)
                    try:
                        subprocess.run([
                            "osascript", "-e",
                            'tell application "System Events" to set frontmost of process "Python" to true'
                        ], capture_output=True)
                    except:
                        pass
                else:
                    # Launch new helper process
                    process = subprocess.Popen(
                        [python_exe, helper_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                    # Save PID
                    with open(pid_file, 'w') as f:
                        f.write(str(process.pid))
            else:
                # Fallback: show message if helper not found
                smgr = self.ctx.ServiceManager
                desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
                doc = desktop.getCurrentComponent()
                if doc:
                    frame = doc.getCurrentController().getFrame()
                    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
                    parent_win = frame.getContainerWindow()
                    msgbox = toolkit.createMessageBox(
                        parent_win, 1, 1,
                        "PrePanda Helper",
                        f"Helper not found at: {helper_path}"
                    )
                    msgbox.execute()

        except Exception as e:
            # Log error
            try:
                with open("/tmp/prepanda_helper_launch.log", "a") as f:
                    import traceback
                    f.write(f"Launch error: {str(e)}\n{traceback.format_exc()}\n")
            except:
                pass

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


# =============================================================================
# UNO Component Registration
# =============================================================================
# Note: Sidebar panel factory is now in prepanda_panel.py

g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(
    AskJob.createInstance,
    AskJob.IMPLEMENTATION_NAME,
    AskJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    SummarizeJob.createInstance,
    SummarizeJob.IMPLEMENTATION_NAME,
    SummarizeJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    ImproveJob.createInstance,
    ImproveJob.IMPLEMENTATION_NAME,
    ImproveJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    TranslateJob.createInstance,
    TranslateJob.IMPLEMENTATION_NAME,
    TranslateJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    ExplainJob.createInstance,
    ExplainJob.IMPLEMENTATION_NAME,
    ExplainJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    ProofreadJob.createInstance,
    ProofreadJob.IMPLEMENTATION_NAME,
    ProofreadJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    SettingsJob.createInstance,
    SettingsJob.IMPLEMENTATION_NAME,
    SettingsJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    OptionsHandler.createInstance,
    OptionsHandler.IMPLEMENTATION_NAME,
    OptionsHandler.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    ToggleAssistantJob.createInstance,
    ToggleAssistantJob.IMPLEMENTATION_NAME,
    ToggleAssistantJob.SERVICE_NAMES
)
