# -*- coding: utf-8 -*-
"""
PreOffice - Search with Presearch Integration
License: MIT
"""

import webbrowser
import urllib.parse
from typing import Optional

# Default configuration
DEFAULT_SEARCH_URL = "https://presearch.com/search"
DEFAULT_PARAMS = {"utm_source": "preoffice"}


class PresearchSearch:
    """Integration for searching with Presearch."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the Presearch Search integration.

        Args:
            base_url: Custom search URL (for gov/enterprise deployments)
        """
        self.base_url = base_url or DEFAULT_SEARCH_URL
        self.enabled = True

    def search(self, query: str, open_browser: bool = True) -> str:
        """
        Search with Presearch.

        Args:
            query: The search query
            open_browser: Whether to open the browser automatically

        Returns:
            The full search URL
        """
        if not self.enabled:
            raise RuntimeError("Search integration is disabled (air-gapped mode)")

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        params = {"q": query.strip(), **DEFAULT_PARAMS}
        url = f"{self.base_url}?{urllib.parse.urlencode(params)}"

        if open_browser:
            webbrowser.open(url)

        return url

    def disable(self):
        """Disable the integration (for air-gapped mode)."""
        self.enabled = False

    def enable(self):
        """Enable the integration."""
        self.enabled = True

    def set_base_url(self, url: str):
        """Set custom base URL for enterprise deployments."""
        self.base_url = url


# LibreOffice UNO integration
def SearchWithPresearch(*args):
    """UNO entry point for Search with Presearch."""
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
            search = PresearchSearch()
            search.search(text)
        else:
            _show_message("Search with Presearch", "Please select some text first.")
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


g_exportedScripts = (SearchWithPresearch,)
