#!/usr/bin/env python3
"""
PrePanda AI Sidebar Panel
All AI interactions happen in this sidebar - no popups.
Clean, compact, readable UI with chat-style interface.
"""

import uno
import unohelper
import json
import urllib.request
import urllib.error
import ssl
import os
import threading
import traceback

# Debug logging
def log(msg):
    try:
        with open("/tmp/prepanda_panel.log", "a") as f:
            f.write(f"{msg}\n")
    except:
        pass

log("=== PrePanda Panel Module Loading ===")

from com.sun.star.ui import XUIElementFactory, XUIElement, XToolPanel, XSidebarPanel
from com.sun.star.ui.UIElementType import TOOLPANEL as unoTOOLPANEL
from com.sun.star.awt import XActionListener, XKeyListener

log("Imports successful")

# Constants
IMPL_NAME = "com.presearch.prepanda.PanelFactory"
SERVICES = (IMPL_NAME,)
EXT_ID = "com.presearch.preoffice"
XDL_PATH = "dialogs/prepanda_sidebar.xdl"
CONFIG_FILE = "prepanda_config.json"

# Global state
_panel_window = None
_current_response = ""
_conversation = []


def get_config_path():
    """Get config file path."""
    try:
        ctx = uno.getComponentContext()
        ps = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.util.PathSubstitution", ctx)
        user_url = ps.substituteVariables("$(user)", True)
        return os.path.join(uno.fileUrlToSystemPath(user_url), CONFIG_FILE)
    except:
        return None


def load_config():
    """Load config from file."""
    path = get_config_path()
    defaults = {
        "api_key": "",
        "api_url": "https://api.venice.ai/api/v1/chat/completions",
        "model": "llama-3.3-70b",
        "language": "English"
    }
    try:
        if path and os.path.exists(path):
            with open(path, 'r') as f:
                return {**defaults, **json.load(f)}
    except:
        pass
    return defaults


def call_ai(messages, config):
    """Call Venice.ai API."""
    if not config.get("api_key"):
        return "Please configure your API key in Settings."

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        data = json.dumps({
            "model": config.get("model", "llama-3.3-70b"),
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7
        }).encode('utf-8')

        req = urllib.request.Request(
            config.get("api_url"),
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['api_key']}"
            },
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"


