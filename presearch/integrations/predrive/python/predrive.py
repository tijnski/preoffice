# -*- coding: utf-8 -*-
"""
PreDrive Integration for PreOffice
WebDAV-based cloud storage integration with PreDrive.

Copyright (c) 2024 Presearch
Licensed under MPL-2.0
"""

import uno
import unohelper
from com.sun.star.task import XJobExecutor
from com.sun.star.beans import PropertyValue
from com.sun.star.awt import XActionListener, XItemListener, XMouseListener
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO
from com.sun.star.awt.PosSize import POSSIZE, POS, SIZE

import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import base64
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime

# Configuration
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "preoffice")
CONFIG_FILE = os.path.join(CONFIG_DIR, "predrive.json")

DEFAULT_CONFIG = {
    "server_url": "https://predrive.eu",
    "username": "",
    "password": "",
    "last_path": "/",
    "remember_credentials": True
}

# WebDAV XML namespaces
DAV_NS = "DAV:"
NSMAP = {"d": DAV_NS}


class PreDriveConfig:
    """Manages PreDrive configuration."""

    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._load()

    def _load(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    saved = json.load(f)
                    self._config.update(saved)
        except Exception:
            pass

    def save(self):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception:
            pass

    def get(self, key, default=None):
        return self._config.get(key, default)

    def set(self, key, value):
        self._config[key] = value

    @property
    def server_url(self):
        return self._config.get("server_url", "").rstrip("/")

    @server_url.setter
    def server_url(self, value):
        self._config["server_url"] = value.rstrip("/")

    @property
    def webdav_url(self):
        return f"{self.server_url}/dav"

    @property
    def username(self):
        return self._config.get("username", "")

    @username.setter
    def username(self, value):
        self._config["username"] = value

    @property
    def password(self):
        return self._config.get("password", "")

    @password.setter
    def password(self, value):
        self._config["password"] = value

    @property
    def is_authenticated(self):
        return bool(self.username and self.password)


class WebDAVClient:
    """WebDAV client for PreDrive."""

    def __init__(self, config):
        self.config = config
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE

    def _get_auth_header(self):
        credentials = f"{self.config.username}:{self.config.password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded}"

    def _request(self, method, path, data=None, headers=None, depth=1):
        """Make WebDAV request."""
        # URL-encode path segments but preserve slashes
        encoded_path = "/".join(urllib.parse.quote(segment, safe="") for segment in path.split("/"))
        url = f"{self.config.webdav_url}{encoded_path}"

        # Debug: write to log file
        try:
            with open(os.path.join(CONFIG_DIR, "debug.log"), "a") as f:
                f.write(f"{method} {url}\n")
        except:
            pass

        req_headers = {
            "Authorization": self._get_auth_header(),
            "User-Agent": "PreOffice/1.0",
        }
        if headers:
            req_headers.update(headers)

        if method == "PROPFIND":
            req_headers["Depth"] = str(depth)
            req_headers["Content-Type"] = "application/xml"

        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)

        try:
            with urllib.request.urlopen(req, context=self._ssl_context, timeout=30) as resp:
                response_data = resp.read()
                # Debug: log response size
                try:
                    with open(os.path.join(CONFIG_DIR, "debug.log"), "a") as f:
                        f.write(f"  -> {resp.status} ({len(response_data)} bytes)\n")
                except:
                    pass
                return response_data, resp.status
        except urllib.error.HTTPError as e:
            if e.code == 207:  # Multi-Status (normal for PROPFIND)
                return e.read(), e.code
            # Debug: log error
            try:
                with open(os.path.join(CONFIG_DIR, "debug.log"), "a") as f:
                    f.write(f"  -> ERROR {e.code}: {e.reason}\n")
            except:
                pass
            raise WebDAVError(f"HTTP {e.code}: {e.reason}", e.code)
        except urllib.error.URLError as e:
            raise WebDAVError(f"Connection error: {e.reason}", 0)

    def test_connection(self):
        """Test WebDAV connection with OPTIONS request."""
        url = f"{self.config.webdav_url}/"
        req = urllib.request.Request(
            url,
            headers={"Authorization": self._get_auth_header()},
            method="OPTIONS"
        )
        try:
            with urllib.request.urlopen(req, context=self._ssl_context, timeout=10) as resp:
                dav_header = resp.headers.get("DAV", "")
                return "1" in dav_header or "2" in dav_header
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise WebDAVError("Authentication failed", 401)
            raise WebDAVError(f"HTTP {e.code}", e.code)
        except Exception as e:
            raise WebDAVError(str(e), 0)

    def list_directory(self, path="/"):
        """List directory contents using PROPFIND."""
        if not path.startswith("/"):
            path = "/" + path
        if not path.endswith("/"):
            path = path + "/"

        propfind_body = b'''<?xml version="1.0" encoding="utf-8"?>
<D:propfind xmlns:D="DAV:">
  <D:prop>
    <D:displayname/>
    <D:resourcetype/>
    <D:getcontentlength/>
    <D:getcontenttype/>
    <D:getlastmodified/>
  </D:prop>
</D:propfind>'''

        data, status = self._request("PROPFIND", path, data=propfind_body, depth=1)

        # Parse XML response
        items = []
        try:
            root = ET.fromstring(data)
            for response in root.findall(".//{DAV:}response"):
                href_elem = response.find("{DAV:}href")
                if href_elem is None:
                    continue

                href = urllib.parse.unquote(href_elem.text or "")
                # Skip the directory itself (handle various href formats)
                href_clean = href.rstrip("/")
                path_clean = path.rstrip("/")
                dav_path = "/dav" + path_clean
                if (href_clean == path_clean or
                    href_clean == dav_path or
                    href_clean == self.config.webdav_url + path_clean):
                    continue

                props = response.find(".//{DAV:}prop")
                if props is None:
                    continue

                name_elem = props.find("{DAV:}displayname")
                name = name_elem.text if name_elem is not None and name_elem.text else href.rstrip("/").split("/")[-1]

                resourcetype = props.find("{DAV:}resourcetype")
                is_folder = resourcetype is not None and resourcetype.find("{DAV:}collection") is not None

                size_elem = props.find("{DAV:}getcontentlength")
                size = int(size_elem.text) if size_elem is not None and size_elem.text else 0

                mime_elem = props.find("{DAV:}getcontenttype")
                mime = mime_elem.text if mime_elem is not None else ""

                modified_elem = props.find("{DAV:}getlastmodified")
                modified = modified_elem.text if modified_elem is not None else ""

                # Extract relative path from href (remove /dav prefix if present)
                item_path = href
                # Remove full URL prefix
                if item_path.startswith(self.config.webdav_url):
                    item_path = item_path[len(self.config.webdav_url):]
                # Remove /dav prefix (server returns paths like /dav/folder/file.txt)
                if item_path.startswith("/dav/"):
                    item_path = item_path[4:]  # Remove /dav, keep the /
                elif item_path.startswith("/dav"):
                    item_path = item_path[4:] or "/"
                if not item_path.startswith("/"):
                    item_path = "/" + item_path

                items.append({
                    "name": name,
                    "path": item_path,
                    "is_folder": is_folder,
                    "size": size,
                    "mime": mime,
                    "modified": modified
                })
        except ET.ParseError as e:
            raise WebDAVError(f"Failed to parse response: {e}", 0)

        # Sort: folders first, then files
        items.sort(key=lambda x: (0 if x["is_folder"] else 1, x["name"].lower()))
        return items

    def download_file(self, path):
        """Download file using GET."""
        if not path.startswith("/"):
            path = "/" + path

        data, status = self._request("GET", path)
        if not data:
            raise WebDAVError(f"Empty response for {path}", 0)
        return data

    def upload_file(self, path, content, content_type="application/octet-stream"):
        """Upload file using PUT."""
        if not path.startswith("/"):
            path = "/" + path

        headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(content)),
        }
        self._request("PUT", path, data=content, headers=headers)

    def create_folder(self, path):
        """Create folder using MKCOL."""
        if not path.startswith("/"):
            path = "/" + path
        if not path.endswith("/"):
            path = path + "/"

        self._request("MKCOL", path)

    def delete(self, path):
        """Delete file or folder using DELETE."""
        if not path.startswith("/"):
            path = "/" + path

        self._request("DELETE", path)


