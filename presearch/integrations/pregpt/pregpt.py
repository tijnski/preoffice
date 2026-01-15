# -*- coding: utf-8 -*-
"""
PreOffice - PreGPT Integration
License: MIT
"""

import webbrowser
import urllib.parse
from typing import Optional
from enum import Enum


class DeploymentMode(Enum):
    """PreGPT deployment modes."""
    CLOUD = "cloud"           # Presearch cloud
    SOVEREIGN = "sovereign"   # Sovereign cloud deployment
    LOCAL = "local"           # On-premises/local
    DISABLED = "disabled"     # Air-gapped mode


# Default endpoints
ENDPOINTS = {
    DeploymentMode.CLOUD: "https://pregpt.presearch.com",
    DeploymentMode.SOVEREIGN: None,  # Configured per deployment
    DeploymentMode.LOCAL: "http://localhost:8080",
}


class PreGPT:
    """Integration for PreGPT AI assistant."""

    def __init__(self, mode: DeploymentMode = DeploymentMode.CLOUD,
                 custom_endpoint: Optional[str] = None):
        """
        Initialize PreGPT integration.

        Args:
            mode: Deployment mode
            custom_endpoint: Custom endpoint URL (for sovereign/local)
        """
        self.mode = mode
        self.custom_endpoint = custom_endpoint

    @property
    def endpoint(self) -> Optional[str]:
        """Get the current endpoint URL."""
        if self.mode == DeploymentMode.DISABLED:
            return None
        if self.custom_endpoint:
            return self.custom_endpoint
        return ENDPOINTS.get(self.mode)

    @property
    def enabled(self) -> bool:
        """Check if PreGPT is enabled."""
        return self.mode != DeploymentMode.DISABLED and self.endpoint is not None

    def ask(self, query: str, open_browser: bool = True) -> Optional[str]:
        """
        Ask PreGPT a question.

        Args:
            query: The question or prompt
            open_browser: Whether to open browser automatically

        Returns:
            The full URL, or None if disabled
        """
        if not self.enabled:
            raise RuntimeError("PreGPT is disabled (air-gapped mode or no endpoint configured)")

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        params = {"q": query.strip(), "source": "preoffice"}
        url = f"{self.endpoint}?{urllib.parse.urlencode(params)}"

        if open_browser:
            webbrowser.open(url)

        return url

    def set_mode(self, mode: DeploymentMode, endpoint: Optional[str] = None):
        """
        Change deployment mode.

        Args:
            mode: New deployment mode
            endpoint: Custom endpoint (required for SOVEREIGN mode)
        """
        self.mode = mode
        if endpoint:
            self.custom_endpoint = endpoint
        elif mode == DeploymentMode.SOVEREIGN and not self.custom_endpoint:
            raise ValueError("Sovereign mode requires a custom endpoint")

    def disable(self):
        """Disable PreGPT (air-gapped mode)."""
        self.mode = DeploymentMode.DISABLED


# LibreOffice UNO integration
def AskPreGPT(*args):
    """UNO entry point for Ask PreGPT."""
    try:
        import uno
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.getCurrentComponent()

        text = ""
        if doc:
            controller = doc.getCurrentController()
            sel = controller.getSelection()
            if sel and hasattr(sel, 'getString'):
                text = sel.getString()

        if text.strip():
            pregpt = PreGPT()
            pregpt.ask(text)
        else:
            _show_message("Ask PreGPT", "Please select some text first.")
    except Exception as e:
        _show_message("Error", str(e))


def _show_message(title: str, msg: str):
    """Show a message box in LibreOffice."""
    try:
        import uno
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        frame = desktop.getCurrentFrame()
        win = frame.getContainerWindow()
        box = toolkit.createMessageBox(win, 0, 1, title, msg)
        box.execute()
    except:
        pass


g_exportedScripts = (AskPreGPT,)