class PanelActions(unohelper.Base, XActionListener):
    """Handles all button clicks in the sidebar."""

    def __init__(self, ctx, window):
        self.ctx = ctx
        self.window = window
        log("PanelActions initialized")

    def _get_control(self, name):
        """Get a control by name."""
        try:
            return self.window.getControl(name)
        except:
            return None

    def _get_selection(self):
        """Get selected text from document."""
        try:
            smgr = self.ctx.ServiceManager
            desktop = smgr.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.ctx)
            doc = desktop.getCurrentComponent()
            if doc:
                sel = doc.getCurrentController().getSelection()
                if sel:
                    if hasattr(sel, 'getString'):
                        return sel.getString()
                    elif hasattr(sel, 'getByIndex'):
                        parts = []
                        for i in range(sel.getCount()):
                            p = sel.getByIndex(i)
                            if hasattr(p, 'getString'):
                                parts.append(p.getString())
                        return "\n".join(parts)
        except:
            pass
        return ""

    def _set_status(self, msg):
        """Update status label."""
        ctrl = self._get_control("lblStatus")
        if ctrl:
            ctrl.setText(msg)

    def _set_output(self, text):
        """Update output area."""
        global _current_response
        _current_response = text
        ctrl = self._get_control("txtOutput")
        if ctrl:
            ctrl.setText(text)

    def _append_output(self, text):
        """Append to output area."""
        ctrl = self._get_control("txtOutput")
        if ctrl:
            current = ctrl.getText()
            new_text = f"{current}\n\n{text}" if current else text
            ctrl.setText(new_text)
            global _current_response
            _current_response = new_text

    def _get_input(self):
        """Get text from input field."""
        ctrl = self._get_control("txtInput")
        return ctrl.getText() if ctrl else ""

    def _clear_input(self):
        """Clear input field."""
        ctrl = self._get_control("txtInput")
        if ctrl:
            ctrl.setText("")

    def _run_ai(self, action, text, system_prompt=None, apply_directly=False):
        """Run AI action in background thread.

        Args:
            action: The action name (e.g., "Improve", "Bullets")
            text: The text to process
            system_prompt: Optional custom system prompt
            apply_directly: If True, apply result directly to document without showing in output
        """
        if not text.strip():
            self._set_status("No text selected!")
            self._set_output("Please select some text in your document first.")
            return

        config = load_config()
        self._set_status(f"Processing: {action}...")
        if not apply_directly:
            self._append_output(f"--- {action} ---\nProcessing...")

        # Build messages
        prompts = {
            "Ask": "You are PrePanda, a helpful AI assistant. Answer the user's question.",
            "Improve": "Improve this text for clarity and style. Return only the improved text.",
            "Proofread": "Check for grammar, spelling, and punctuation. List issues and provide corrected text.",
            "Summarize": "Provide a concise summary of this text.",
            "Translate": f"Translate this text to {config.get('language', 'English')}. Return only the translation.",
            "Explain": "Explain this text in simple terms.",
            "Bullets": "Convert this text into a bulleted list of key points. Return only the bullet points.",
            "Continue": "Continue writing from where this text ends, maintaining the same style. Return only the continuation.",
            "Tone": "Rewrite this text in a more professional tone. Return only the rewritten text.",
        }

        sys_msg = system_prompt or prompts.get(action, "Help the user with this text.")
        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": text}
        ]

        def do_call():
            try:
                response = call_ai(messages, config)
                if apply_directly:
                    # Apply directly to document
                    global _current_response
                    _current_response = response
                    self._apply_to_doc()
                    self._set_status(f"{action} applied!")
                else:
                    self._set_status(f"{action} complete")
                    self._set_output(f"--- {action} ---\n\n{response}")
            except Exception as e:
                self._set_status("Error")
                self._set_output(f"Error: {str(e)}")

        thread = threading.Thread(target=do_call, daemon=True)
        thread.start()

    def _apply_to_doc(self):
        """Replace selection with AI response."""
        global _current_response
        if not _current_response:
            self._set_status("No response to apply")
            return

        try:
            smgr = self.ctx.ServiceManager
            desktop = smgr.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.ctx)
            doc = desktop.getCurrentComponent()
            if doc:
                sel = doc.getCurrentController().getSelection()
                if sel and hasattr(sel, 'setString'):
                    sel.setString(_current_response)
                    self._set_status("Applied to document!")
                elif sel and hasattr(sel, 'getByIndex'):
                    for i in range(sel.getCount()):
                        p = sel.getByIndex(i)
                        if hasattr(p, 'setString'):
                            p.setString(_current_response)
                            break
                    self._set_status("Applied to document!")
        except Exception as e:
            self._set_status(f"Apply failed: {str(e)}")

    def _copy_response(self):
        """Copy response to clipboard."""
        global _current_response
        if _current_response:
            self._set_status("Copied! (Use Cmd/Ctrl+V to paste)")

    def _open_settings(self):
        """Open settings dialog."""
        try:
            smgr = self.ctx.ServiceManager
            desktop = smgr.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.ctx)
            doc = desktop.getCurrentComponent()
            if doc:
                frame = doc.getCurrentController().getFrame()
                dispatcher = smgr.createInstanceWithContext(
                    "com.sun.star.frame.DispatchHelper", self.ctx)
                dispatcher.executeDispatch(frame, ".uno:OptionsTreeDialog", "", 0, ())
        except:
            pass

    def actionPerformed(self, event):
        """Handle button clicks."""
        try:
            btn = event.Source.getModel().Name
            log(f"Button clicked: {btn}")

            text = self._get_selection()

            if btn == "btnAsk":
                # Use input field text if no selection
                input_text = self._get_input()
                if input_text:
                    self._run_ai("Ask", input_text)
                    self._clear_input()
                elif text:
                    self._run_ai("Ask", text)
                else:
                    self._set_status("Type a question or select text")
                    self._set_output("Enter your question in the input field below, or select text in your document.")

            elif btn == "btnSend":
                input_text = self._get_input()
                if input_text:
                    combined = f"{input_text}\n\nSelected text:\n{text}" if text else input_text
                    self._run_ai("Ask", combined)
                    self._clear_input()
                else:
                    self._set_status("Enter a message")

            elif btn in ["btnBullets", "btnContinue", "btnImprove", "btnTone"]:
                # These actions apply directly to the document
                action = btn.replace("btn", "")
                self._run_ai(action, text, apply_directly=True)

            elif btn in ["btnProofread", "btnSummarize", "btnTranslate", "btnExplain"]:
                # These actions show results in output panel
                action = btn.replace("btn", "")
                self._run_ai(action, text)

            elif btn == "btnApply":
                self._apply_to_doc()

            elif btn == "btnCopy":
                self._copy_response()

            elif btn == "btnClear":
                self._set_output("")
                self._clear_input()
                self._set_status("Ready - select text and click an action")

            elif btn == "btnSettings":
                self._open_settings()

        except Exception as e:
            log(f"Button error: {e}\n{traceback.format_exc()}")

    def disposing(self, event):
        pass