class WebDAVError(Exception):
    def __init__(self, message, status_code=0):
        super().__init__(message)
        self.status_code = status_code


def format_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"


def get_mime_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    types = {
        ".odt": "application/vnd.oasis.opendocument.text",
        ".ods": "application/vnd.oasis.opendocument.spreadsheet",
        ".odp": "application/vnd.oasis.opendocument.presentation",
        ".odg": "application/vnd.oasis.opendocument.graphics",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".rtf": "application/rtf",
        ".csv": "text/csv",
    }
    return types.get(ext, "application/octet-stream")


class FileListListener(unohelper.Base, XMouseListener):
    def __init__(self, browser):
        self.browser = browser

    def mousePressed(self, event):
        if event.ClickCount == 2:
            self.browser.on_double_click()

    def mouseReleased(self, event):
        pass

    def mouseEntered(self, event):
        pass

    def mouseExited(self, event):
        pass

    def disposing(self, event):
        pass


class ButtonListener(unohelper.Base, XActionListener):
    def __init__(self, callback):
        self.callback = callback

    def actionPerformed(self, event):
        self.callback(event)

    def disposing(self, event):
        pass


class PreDriveFileBrowser:
    """WebDAV file browser dialog."""

    def __init__(self, ctx, config, client, mode="open"):
        self.ctx = ctx
        self.config = config
        self.client = client
        self.mode = mode
        self.current_path = "/"
        self.path_stack = []
        self.items = []
        self.result = None

    def show(self, default_filename=""):
        smgr = self.ctx.ServiceManager

        dialog_model = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControlDialogModel", self.ctx)
        dialog_model.Width = 420
        dialog_model.Height = 360
        dialog_model.Title = "PreDrive - " + ("Open File" if self.mode == "open" else "Save to PreDrive")
        dialog_model.Closeable = True
        dialog_model.Moveable = True

        self._create_controls(dialog_model, default_filename)

        dialog = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControlDialog", self.ctx)
        dialog.setModel(dialog_model)

        self.dialog = dialog
        self.dialog_model = dialog_model

        self._add_listeners()
        self._load_directory("/")

        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
        dialog.createPeer(toolkit, None)

        result = dialog.execute()
        dialog.dispose()

        return self.result if result == 1 else None

    def _create_controls(self, model, default_filename):
        # Location label
        lbl = model.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        lbl.Name = "LblPath"
        lbl.PositionX = 10
        lbl.PositionY = 10
        lbl.Width = 45
        lbl.Height = 12
        lbl.Label = "Location:"
        model.insertByName("LblPath", lbl)

        # Path display
        path_fld = model.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        path_fld.Name = "PathField"
        path_fld.PositionX = 58
        path_fld.PositionY = 10
        path_fld.Width = 280
        path_fld.Height = 12
        path_fld.Label = "/"
        model.insertByName("PathField", path_fld)

        # Back button
        btn_back = model.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_back.Name = "BtnBack"
        btn_back.PositionX = 345
        btn_back.PositionY = 6
        btn_back.Width = 30
        btn_back.Height = 20
        btn_back.Label = "< Back"
        model.insertByName("BtnBack", btn_back)

        # Up button
        btn_up = model.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_up.Name = "BtnUp"
        btn_up.PositionX = 378
        btn_up.PositionY = 6
        btn_up.Width = 30
        btn_up.Height = 20
        btn_up.Label = "Up"
        model.insertByName("BtnUp", btn_up)

        # Toolbar buttons
        btn_refresh = model.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_refresh.Name = "BtnRefresh"
        btn_refresh.PositionX = 10
        btn_refresh.PositionY = 28
        btn_refresh.Width = 55
        btn_refresh.Height = 20
        btn_refresh.Label = "Refresh"
        model.insertByName("BtnRefresh", btn_refresh)

        btn_newfolder = model.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_newfolder.Name = "BtnNewFolder"
        btn_newfolder.PositionX = 70
        btn_newfolder.PositionY = 28
        btn_newfolder.Width = 65
        btn_newfolder.Height = 20
        btn_newfolder.Label = "New Folder"
        model.insertByName("BtnNewFolder", btn_newfolder)

        # File list
        file_list = model.createInstance("com.sun.star.awt.UnoControlListBoxModel")
        file_list.Name = "FileList"
        file_list.PositionX = 10
        file_list.PositionY = 54
        file_list.Width = 400
        file_list.Height = 220
        file_list.Dropdown = False
        file_list.MultiSelection = False
        file_list.Border = 1
        model.insertByName("FileList", file_list)

        # Info label
        info = model.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        info.Name = "InfoLabel"
        info.PositionX = 10
        info.PositionY = 280
        info.Width = 400
        info.Height = 12
        info.Label = "Double-click a folder to open it"
        model.insertByName("InfoLabel", info)

        if self.mode == "save":
            # Filename label
            fn_lbl = model.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
            fn_lbl.Name = "LblFilename"
            fn_lbl.PositionX = 10
            fn_lbl.PositionY = 300
            fn_lbl.Width = 45
            fn_lbl.Height = 12
            fn_lbl.Label = "Filename:"
            model.insertByName("LblFilename", fn_lbl)

            fn_fld = model.createInstance("com.sun.star.awt.UnoControlEditModel")
            fn_fld.Name = "FilenameField"
            fn_fld.PositionX = 58
            fn_fld.PositionY = 297
            fn_fld.Width = 280
            fn_fld.Height = 18
            fn_fld.Text = default_filename
            model.insertByName("FilenameField", fn_fld)

        # OK/Cancel buttons
        btn_ok = model.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_ok.Name = "BtnOK"
        btn_ok.PositionX = 260
        btn_ok.PositionY = 330
        btn_ok.Width = 70
        btn_ok.Height = 24
        btn_ok.Label = "Open" if self.mode == "open" else "Save"
        btn_ok.DefaultButton = True
        model.insertByName("BtnOK", btn_ok)

        btn_cancel = model.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_cancel.Name = "BtnCancel"
        btn_cancel.PositionX = 335
        btn_cancel.PositionY = 330
        btn_cancel.Width = 70
        btn_cancel.Height = 24
        btn_cancel.Label = "Cancel"
        model.insertByName("BtnCancel", btn_cancel)

    def _add_listeners(self):
        self.dialog.getControl("BtnBack").addActionListener(ButtonListener(lambda e: self._go_back()))
        self.dialog.getControl("BtnUp").addActionListener(ButtonListener(lambda e: self._go_up()))
        self.dialog.getControl("BtnRefresh").addActionListener(ButtonListener(lambda e: self._load_directory(self.current_path)))
        self.dialog.getControl("BtnNewFolder").addActionListener(ButtonListener(lambda e: self._create_folder()))
        self.dialog.getControl("BtnOK").addActionListener(ButtonListener(lambda e: self._on_ok()))
        self.dialog.getControl("BtnCancel").addActionListener(ButtonListener(lambda e: self.dialog.endDialog(0)))

        self.dialog.getControl("FileList").addMouseListener(FileListListener(self))

    def _load_directory(self, path):
        try:
            self.dialog_model.getByName("InfoLabel").Label = "Loading..."
            self.items = self.client.list_directory(path)
            self.current_path = path

            # Update path display
            self.dialog_model.getByName("PathField").Label = path or "/"

            # Update list
            file_list = self.dialog.getControl("FileList")
            file_list.removeItems(0, file_list.getItemCount())

            for item in self.items:
                if item["is_folder"]:
                    display = f"[Folder]  {item['name']}"
                else:
                    display = f"{item['name']}  ({format_size(item['size'])})"
                file_list.addItem(display, file_list.getItemCount())

            # Update info
            folders = sum(1 for i in self.items if i["is_folder"])
            files = len(self.items) - folders
            self.dialog_model.getByName("InfoLabel").Label = f"{folders} folders, {files} files"

        except WebDAVError as e:
            self.dialog_model.getByName("InfoLabel").Label = f"Error: {e}"

    def _get_selected_item(self):
        file_list = self.dialog.getControl("FileList")
        idx = file_list.getSelectedItemPos()
        if 0 <= idx < len(self.items):
            return self.items[idx]
        return None

    def on_double_click(self):
        item = self._get_selected_item()
        if item and item["is_folder"]:
            self.path_stack.append(self.current_path)
            self._load_directory(item["path"])
        elif item and self.mode == "open":
            self._on_ok()

    def _go_back(self):
        if self.path_stack:
            path = self.path_stack.pop()
            self._load_directory(path)

    def _go_up(self):
        if self.current_path and self.current_path != "/":
            parent = "/".join(self.current_path.rstrip("/").split("/")[:-1])
            if not parent:
                parent = "/"
            self.path_stack.append(self.current_path)
            self._load_directory(parent)

    def _create_folder(self):
        name = self._input_dialog("New Folder", "Enter folder name:")
        if name:
            try:
                new_path = self.current_path.rstrip("/") + "/" + name
                self.client.create_folder(new_path)
                self._load_directory(self.current_path)
            except WebDAVError as e:
                self.dialog_model.getByName("InfoLabel").Label = f"Error: {e}"

    def _input_dialog(self, title, prompt):
        smgr = self.ctx.ServiceManager

        dm = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", self.ctx)
        dm.Width = 220
        dm.Height = 85
        dm.Title = title

        lbl = dm.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        lbl.Name = "Label"
        lbl.PositionX = 10
        lbl.PositionY = 12
        lbl.Width = 200
        lbl.Height = 12
        lbl.Label = prompt
        dm.insertByName("Label", lbl)

        fld = dm.createInstance("com.sun.star.awt.UnoControlEditModel")
        fld.Name = "Input"
        fld.PositionX = 10
        fld.PositionY = 28
        fld.Width = 200
        fld.Height = 18
        dm.insertByName("Input", fld)

        btn_ok = dm.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_ok.Name = "OK"
        btn_ok.PositionX = 70
        btn_ok.PositionY = 55
        btn_ok.Width = 60
        btn_ok.Height = 22
        btn_ok.Label = "OK"
        btn_ok.PushButtonType = 1
        dm.insertByName("OK", btn_ok)

        btn_cancel = dm.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_cancel.Name = "Cancel"
        btn_cancel.PositionX = 135
        btn_cancel.PositionY = 55
        btn_cancel.Width = 60
        btn_cancel.Height = 22
        btn_cancel.Label = "Cancel"
        btn_cancel.PushButtonType = 2
        dm.insertByName("Cancel", btn_cancel)

        dlg = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", self.ctx)
        dlg.setModel(dm)

        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
        dlg.createPeer(toolkit, None)

        if dlg.execute() == 1:
            value = dlg.getControl("Input").getText()
            dlg.dispose()
            return value
        dlg.dispose()
        return None

    def _on_ok(self):
        if self.mode == "open":
            item = self._get_selected_item()
            if item and not item["is_folder"]:
                self.result = {"path": item["path"], "name": item["name"]}
                self.dialog.endDialog(1)  # Return 1 for OK
            elif item and item["is_folder"]:
                self.path_stack.append(self.current_path)
                self._load_directory(item["path"])
            else:
                self.dialog_model.getByName("InfoLabel").Label = "Please select a file"
        else:  # save
            filename = self.dialog.getControl("FilenameField").getText().strip()
            if filename:
                save_path = self.current_path.rstrip("/") + "/" + filename
                self.result = {"path": save_path, "name": filename}
                self.dialog.endDialog(1)  # Return 1 for OK
            else:
                self.dialog_model.getByName("InfoLabel").Label = "Please enter a filename"


