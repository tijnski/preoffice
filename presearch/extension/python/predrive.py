#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PreDrive Cloud Storage Integration for PreOffice
Upload documents to PreDrive cloud storage (https://predrive.eu)

Copyright (c) 2024 Presearch
Licensed under MIT License
"""

import uno
import unohelper
from com.sun.star.task import XJobExecutor
from com.sun.star.lang import XServiceInfo
from com.sun.star.beans import PropertyValue

import os
import json
import urllib.request
import urllib.error
import ssl
import tempfile
import base64

# Extension identifier
EXTENSION_ID = "com.presearch.preoffice"

# Configuration
CONFIG_FILE = "predrive_config.json"
DEFAULT_API_URL = "https://predrive.eu/api"


def get_config_path():
    """Get the path to the configuration file."""
    ctx = uno.getComponentContext()
    path_sub = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.util.PathSubstitution", ctx)
    user_url = path_sub.substituteVariables("$(user)", True)
    user_path = uno.fileUrlToSystemPath(user_url)
    return os.path.join(user_path, CONFIG_FILE)


def load_config():
    """Load configuration from file."""
    config_path = get_config_path()
    default_config = {
        "api_url": DEFAULT_API_URL,
        "api_key": "",
        "default_folder": "/",
        "auto_convert_pdf": False,
        "enabled": True
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


def show_message(ctx, message, title="PreDrive"):
    """Show a message dialog."""
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    frame = desktop.getCurrentFrame()
    if frame:
        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
        parent_win = frame.getContainerWindow()
        msgbox = toolkit.createMessageBox(
            parent_win, 1, 1, title, message)
        msgbox.execute()


def show_error(ctx, message, title="PreDrive Error"):
    """Show an error dialog."""
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    frame = desktop.getCurrentFrame()
    if frame:
        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
        parent_win = frame.getContainerWindow()
        msgbox = toolkit.createMessageBox(
            parent_win, 0, 1, title, message)
        msgbox.execute()


def export_to_pdf(doc, ctx):
    """Export document to PDF and return the file path."""
    try:
        # Create temporary file for PDF
        temp_dir = tempfile.gettempdir()
        doc_title = doc.getTitle() or "document"
        # Remove extension if present
        if "." in doc_title:
            doc_title = doc_title.rsplit(".", 1)[0]
        pdf_path = os.path.join(temp_dir, f"{doc_title}.pdf")
        pdf_url = uno.systemPathToFileUrl(pdf_path)

        # Export properties
        props = (
            PropertyValue("FilterName", 0, "writer_pdf_Export", 0),
            PropertyValue("Overwrite", 0, True, 0),
        )

        # Try different filter names based on document type
        doc_type = doc.getImplementationName()
        if "SpreadsheetDocument" in doc_type:
            props = (
                PropertyValue("FilterName", 0, "calc_pdf_Export", 0),
                PropertyValue("Overwrite", 0, True, 0),
            )
        elif "PresentationDocument" in doc_type or "DrawingDocument" in doc_type:
            props = (
                PropertyValue("FilterName", 0, "impress_pdf_Export", 0),
                PropertyValue("Overwrite", 0, True, 0),
            )

        doc.storeToURL(pdf_url, props)
        return pdf_path
    except Exception as e:
        raise Exception(f"Failed to export PDF: {str(e)}")


def export_to_odf(doc, ctx):
    """Export document to ODF format and return the file path."""
    try:
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        doc_title = doc.getTitle() or "document"

        # Determine file extension based on document type
        doc_type = doc.getImplementationName()
        if "SpreadsheetDocument" in doc_type:
            ext = ".ods"
            filter_name = "calc8"
        elif "PresentationDocument" in doc_type:
            ext = ".odp"
            filter_name = "impress8"
        elif "DrawingDocument" in doc_type:
            ext = ".odg"
            filter_name = "draw8"
        else:
            ext = ".odt"
            filter_name = "writer8"

        # Remove existing extension if present
        if "." in doc_title:
            doc_title = doc_title.rsplit(".", 1)[0]

        odf_path = os.path.join(temp_dir, f"{doc_title}{ext}")
        odf_url = uno.systemPathToFileUrl(odf_path)

        props = (
            PropertyValue("FilterName", 0, filter_name, 0),
            PropertyValue("Overwrite", 0, True, 0),
        )

        doc.storeToURL(odf_url, props)
        return odf_path
    except Exception as e:
        raise Exception(f"Failed to export ODF: {str(e)}")


def upload_to_predrive(file_path, config, folder="/"):
    """Upload a file to PreDrive cloud storage."""
    api_url = config.get("api_url", DEFAULT_API_URL)
    api_key = config.get("api_key", "")

    if not api_key:
        raise Exception("PreDrive API key not configured. Please set your API key in PreDrive Settings.")

    # Read file content
    with open(file_path, 'rb') as f:
        file_content = f.read()

    file_name = os.path.basename(file_path)
    file_base64 = base64.b64encode(file_content).decode('utf-8')

    # Prepare upload request
    upload_data = {
        "file": {
            "name": file_name,
            "content": file_base64,
            "encoding": "base64"
        },
        "folder": folder
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "PreOffice/1.0"
    }

    data = json.dumps(upload_data).encode('utf-8')

    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            f"{api_url}/upload",
            data=data,
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, context=ctx, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result

    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode('utf-8')
        except:
            pass
        raise Exception(f"Upload failed: {e.code} - {e.reason}. {error_body}")
    except urllib.error.URLError as e:
        raise Exception(f"Connection failed: {e.reason}")
    except Exception as e:
        raise Exception(f"Upload error: {str(e)}")


def list_predrive_folders(config):
    """List folders from PreDrive."""
    api_url = config.get("api_url", DEFAULT_API_URL)
    api_key = config.get("api_key", "")

    if not api_key:
        return []

    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "PreOffice/1.0"
    }

    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            f"{api_url}/folders",
            headers=headers,
            method='GET'
        )

        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("folders", [])

    except Exception:
        return []


# =============================================================================
# Job Executor Services
# =============================================================================

class UploadPDFJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Upload current document as PDF to PreDrive."""

    IMPLEMENTATION_NAME = "com.presearch.predrive.UploadPDF"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return UploadPDFJob(ctx)

    def trigger(self, args):
        config = load_config()

        if not config.get("enabled", True):
            show_message(self.ctx, "PreDrive integration is disabled. Enable it in PreDrive Settings.")
            return

        smgr = self.ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()

        if not doc:
            show_error(self.ctx, "No document is open.")
            return

        try:
            # Export to PDF
            pdf_path = export_to_pdf(doc, self.ctx)

            # Upload to PreDrive
            folder = config.get("default_folder", "/")
            result = upload_to_predrive(pdf_path, config, folder)

            # Clean up temp file
            try:
                os.remove(pdf_path)
            except:
                pass

            # Show success message
            file_url = result.get("url", "")
            msg = f"Document uploaded successfully to PreDrive!\n\nFile: {os.path.basename(pdf_path)}"
            if file_url:
                msg += f"\nURL: {file_url}"
            show_message(self.ctx, msg, "Upload Complete")

        except Exception as e:
            show_error(self.ctx, str(e))

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


class UploadODFJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Upload current document as ODF to PreDrive."""

    IMPLEMENTATION_NAME = "com.presearch.predrive.UploadODF"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return UploadODFJob(ctx)

    def trigger(self, args):
        config = load_config()

        if not config.get("enabled", True):
            show_message(self.ctx, "PreDrive integration is disabled. Enable it in PreDrive Settings.")
            return

        smgr = self.ctx.ServiceManager
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()

        if not doc:
            show_error(self.ctx, "No document is open.")
            return

        try:
            # Export to ODF
            odf_path = export_to_odf(doc, self.ctx)

            # Upload to PreDrive
            folder = config.get("default_folder", "/")
            result = upload_to_predrive(odf_path, config, folder)

            # Clean up temp file
            try:
                os.remove(odf_path)
            except:
                pass

            # Show success message
            file_url = result.get("url", "")
            msg = f"Document uploaded successfully to PreDrive!\n\nFile: {os.path.basename(odf_path)}"
            if file_url:
                msg += f"\nURL: {file_url}"
            show_message(self.ctx, msg, "Upload Complete")

        except Exception as e:
            show_error(self.ctx, str(e))

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


class PreDriveSettingsJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Open PreDrive settings dialog."""

    IMPLEMENTATION_NAME = "com.presearch.predrive.Settings"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return PreDriveSettingsJob(ctx)

    def trigger(self, args):
        """Open the PreDrive settings by opening LibreOffice Options dialog."""
        smgr = self.ctx.ServiceManager
        dispatcher = smgr.createInstanceWithContext(
            "com.sun.star.frame.DispatchHelper", self.ctx)
        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        frame = desktop.getCurrentFrame()

        # Open the Options dialog
        dispatcher.executeDispatch(frame, ".uno:OptionsTreeDialog", "", 0, ())

    def getImplementationName(self):
        return self.IMPLEMENTATION_NAME

    def supportsService(self, name):
        return name in self.SERVICE_NAMES

    def getSupportedServiceNames(self):
        return self.SERVICE_NAMES


class OpenPreDriveJob(unohelper.Base, XJobExecutor, XServiceInfo):
    """Open PreDrive in browser."""

    IMPLEMENTATION_NAME = "com.presearch.predrive.Open"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def createInstance(ctx):
        return OpenPreDriveJob(ctx)

    def trigger(self, args):
        config = load_config()
        api_url = config.get("api_url", DEFAULT_API_URL)

        # Extract base URL (remove /api if present)
        base_url = api_url.replace("/api", "").rstrip("/")

        try:
            smgr = self.ctx.ServiceManager
            system_shell = smgr.createInstanceWithContext(
                "com.sun.star.system.SystemShellExecute", self.ctx)
            system_shell.execute(base_url, "", 0)
        except Exception as e:
            show_error(self.ctx, f"Could not open browser: {str(e)}")

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

class PreDriveOptionsHandler(unohelper.Base, XContainerWindowEventHandler, XServiceInfo):
    """Handler for the PreDrive options dialog in Preferences."""

    IMPLEMENTATION_NAME = "com.presearch.predrive.OptionsHandler"
    SERVICE_NAMES = (IMPLEMENTATION_NAME,)

    def __init__(self, ctx):
        self.ctx = ctx
        self.config = load_config()

    @staticmethod
    def createInstance(ctx):
        return PreDriveOptionsHandler(ctx)

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
        """Get a control from the window."""
        try:
            return window.getControl(name)
        except:
            return None

    def _loadSettings(self, window):
        """Load current settings into dialog controls."""
        try:
            self.config = load_config()

            # API URL
            url_field = self._getControl(window, "txtApiUrl")
            if url_field:
                url_field.setText(self.config.get("api_url", DEFAULT_API_URL))

            # API Key
            key_field = self._getControl(window, "txtApiKey")
            if key_field:
                key_field.setText(self.config.get("api_key", ""))

            # Default folder
            folder_field = self._getControl(window, "txtFolder")
            if folder_field:
                folder_field.setText(self.config.get("default_folder", "/"))

            # Enabled checkbox
            enabled_check = self._getControl(window, "chkEnabled")
            if enabled_check:
                enabled_check.setState(1 if self.config.get("enabled", True) else 0)

        except Exception as e:
            try:
                with open("/tmp/predrive_options_error.log", "a") as f:
                    f.write(f"Load error: {str(e)}\n")
            except:
                pass

    def _saveSettings(self, window):
        """Save dialog settings to config file."""
        try:
            self.config = load_config()

            # API URL
            url_field = self._getControl(window, "txtApiUrl")
            if url_field:
                text = url_field.getText()
                if text:
                    self.config["api_url"] = text

            # API Key
            key_field = self._getControl(window, "txtApiKey")
            if key_field:
                text = key_field.getText()
                if text is not None:
                    self.config["api_key"] = text

            # Default folder
            folder_field = self._getControl(window, "txtFolder")
            if folder_field:
                text = folder_field.getText()
                if text:
                    self.config["default_folder"] = text

            # Enabled checkbox
            enabled_check = self._getControl(window, "chkEnabled")
            if enabled_check:
                self.config["enabled"] = enabled_check.getState() == 1

            save_config(self.config)

        except Exception as e:
            try:
                with open("/tmp/predrive_options_error.log", "a") as f:
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
# UNO Component Registration
# =============================================================================

g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(
    UploadPDFJob.createInstance,
    UploadPDFJob.IMPLEMENTATION_NAME,
    UploadPDFJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    UploadODFJob.createInstance,
    UploadODFJob.IMPLEMENTATION_NAME,
    UploadODFJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    PreDriveSettingsJob.createInstance,
    PreDriveSettingsJob.IMPLEMENTATION_NAME,
    PreDriveSettingsJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    OpenPreDriveJob.createInstance,
    OpenPreDriveJob.IMPLEMENTATION_NAME,
    OpenPreDriveJob.SERVICE_NAMES
)

g_ImplementationHelper.addImplementation(
    PreDriveOptionsHandler.createInstance,
    PreDriveOptionsHandler.IMPLEMENTATION_NAME,
    PreDriveOptionsHandler.SERVICE_NAMES
)
