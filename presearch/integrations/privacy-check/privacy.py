# -*- coding: utf-8 -*-
"""
PreOffice - Privacy Check Integration
License: MIT
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class PrivacyRisk(Enum):
    """Privacy risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class PrivacyFinding:
    """A privacy-related finding in a document."""
    category: str
    description: str
    risk: PrivacyRisk
    location: Optional[str] = None
    can_clean: bool = False


class PrivacyChecker:
    """Check documents for privacy-sensitive content."""

    def __init__(self):
        self.findings: List[PrivacyFinding] = []

    def check_document(self, document) -> List[PrivacyFinding]:
        """
        Perform a comprehensive privacy check on a document.

        Args:
            document: LibreOffice document object

        Returns:
            List of privacy findings
        """
        self.findings = []

        if document is None:
            return self.findings

        # Check document properties/metadata
        self._check_metadata(document)

        # Check for tracked changes
        self._check_tracked_changes(document)

        # Check for comments
        self._check_comments(document)

        # Check for hidden text (Writer only)
        self._check_hidden_text(document)

        # Check for embedded links
        self._check_links(document)

        return self.findings

    def _check_metadata(self, document):
        """Check document metadata for privacy issues."""
        try:
            if hasattr(document, 'getDocumentProperties'):
                props = document.getDocumentProperties()

                if props.Author:
                    self.findings.append(PrivacyFinding(
                        category="Metadata",
                        description=f"Author: {props.Author}",
                        risk=PrivacyRisk.MEDIUM,
                        can_clean=True
                    ))

                if props.ModifiedBy:
                    self.findings.append(PrivacyFinding(
                        category="Metadata",
                        description=f"Last modified by: {props.ModifiedBy}",
                        risk=PrivacyRisk.MEDIUM,
                        can_clean=True
                    ))

                if props.Subject:
                    self.findings.append(PrivacyFinding(
                        category="Metadata",
                        description=f"Subject: {props.Subject}",
                        risk=PrivacyRisk.LOW,
                        can_clean=True
                    ))

                if props.Keywords:
                    self.findings.append(PrivacyFinding(
                        category="Metadata",
                        description=f"Keywords present",
                        risk=PrivacyRisk.LOW,
                        can_clean=True
                    ))
        except Exception:
            pass

    def _check_tracked_changes(self, document):
        """Check for tracked changes/revisions."""
        try:
            if hasattr(document, 'getRedlines'):
                redlines = document.getRedlines()
                if redlines and redlines.getCount() > 0:
                    self.findings.append(PrivacyFinding(
                        category="Tracked Changes",
                        description=f"{redlines.getCount()} tracked changes found",
                        risk=PrivacyRisk.HIGH,
                        can_clean=True
                    ))
        except Exception:
            pass

    def _check_comments(self, document):
        """Check for comments/annotations."""
        try:
            if hasattr(document, 'getTextFields'):
                fields = document.getTextFields()
                enum = fields.createEnumeration()
                comment_count = 0
                while enum.hasMoreElements():
                    field = enum.nextElement()
                    if hasattr(field, 'supportsService'):
                        if field.supportsService("com.sun.star.text.TextField.Annotation"):
                            comment_count += 1

                if comment_count > 0:
                    self.findings.append(PrivacyFinding(
                        category="Comments",
                        description=f"{comment_count} comments found",
                        risk=PrivacyRisk.MEDIUM,
                        can_clean=True
                    ))
        except Exception:
            pass

    def _check_hidden_text(self, document):
        """Check for hidden text sections."""
        try:
            if hasattr(document, 'getTextSections'):
                sections = document.getTextSections()
                hidden_count = 0
                for i in range(sections.getCount()):
                    section = sections.getByIndex(i)
                    if hasattr(section, 'IsVisible') and not section.IsVisible:
                        hidden_count += 1

                if hidden_count > 0:
                    self.findings.append(PrivacyFinding(
                        category="Hidden Content",
                        description=f"{hidden_count} hidden sections found",
                        risk=PrivacyRisk.HIGH,
                        can_clean=True
                    ))
        except Exception:
            pass

    def _check_links(self, document):
        """Check for embedded links."""
        try:
            if hasattr(document, 'getLinks'):
                links = document.getLinks()
                if links and links.getCount() > 0:
                    self.findings.append(PrivacyFinding(
                        category="Embedded Links",
                        description=f"{links.getCount()} embedded links found",
                        risk=PrivacyRisk.LOW,
                        can_clean=False
                    ))
        except Exception:
            pass

    def get_report(self) -> str:
        """Generate a human-readable privacy report."""
        if not self.findings:
            return "No privacy issues found."

        lines = ["Privacy Check Report", "=" * 40, ""]

        # Group by risk level
        high = [f for f in self.findings if f.risk == PrivacyRisk.HIGH]
        medium = [f for f in self.findings if f.risk == PrivacyRisk.MEDIUM]
        low = [f for f in self.findings if f.risk == PrivacyRisk.LOW]

        if high:
            lines.append("HIGH RISK:")
            for f in high:
                lines.append(f"  - [{f.category}] {f.description}")
            lines.append("")

        if medium:
            lines.append("MEDIUM RISK:")
            for f in medium:
                lines.append(f"  - [{f.category}] {f.description}")
            lines.append("")

        if low:
            lines.append("LOW RISK:")
            for f in low:
                lines.append(f"  - [{f.category}] {f.description}")
            lines.append("")

        cleanable = [f for f in self.findings if f.can_clean]
        if cleanable:
            lines.append(f"({len(cleanable)} items can be cleaned)")

        return "\n".join(lines)


# LibreOffice UNO integration
def PrivacyCheck(*args):
    """UNO entry point for Privacy Check."""
    try:
        import uno
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.getCurrentComponent()

        if not doc:
            _show_message("Privacy Check", "No document open.")
            return

        checker = PrivacyChecker()
        checker.check_document(doc)
        report = checker.get_report()

        _show_message("Privacy Check", report)

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


g_exportedScripts = (PrivacyCheck,)