class PreDriveProgressDialog:
    def __init__(self, ctx, title, message):
        self.ctx = ctx
        self.title = title
        self.message = message
        self.dialog = None

    def show(self):
        smgr = self.ctx.ServiceManager

        dm = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", self.ctx)
        dm.Width = 260
        dm.Height = 70
        dm.Title = self.title
        dm.Closeable = False

        lbl = dm.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        lbl.Name = "Message"
        lbl.PositionX = 10
        lbl.PositionY = 15
        lbl.Width = 240
        lbl.Height = 12
        lbl.Label = self.message
        dm.insertByName("Message", lbl)

        prog = dm.createInstance("com.sun.star.awt.UnoControlProgressBarModel")
        prog.Name = "Progress"
        prog.PositionX = 10
        prog.PositionY = 35
        prog.Width = 240
        prog.Height = 18
        prog.ProgressValueMin = 0
        prog.ProgressValueMax = 100
        prog.ProgressValue = 0
        dm.insertByName("Progress", prog)

        self.dialog = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", self.ctx)
        self.dialog.setModel(dm)
        self.dialog_model = dm

        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
        self.dialog.createPeer(toolkit, None)
        self.dialog.setVisible(True)

    def update(self, value, message=None):
        if self.dialog:
            self.dialog_model.getByName("Progress").ProgressValue = int(value)
            if message:
                self.dialog_model.getByName("Message").Label = message

    def close(self):
        if self.dialog:
            self.dialog.setVisible(False)
            self.dialog.dispose()
            self.dialog = None


