#!/usr/bin/env python3
"""
PreOffice Customization Installer
Applies PreOffice UI customizations to LibreOffice

Usage:
    python install.py [--uninstall] [--libreoffice-path <path>]
"""

import os
import sys
import shutil
import platform
import argparse
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET


class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

    @classmethod
    def disable(cls):
        cls.BLUE = cls.GREEN = cls.YELLOW = cls.RED = cls.END = cls.BOLD = ''


def info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")


def success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {msg}")


def warn(msg):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {msg}")


def error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.END} {msg}")
    sys.exit(1)


class PreOfficeInstaller:
    def __init__(self, libreoffice_path=None):
        self.script_dir = Path(__file__).parent.resolve()
        self.ui_dir = self.script_dir / "ui"
        self.libreoffice_path = None
        self.user_profile = None

        self._detect_paths(libreoffice_path)

    def _detect_paths(self, custom_path=None):
        """Detect LibreOffice installation and user profile paths"""
        system = platform.system()

        if custom_path:
            self.libreoffice_path = Path(custom_path)
        else:
            if system == "Darwin":  # macOS
                candidates = [
                    Path("/Applications/LibreOffice.app/Contents"),
                    Path.home() / "Applications/LibreOffice.app/Contents"
                ]
            elif system == "Linux":
                candidates = [
                    Path("/usr/lib/libreoffice"),
                    Path("/opt/libreoffice"),
                    Path("/usr/lib64/libreoffice"),
                    Path("/snap/libreoffice/current/lib/libreoffice")
                ]
            elif system == "Windows":
                candidates = [
                    Path("C:/Program Files/LibreOffice"),
                    Path("C:/Program Files (x86)/LibreOffice")
                ]
            else:
                error(f"Unsupported operating system: {system}")

            for path in candidates:
                if path.exists():
                    self.libreoffice_path = path
                    break

        # Set user profile path
        if system == "Darwin":
            self.user_profile = Path.home() / "Library/Application Support/LibreOffice/4/user"
        elif system == "Linux":
            self.user_profile = Path.home() / ".config/libreoffice/4/user"
        elif system == "Windows":
            self.user_profile = Path(os.environ.get("APPDATA", "")) / "LibreOffice/4/user"

    def verify_paths(self):
        """Verify that required paths exist"""
        if not self.libreoffice_path or not self.libreoffice_path.exists():
            error("LibreOffice installation not found. Use --libreoffice-path to specify.")

        info(f"LibreOffice found at: {self.libreoffice_path}")
        info(f"User profile at: {self.user_profile}")

        if not self.ui_dir.exists():
            error(f"UI directory not found at: {self.ui_dir}")

    def create_backup(self):
        """Create backup of existing configuration"""
        backup_dir = self.user_profile / f"preoffice_backup_{datetime.now():%Y%m%d_%H%M%S}"

        reg_file = self.user_profile / "registrymodifications.xcu"
        if reg_file.exists():
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(reg_file, backup_dir)
            info(f"Backup created at: {backup_dir}")

    def install_color_schemes(self):
        """Install color scheme XCU files"""
        info("Installing color schemes...")

        target_dir = self.user_profile / "registrymodifications"
        target_dir.mkdir(parents=True, exist_ok=True)

        source_dir = self.ui_dir / "color-scheme"
        if source_dir.exists():
            for xcu in source_dir.glob("*.xcu"):
                shutil.copy2(xcu, target_dir)
                success(f"Installed: {xcu.name}")

    def install_icons(self):
        """Install icon themes"""
        info("Installing icon theme...")

        # Light theme
        icon_dir = self.user_profile / "config/images_presearch/cmd"
        icon_dir.mkdir(parents=True, exist_ok=True)

        source_dir = self.ui_dir / "icon-theme/cmd"
        if source_dir.exists():
            for svg in source_dir.glob("*.svg"):
                shutil.copy2(svg, icon_dir)
            success("Installed light theme icons")

        # Copy links.txt
        links_file = self.ui_dir / "icon-theme/links.txt"
        if links_file.exists():
            shutil.copy2(links_file, icon_dir.parent)

        # Dark theme
        dark_icon_dir = self.user_profile / "config/images_presearch_dark/cmd"
        dark_icon_dir.mkdir(parents=True, exist_ok=True)

        dark_source = self.ui_dir / "icon-theme-dark/cmd"
        if dark_source.exists():
            for svg in dark_source.glob("*.svg"):
                shutil.copy2(svg, dark_icon_dir)
            success("Installed dark theme icons")

    def install_templates(self):
        """Install document templates"""
        info("Installing templates...")

        template_base = self.user_profile / "template/PreOffice"

        # Writer templates
        writer_dir = template_base / "Writer"
        writer_dir.mkdir(parents=True, exist_ok=True)
        source = self.ui_dir / "templates/writer"
        if source.exists():
            for fodt in source.glob("*.fodt"):
                shutil.copy2(fodt, writer_dir)
            success("Installed Writer templates")

        # Calc templates
        calc_dir = template_base / "Calc"
        calc_dir.mkdir(parents=True, exist_ok=True)
        source = self.ui_dir / "templates/calc"
        if source.exists():
            for fods in source.glob("*.fods"):
                shutil.copy2(fods, calc_dir)
            success("Installed Calc templates")

        # Impress templates
        impress_dir = template_base / "Impress"
        impress_dir.mkdir(parents=True, exist_ok=True)
        source = self.ui_dir / "templates/impress"
        if source.exists():
            for fodp in source.glob("*.fodp"):
                shutil.copy2(fodp, impress_dir)
            success("Installed Impress templates")

    def install_startcenter(self):
        """Install Start Center branding"""
        info("Installing Start Center branding...")

        target_dir = self.user_profile / "config/startcenter"
        target_dir.mkdir(parents=True, exist_ok=True)

        source_dir = self.ui_dir / "startcenter"
        if source_dir.exists():
            for svg in source_dir.glob("*.svg"):
                shutil.copy2(svg, target_dir)
            for xcu in source_dir.glob("*.xcu"):
                shutil.copy2(xcu, target_dir)
            success("Installed Start Center branding")

    def install_defaults(self):
        """Install default settings"""
        info("Installing default settings...")

        target_dir = self.user_profile / "registrymodifications"
        target_dir.mkdir(parents=True, exist_ok=True)

        source_dir = self.ui_dir / "defaults"
        if source_dir.exists():
            for xcu in source_dir.glob("*.xcu"):
                shutil.copy2(xcu, target_dir)
            success("Installed default settings")

    def apply_registry(self):
        """Apply registry modifications"""
        info("Applying registry modifications...")

        reg_file = self.user_profile / "registrymodifications.xcu"

        # Create if doesn't exist
        if not reg_file.exists():
            reg_file.parent.mkdir(parents=True, exist_ok=True)
            with open(reg_file, 'w', encoding='utf-8') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
