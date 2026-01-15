#!/usr/bin/env python3
"""
PrePanda LibreOffice Extension
Integrates PrePanda AI Assistant into LibreOffice/PreOffice

This extension adds:
- PrePanda sidebar panel
- Context menu integration
- Keyboard shortcuts
- Toolbar buttons
"""

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.awt import WindowDescriptor, Rectangle
from com.sun.star.awt.WindowClass import SIMPLE
from com.sun.star.task import XJobExecutor

# Try to import the service
try:
    from prepanda_service import PrePandaService, PrePandaConfig
except ImportError:
    PrePandaService = None


class PrePandaExtension:
    """
    Main extension class for PrePanda integration
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.smgr = ctx.ServiceManager
        self.desktop = self.smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx
        )
        self.service = PrePandaService() if PrePandaService else None

    def get_selected_text(self):
        """Get currently selected text from the active document"""
        try:
            doc = self.desktop.getCurrentComponent()
            if not doc:
                return ""

            controller = doc.getCurrentController()
            if not controller:
                return ""

            selection = controller.getSelection()
            if not selection:
                return ""

            # Handle different selection types
            if hasattr(selection, "getString"):
                return selection.getString()
            elif hasattr(selection, "getCount"):
                # Multiple selections
                texts = []
                for i in range(selection.getCount()):
                    item = selection.getByIndex(i)
                    if hasattr(item, "getString"):
                        texts.append(item.getString())
                return "\n".join(texts)

            return ""
        except Exception as e:
            print(f"Error getting selection: {e}")
            return ""

    def replace_selected_text(self, new_text):
        """Replace the selected text with new text"""
        try:
            doc = self.desktop.getCurrentComponent()
            if not doc:
                return False

            controller = doc.getCurrentController()
            if not controller:
                return False

            selection = controller.getSelection()
            if not selection:
                return False

            if hasattr(selection, "setString"):
                selection.setString(new_text)
                return True

            return False
        except Exception as e:
            print(f"Error replacing text: {e}")
            return False

    def show_message(self, message, title="PrePanda"):
        """Show a message dialog"""
        try:
            toolkit = self.smgr.createInstanceWithContext(
                "com.sun.star.awt.Toolkit", self.ctx
            )
            parent = self.desktop.getCurrentFrame().getContainerWindow()

            msgbox = toolkit.createMessageBox(
                parent,
                1,  # MESSAGEBOX
                1,  # BUTTONS_OK
                title,
                message
            )
            msgbox.execute()
        except Exception as e:
            print(f"Error showing message: {e}")

    def ask_prepanda(self, question=None):
        """Open PrePanda dialog with optional question"""
        if not self.service:
            self.show_message(
                "PrePanda service not available. Please check your installation.",
                "PrePanda Error"
            )
            return

        selected_text = self.get_selected_text()

        if not question:
            # Show input dialog
            question = self._get_input("Ask PrePanda", "What would you like to know?")

        if question:
            try:
                response = self.service.ask(question, context=selected_text)
                self.show_message(response, "PrePanda Response")
            except Exception as e:
                self.show_message(f"Error: {e}", "PrePanda Error")

    def summarize_selection(self):
        """Summarize selected text"""
        self._perform_action("summarize")

    def improve_selection(self):
        """Improve selected text"""
        self._perform_action("improve", replace=True)

    def translate_selection(self, language="English"):
        """Translate selected text"""
        self._perform_action("translate", language=language, replace=True)

    def explain_selection(self):
        """Explain selected text"""
        self._perform_action("explain")

    def proofread_selection(self):
        """Proofread selected text"""
        self._perform_action("proofread", replace=True)

    def _perform_action(self, action, replace=False, language="English"):
        """Perform an action on selected text"""
        if not self.service:
            self.show_message("PrePanda service not available.")
            return

        selected_text = self.get_selected_text()
        if not selected_text:
            self.show_message("Please select some text first.")
            return

        try:
            if action == "translate":
                result = self.service.translate(selected_text, language)
            else:
                result = self.service.perform_action(action, selected_text)

            if replace:
                self.replace_selected_text(result)
            else:
                self.show_message(result, f"PrePanda - {action.title()}")

        except Exception as e:
            self.show_message(f"Error: {e}", "PrePanda Error")

    def _get_input(self, title, prompt):
        """Show input dialog and return user input"""
        try:
            # Simple implementation using a message box
            # In a full implementation, this would be a proper input dialog
            return None  # Placeholder
        except Exception:
            return None


# UNO component implementation
class PrePandaSummarize(unohelper.Base, XJobExecutor):
    """Job executor for summarize action"""

    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, args):
        ext = PrePandaExtension(self.ctx)
        ext.summarize_selection()


class PrePandaImprove(unohelper.Base, XJobExecutor):
    """Job executor for improve action"""

    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, args):
        ext = PrePandaExtension(self.ctx)
        ext.improve_selection()


class PrePandaTranslate(unohelper.Base, XJobExecutor):
    """Job executor for translate action"""

    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, args):
        ext = PrePandaExtension(self.ctx)
        ext.translate_selection()


class PrePandaExplain(unohelper.Base, XJobExecutor):
    """Job executor for explain action"""

    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, args):
        ext = PrePandaExtension(self.ctx)
        ext.explain_selection()


class PrePandaProofread(unohelper.Base, XJobExecutor):
    """Job executor for proofread action"""

    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, args):
        ext = PrePandaExtension(self.ctx)
        ext.proofread_selection()


class PrePandaAsk(unohelper.Base, XJobExecutor):
    """Job executor for ask action"""

    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, args):
        ext = PrePandaExtension(self.ctx)
        ext.ask_prepanda()


# Component registration
try:
    import unohelper

    g_ImplementationHelper = unohelper.ImplementationHelper()

    g_ImplementationHelper.addImplementation(
        PrePandaSummarize,
        "com.presearch.prepanda.Summarize",
        ("com.sun.star.task.Job",),
    )

    g_ImplementationHelper.addImplementation(
        PrePandaImprove,
        "com.presearch.prepanda.Improve",
        ("com.sun.star.task.Job",),
    )

    g_ImplementationHelper.addImplementation(
        PrePandaTranslate,
        "com.presearch.prepanda.Translate",
        ("com.sun.star.task.Job",),
    )

    g_ImplementationHelper.addImplementation(
        PrePandaExplain,
        "com.presearch.prepanda.Explain",
        ("com.sun.star.task.Job",),
    )

    g_ImplementationHelper.addImplementation(
        PrePandaProofread,
        "com.presearch.prepanda.Proofread",
        ("com.sun.star.task.Job",),
    )

    g_ImplementationHelper.addImplementation(
        PrePandaAsk,
        "com.presearch.prepanda.Ask",
        ("com.sun.star.task.Job",),
    )

except ImportError:
    # Not running in LibreOffice context
    pass


# CLI for testing outside LibreOffice
if __name__ == "__main__":
    print("PrePanda Extension - Test Mode")
    print("This module is designed to run within LibreOffice.")
    print("\nAvailable actions:")
    print("  - Summarize: Summarize selected text")
    print("  - Improve: Improve text quality")
    print("  - Translate: Translate to another language")
    print("  - Explain: Explain text in simple terms")
    print("  - Proofread: Check grammar and spelling")
    print("  - Ask: Ask any question")
