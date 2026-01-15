# -*- coding: utf-8 -*-
"""
PreOffice Tools - LibreOffice Extension by Presearch
"""

import webbrowser
import urllib.parse


def SearchWithPresearch(*args):
    """Search selected text with Presearch."""
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
            url = "https://presearch.com/search?q=" + urllib.parse.quote_plus(text.strip())
            webbrowser.open(url)
        else:
            _show_msg("Search with Presearch", "Please select some text first.")
    except Exception as e:
        _show_msg("Error", str(e))


def AskPreGPT(*args):
    """Ask PreGPT about selected text."""
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
            url = "https://pregpt.presearch.com/?q=" + urllib.parse.quote_plus(text.strip())
            webbrowser.open(url)
        else:
            _show_msg("Ask PreGPT", "Please select some text first.")
    except Exception as e:
        _show_msg("Error", str(e))


def PrivacyCheck(*args):
    """Scan document for privacy-sensitive metadata."""
    try:
        import uno
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.getCurrentComponent()

        if not doc:
            _show_msg("Privacy Check", "No document open.")
            return

        findings = []

        if hasattr(doc, 'getDocumentProperties'):
            props = doc.getDocumentProperties()
            if props.Author:
                findings.append("Author: " + props.Author)
            if props.ModifiedBy:
                findings.append("Modified by: " + props.ModifiedBy)
            if props.Subject:
                findings.append("Subject: " + props.Subject)

        if findings:
            msg = "Found metadata:\n\n" + "\n".join("- " + f for f in findings)
        else:
            msg = "No sensitive metadata found!"

        _show_msg("Privacy Check", msg)
    except Exception as e:
        _show_msg("Error", str(e))


def ExportToPreStorage(*args):
    """Export to PDF."""
    _show_msg("Export to PreStorage", "Use File > Export as PDF\n\nCloud upload coming soon!")


def _show_msg(title, msg):
    """Show message box."""
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


g_exportedScripts = (SearchWithPresearch, AskPreGPT, PrivacyCheck, ExportToPreStorage,)