class ToolPanel(unohelper.Base, XToolPanel, XSidebarPanel):
    """The sidebar panel implementation."""

    def __init__(self, window, ctx):
        self.ctx = ctx
        self.Window = window
        self.PanelWindow = window
        log("ToolPanel created")

    def createAccessible(self, parent):
        return self.Window

    def getHeightForWidth(self, width):
        """Return panel height for given width (compact sizing)."""
        log(f"getHeightForWidth: {width}")
        ls = uno.createUnoStruct("com.sun.star.ui.LayoutSize")
        ls.Minimum = 280   # Compact minimum
        ls.Maximum = 500   # Reasonable max
        ls.Preferred = 310 # Match XDL height
        return ls

    def getMinimalWidth(self):
        return 170  # Match XDL width


class Panel(unohelper.Base, XUIElement):
    """UIElement wrapper for the sidebar panel."""

    def __init__(self, ctx, frame, parent, url):
        self.ctx = ctx
        self.parent = parent
        self.panel = None
        self.window = None
        self.Frame = frame
        self.ResourceURL = url
        self.Type = unoTOOLPANEL
        self.Window = None
        log("Panel created")

    def getRealInterface(self):
        global _panel_window
        log("getRealInterface called")

        if not self.panel:
            self.window = self._create_window()
            if self.window:
                self.panel = ToolPanel(self.window, self.ctx)
                self.Window = self.window
                _panel_window = self.window
                self._setup_handlers()
                self._init_ui()
                log("Panel fully initialized")

        return self.panel

    def _create_window(self):
        """Create panel window from XDL."""
        log("Creating window from XDL")
        try:
            # Get extension path
            pip = self.ctx.getValueByName(
                "/singletons/com.sun.star.deployment.PackageInformationProvider")
            ext_path = pip.getPackageLocation(EXT_ID)
            xdl_url = f"{ext_path}/{XDL_PATH}"
            log(f"XDL URL: {xdl_url}")

            # Create window from XDL
            smgr = self.ctx.ServiceManager
            provider = smgr.createInstanceWithContext(
                "com.sun.star.awt.ContainerWindowProvider", self.ctx)

            window = provider.createContainerWindow(
                xdl_url, "", self.parent, None)

            if window:
                window.setVisible(True)
                log("Window created and visible")

            return window
        except Exception as e:
            log(f"Window creation error: {e}\n{traceback.format_exc()}")
            return None

    def _setup_handlers(self):
        """Setup button click handlers."""
        log("Setting up handlers")
        if not self.window:
            return

        try:
            listener = PanelActions(self.ctx, self.window)

            buttons = [
                "btnAsk", "btnImprove", "btnProofread", "btnSummarize",
                "btnTranslate", "btnExplain", "btnBullets", "btnContinue",
                "btnTone", "btnSend", "btnClear", "btnApply", "btnCopy",
                "btnSettings"
            ]

            for name in buttons:
                try:
                    btn = self.window.getControl(name)
                    if btn:
                        btn.addActionListener(listener)
                        log(f"Handler added: {name}")
                except Exception as e:
                    log(f"Handler error for {name}: {e}")
        except Exception as e:
            log(f"Setup handlers error: {e}")

    def _init_ui(self):
        """Initialize UI state."""
        log("Initializing UI")
        try:
            # Set model label
            config = load_config()
            model_ctrl = self.window.getControl("lblModel")
            if model_ctrl:
                model_ctrl.setText(config.get("model", "llama-3.3-70b"))

            # Set status
            status_ctrl = self.window.getControl("lblStatus")
            if status_ctrl:
                if config.get("api_key"):
                    status_ctrl.setText("Ready - select text and click an action")
                else:
                    status_ctrl.setText("Configure API key in Settings")

            # Welcome message
            output_ctrl = self.window.getControl("txtOutput")
            if output_ctrl:
                output_ctrl.setText(
                    "Welcome to PrePanda AI!\n\n"
                    "Quick actions:\n"
                    "- Select text and click a button above\n"
                    "- Or type a question below and click Send\n\n"
                    "All responses appear here."
                )

            log("UI initialized")
        except Exception as e:
            log(f"Init UI error: {e}")


class PanelFactory(unohelper.Base, XUIElementFactory):
    """Factory that creates PrePanda sidebar panels."""

    def __init__(self, ctx):
        self.ctx = ctx
        log("PanelFactory created")

    def createUIElement(self, url, props):
        log(f"createUIElement: {url}")

        frame = None
        parent = None

        for p in props:
            if p.Name == "Frame":
                frame = p.Value
            elif p.Name == "ParentWindow":
                parent = p.Value

        if frame and parent:
            try:
                panel = Panel(self.ctx, frame, parent, url)
                # Initialize immediately
                panel.getRealInterface()
                return panel
            except Exception as e:
                log(f"Factory error: {e}\n{traceback.format_exc()}")

        return None


# UNO registration
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(PanelFactory, IMPL_NAME, SERVICES)

log("=== PrePanda Panel Module Loaded ===")
