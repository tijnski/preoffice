# -*- coding: utf-8 -*-
"""
PreOffice - PreStorage Integration
License: MIT
"""

from typing import Optional, Dict, Any
from enum import Enum
import os


class StorageBackend(Enum):
    """Supported storage backends."""
    PRESTORAGE = "prestorage"  # Presearch cloud storage
    WEBDAV = "webdav"          # WebDAV server
    S3 = "s3"                  # S3-compatible storage
    LOCAL = "local"            # Local filesystem only


class PreStorage:
    """Integration for PreStorage document export/upload."""

    def __init__(self, backend: StorageBackend = StorageBackend.PRESTORAGE,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize PreStorage integration.

        Args:
            backend: Storage backend type
            config: Backend-specific configuration
        """
        self.backend = backend
        self.config = config or {}
        self._enabled = backend != StorageBackend.LOCAL

    @property
    def enabled(self) -> bool:
        """Check if cloud upload is enabled."""
        return self._enabled and self.backend != StorageBackend.LOCAL

    def export_pdf(self, document, output_path: str) -> str:
        """
        Export document to PDF.

        Args:
            document: LibreOffice document object
            output_path: Where to save the PDF

        Returns:
            Path to the exported PDF
        """
        # This is a stub - actual implementation requires UNO API
        # In real implementation, use document.storeToURL() with PDF filter
        return output_path

    def upload(self, file_path: str, remote_path: Optional[str] = None) -> str:
        """
        Upload file to PreStorage.

        Args:
            file_path: Local file path
            remote_path: Remote destination path

        Returns:
            URL or path of uploaded file
        """
        if not self.enabled:
            raise RuntimeError("Upload disabled (offline mode)")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Stub - actual implementation depends on backend
        if self.backend == StorageBackend.PRESTORAGE:
            return self._upload_prestorage(file_path, remote_path)
        elif self.backend == StorageBackend.WEBDAV:
            return self._upload_webdav(file_path, remote_path)
        elif self.backend == StorageBackend.S3:
            return self._upload_s3(file_path, remote_path)

        raise ValueError(f"Unsupported backend: {self.backend}")

    def _upload_prestorage(self, file_path: str, remote_path: Optional[str]) -> str:
        """Upload to PreStorage cloud."""
        # Stub - implement with PreStorage API
        raise NotImplementedError("PreStorage API integration pending")

    def _upload_webdav(self, file_path: str, remote_path: Optional[str]) -> str:
        """Upload via WebDAV."""
        # Stub - implement with WebDAV client
        raise NotImplementedError("WebDAV integration pending")

    def _upload_s3(self, file_path: str, remote_path: Optional[str]) -> str:
        """Upload to S3-compatible storage."""
        # Stub - implement with boto3 or similar
        raise NotImplementedError("S3 integration pending")

    def disable(self):
        """Disable cloud uploads (offline mode)."""
        self._enabled = False

    def enable(self):
        """Enable cloud uploads."""
        self._enabled = True


# LibreOffice UNO integration
def ExportToPreStorage(*args):
    """UNO entry point for Export to PreStorage."""
    _show_message(
        "Export to PreStorage",
        "To export your document:\n\n"
        "1. Use File > Export as PDF\n"
        "2. Save the PDF locally\n\n"
        "Cloud upload feature coming soon!\n\n"
        "For now, you can manually upload to prestorage.com"
    )


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


g_exportedScripts = (ExportToPreStorage,)