class PreDriveService(unohelper.Base, XJobExecutor):
    """Main PreDrive WebDAV service."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.config = PreDriveConfig()
        self.client = WebDAVClient(self.config)

    def trigger(self, command):
        try:
            if command == "SaveToPreDrive":
                self._save_to_predrive()
            elif command == "OpenFromPreDrive":
                self._open_from_predrive()
            elif command == "PreDriveSettings":
                self._show_settings()
            elif command == "PreDriveLogin":
                self._show_login()
            elif command == "PreDriveLogout":
                self._logout()
        except Exception as e:
            self._show_error(f"Error: {e}")

    def _get_desktop(self):
        smgr = self.ctx.ServiceManager
        return smgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)

    def _get_current_document(self):
        return self._get_desktop().getCurrentComponent()

    def _show_message(self, message, title="PreDrive", msg_type=INFOBOX):
        desktop = self._get_desktop()
        frame = desktop.getCurrentFrame()
        window = frame.getContainerWindow()
        toolkit = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
        msgbox = toolkit.createMessageBox(window, msg_type, BUTTONS_OK, title, message)
        return msgbox.execute()

    def _show_error(self, message):
        self._show_message(message, "PreDrive Error", ERRORBOX)

    def _ensure_authenticated(self):
        if not self.config.is_authenticated:
            self._show_login()
            return self.config.is_authenticated
        try:
            self.client.test_connection()
            return True
        except WebDAVError as e:
            if e.status_code == 401:
                self.config.username = ""
                self.config.password = ""
                self._show_login()
                return self.config.is_authenticated
            raise

    def _save_to_predrive(self):
        if not self._ensure_authenticated():
            return

        doc = self._get_current_document()
        if not doc:
            self._show_error("No document is currently open.")
            return

        # Get filename
        doc_url = doc.getURL()
        if doc_url:
            filename = os.path.basename(urllib.parse.unquote(doc_url.replace("file://", "")))
        else:
            impl = doc.getImplementationName()
            if "TextDocument" in impl:
                filename = "Untitled.odt"
            elif "SpreadsheetDocument" in impl:
                filename = "Untitled.ods"
            elif "PresentationDocument" in impl:
                filename = "Untitled.odp"
            else:
                filename = "Untitled.odt"

        # Show browser
        browser = PreDriveFileBrowser(self.ctx, self.config, self.client, mode="save")
        result = browser.show(filename)

        if not result:
            return

        save_path = result["path"]
        filename = result["name"]

        # Ensure extension
        if not os.path.splitext(filename)[1]:
            impl = doc.getImplementationName()
            if "TextDocument" in impl:
                save_path += ".odt"
            elif "SpreadsheetDocument" in impl:
                save_path += ".ods"
            elif "PresentationDocument" in impl:
                save_path += ".odp"

        # Debug: show what we're about to upload
        self._show_message(f"Uploading to:\nPath: {save_path}\nURL: {self.config.webdav_url}{save_path}", "Debug")

        progress = PreDriveProgressDialog(self.ctx, "Saving to PreDrive", f"Saving {filename}...")
        progress.show()

        try:
            # Save to temp (use safe filename)
            safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            if not safe_filename:
                safe_filename = "document"
            ext = os.path.splitext(filename)[1]
            if ext and not safe_filename.endswith(ext):
                safe_filename += ext
            temp_path = os.path.join(tempfile.gettempdir(), safe_filename)
            temp_url = "file://" + urllib.parse.quote(temp_path, safe="/:")
            doc.storeToURL(temp_url, ())

            progress.update(40, "Uploading...")

            with open(temp_path, 'rb') as f:
                content = f.read()

            mime = get_mime_type(filename)

            # Debug: show file size
            self._show_message(f"Uploading {len(content)} bytes as {mime}", "Debug")

            self.client.upload_file(save_path, content, mime)

            progress.update(100, "Done!")
            progress.close()

            self._show_message(f"Saved '{filename}' to PreDrive!")

        except Exception as e:
            progress.close()
            self._show_error(f"Failed to save: {e}")
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    def _open_from_predrive(self):
        if not self._ensure_authenticated():
            return

        browser = PreDriveFileBrowser(self.ctx, self.config, self.client, mode="open")
        result = browser.show()

        if not result:
            return

        file_path = result["path"]
        filename = result["name"]

        # Debug: show what we're about to download
        self._show_message(f"Downloading:\nPath: {file_path}\nURL: {self.config.webdav_url}{file_path}", "Debug")

        progress = PreDriveProgressDialog(self.ctx, "Opening from PreDrive", f"Downloading {filename}...")
        progress.show()

        try:
            progress.update(30, "Downloading...")
            content = self.client.download_file(file_path)

            # Debug: show download result
            self._show_message(f"Downloaded {len(content)} bytes", "Debug")

            progress.update(70, "Opening...")

            # Use safe filename for temp file
            safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            if not safe_filename:
                safe_filename = "document"
            ext = os.path.splitext(filename)[1]
            if ext and not safe_filename.endswith(ext):
                safe_filename += ext
            temp_path = os.path.join(tempfile.gettempdir(), safe_filename)
            with open(temp_path, 'wb') as f:
                f.write(content)

            desktop = self._get_desktop()
            temp_url = "file://" + urllib.parse.quote(temp_path, safe="/:")
            desktop.loadComponentFromURL(temp_url, "_blank", 0, ())

            progress.update(100, "Done!")
            progress.close()

        except Exception as e:
            progress.close()
            self._show_error(f"Failed to open: {e}")

    def _show_login(self):
        smgr = self.ctx.ServiceManager

        dm = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", self.ctx)
        dm.Width = 300
        dm.Height = 155
        dm.Title = "Connect to PreDrive"

        # Header
        hdr = dm.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        hdr.Name = "Header"
        hdr.PositionX = 10
        hdr.PositionY = 10
        hdr.Width = 280
        hdr.Height = 14
        hdr.Label = "Enter your PreDrive WebDAV credentials"
        hdr.FontWeight = 150
        dm.insertByName("Header", hdr)

        # Server
        lbl_srv = dm.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        lbl_srv.Name = "LblServer"
        lbl_srv.PositionX = 10
        lbl_srv.PositionY = 34
        lbl_srv.Width = 60
        lbl_srv.Height = 12
        lbl_srv.Label = "Server URL:"
        dm.insertByName("LblServer", lbl_srv)

        fld_srv = dm.createInstance("com.sun.star.awt.UnoControlEditModel")
        fld_srv.Name = "ServerUrl"
        fld_srv.PositionX = 75
        fld_srv.PositionY = 32
        fld_srv.Width = 215
        fld_srv.Height = 16
        fld_srv.Text = self.config.server_url or "https://predrive.eu"
        dm.insertByName("ServerUrl", fld_srv)

        # Username
        lbl_usr = dm.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        lbl_usr.Name = "LblUser"
        lbl_usr.PositionX = 10
        lbl_usr.PositionY = 56
        lbl_usr.Width = 60
        lbl_usr.Height = 12
        lbl_usr.Label = "Username:"
        dm.insertByName("LblUser", lbl_usr)

        fld_usr = dm.createInstance("com.sun.star.awt.UnoControlEditModel")
        fld_usr.Name = "Username"
        fld_usr.PositionX = 75
        fld_usr.PositionY = 54
        fld_usr.Width = 215
        fld_usr.Height = 16
        fld_usr.Text = self.config.username or ""
        dm.insertByName("Username", fld_usr)

        # Password
        lbl_pwd = dm.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
        lbl_pwd.Name = "LblPass"
        lbl_pwd.PositionX = 10
        lbl_pwd.PositionY = 78
        lbl_pwd.Width = 60
        lbl_pwd.Height = 12
        lbl_pwd.Label = "Password:"
        dm.insertByName("LblPass", lbl_pwd)

        fld_pwd = dm.createInstance("com.sun.star.awt.UnoControlEditModel")
        fld_pwd.Name = "Password"
        fld_pwd.PositionX = 75
        fld_pwd.PositionY = 76
        fld_pwd.Width = 215
        fld_pwd.Height = 16
        fld_pwd.EchoChar = ord('*')
        fld_pwd.Text = self.config.password or ""
        dm.insertByName("Password", fld_pwd)

        # Remember
        chk = dm.createInstance("com.sun.star.awt.UnoControlCheckBoxModel")
        chk.Name = "Remember"
        chk.PositionX = 75
        chk.PositionY = 98
        chk.Width = 150
        chk.Height = 12
        chk.Label = "Remember credentials"
        chk.State = 1
        dm.insertByName("Remember", chk)

        # Buttons
        btn_ok = dm.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_ok.Name = "Connect"
        btn_ok.PositionX = 130
        btn_ok.PositionY = 125
        btn_ok.Width = 75
        btn_ok.Height = 22
        btn_ok.Label = "Connect"
        btn_ok.DefaultButton = True
        dm.insertByName("Connect", btn_ok)

        btn_cancel = dm.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn_cancel.Name = "Cancel"
        btn_cancel.PositionX = 210
        btn_cancel.PositionY = 125
        btn_cancel.Width = 75
        btn_cancel.Height = 22
        btn_cancel.Label = "Cancel"
        dm.insertByName("Cancel", btn_cancel)

        dialog = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", self.ctx)
        dialog.setModel(dm)

        def on_connect(event):
            server = dialog.getControl("ServerUrl").getText().strip()
            username = dialog.getControl("Username").getText().strip()
            password = dialog.getControl("Password").getText().strip()
            remember = dialog.getControl("Remember").getState() == 1

            if not server or not username or not password:
                return

            self.config.server_url = server
            self.config.username = username
            self.config.password = password

            try:
                self.client.test_connection()
                if remember:
                    self.config.save()
                dialog.endExecute()
            except WebDAVError as e:
                self.config.username = ""
                self.config.password = ""
                self._show_error(f"Connection failed: {e}")

        dialog.getControl("Connect").addActionListener(ButtonListener(on_connect))
        dialog.getControl("Cancel").addActionListener(ButtonListener(lambda e: dialog.endExecute()))

        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
        dialog.createPeer(toolkit, None)
        dialog.execute()
        dialog.dispose()

    def _show_settings(self):
        status = "Connected" if self.config.is_authenticated else "Not connected"
        msg = f"""PreDrive Settings

Server: {self.config.server_url}
WebDAV: {self.config.webdav_url}
Username: {self.config.username or 'N/A'}
Status: {status}

Config: {CONFIG_FILE}"""
        self._show_message(msg, "PreDrive Settings")

    def _logout(self):
        self.config.username = ""
        self.config.password = ""
        self.config.save()
        self._show_message("Logged out from PreDrive.")


# UNO component registration
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    PreDriveService,
    "com.presearch.predrive.PreDriveService",
    ("com.sun.star.task.Job",)
)