</oor:items>
''')

        # Check if PreOffice settings already exist
        content = reg_file.read_text(encoding='utf-8')
        if "PreOffice" not in content:
            # Add settings before closing tag
            preoffice_settings = '''
<!-- PreOffice Customizations -->
<item oor:path="/org.openoffice.Office.Common/Misc">
  <prop oor:name="FirstRun" oor:op="fuse"><value>false</value></prop>
</item>
<item oor:path="/org.openoffice.Office.Common/Misc">
  <prop oor:name="ShowTipOfTheDay" oor:op="fuse"><value>false</value></prop>
</item>
<item oor:path="/org.openoffice.Office.Common/Save/Document">
  <prop oor:name="AutoSave" oor:op="fuse"><value>true</value></prop>
</item>
<item oor:path="/org.openoffice.Office.Common/Save/Document">
  <prop oor:name="AutoSaveTimeIntervall" oor:op="fuse"><value>5</value></prop>
</item>
<item oor:path="/org.openoffice.Office.Common/Security/Scripting">
  <prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>2</value></prop>
</item>

'''
            content = content.replace('</oor:items>', preoffice_settings + '</oor:items>')
            reg_file.write_text(content, encoding='utf-8')
            success("Applied registry modifications")
        else:
            info("PreOffice settings already present in registry")

    def install(self):
        """Run full installation"""
        print()
        print(f"{Colors.BLUE}╔════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BLUE}║     PreOffice Customization Installer      ║{Colors.END}")
        print(f"{Colors.BLUE}║        Part of the Pre-suite               ║{Colors.END}")
        print(f"{Colors.BLUE}╚════════════════════════════════════════════╝{Colors.END}")
        print()

        self.user_profile.mkdir(parents=True, exist_ok=True)

        self.create_backup()
        self.install_color_schemes()
        self.install_icons()
        self.install_templates()
        self.install_startcenter()
        self.install_defaults()
        self.apply_registry()

        print()
        print(f"{Colors.GREEN}╔════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.GREEN}║     Installation Complete!                 ║{Colors.END}")
        print(f"{Colors.GREEN}╚════════════════════════════════════════════╝{Colors.END}")
        print()
        print("Next steps:")
        print("  1. Restart LibreOffice")
        print("  2. Go to Tools > Options > View")
        print("  3. Select 'Presearch' icon theme")
        print("  4. Access templates via File > New > Templates")
        print()

    def uninstall(self):
        """Remove PreOffice customizations"""
        info("Uninstalling PreOffice customizations...")

        # Remove icon themes
        shutil.rmtree(self.user_profile / "config/images_presearch", ignore_errors=True)
        shutil.rmtree(self.user_profile / "config/images_presearch_dark", ignore_errors=True)

        # Remove templates
        shutil.rmtree(self.user_profile / "template/PreOffice", ignore_errors=True)

        # Remove Start Center customizations
        shutil.rmtree(self.user_profile / "config/startcenter", ignore_errors=True)

        # Remove registry modifications directory
        shutil.rmtree(self.user_profile / "registrymodifications", ignore_errors=True)

        warn("Registry modifications not removed (manual cleanup may be needed)")
        success("PreOffice customizations removed")


def main():
    parser = argparse.ArgumentParser(description='PreOffice Customization Installer')
    parser.add_argument('--libreoffice-path', help='Specify LibreOffice installation path')
    parser.add_argument('--uninstall', action='store_true', help='Remove PreOffice customizations')

    args = parser.parse_args()

    # Disable colors on Windows cmd
    if platform.system() == 'Windows' and not os.environ.get('TERM'):
        Colors.disable()

    installer = PreOfficeInstaller(args.libreoffice_path)
    installer.verify_paths()

    if args.uninstall:
        installer.uninstall()
    else:
        installer.install()


if __name__ == '__main__':
    main()
