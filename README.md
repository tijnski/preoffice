# PreOffice

**PreOffice** is a LibreOffice fork branded for Presearch and the Pre-suite ecosystem. It provides a sovereignty-first, privacy-respecting office suite with integrated Presearch services.

## Features

- **Presearch Search Integration** - Search selected text with Presearch
- **PreGPT Integration** - AI assistance powered by PreGPT (supports cloud, sovereign, and local deployments)
- **PreStorage Export** - Export documents to PDF/ODF with optional cloud upload
- **Privacy Check** - One-click audit for document metadata, tracked changes, and hidden content
- **ODF Default** - Open Document Format as the default save format
- **No Telemetry** - Privacy-respecting defaults with no usage tracking

## Deployment Modes

PreOffice supports multiple deployment scenarios:

| Mode | Description |
|------|-------------|
| **Cloud** | Full integration with Presearch cloud services |
| **Sovereign** | Connect to your own sovereign cloud deployment |
| **Local/On-Prem** | Self-hosted services, full control |
| **Air-Gapped** | Offline-only mode, network features disabled |

## Quick Start

### Download

Pre-built installers available at [presearch.com/preoffice](https://presearch.com/preoffice)

| Platform | Download |
|----------|----------|
| Windows | `PreOffice-x.y.z-win64.msi` |
| macOS | `PreOffice-x.y.z-macos.dmg` |
| Linux | `PreOffice-x.y.z-linux-x86_64.AppImage` |

### Build from Source

See [docs/BUILDING.md](docs/BUILDING.md) for build instructions.

```bash
git clone https://github.com/presearch/preoffice.git
cd preoffice
git submodule update --init --recursive
cd core
./autogen.sh --enable-release-build
make
```

## Repository Structure

```
preoffice/
├── upstream/           # LibreOffice version tracking
├── core/               # LibreOffice fork source
├── presearch/
│   ├── brand/          # Tokens, logos, assets
│   ├── ui/             # Icon theme, notebookbar, defaults
│   └── integrations/   # PreGPT, Search, Storage, Privacy
├── packaging/          # Windows, macOS, Linux installers
├── compliance/         # Licenses, notices, SBOM
├── docs/               # Documentation
└── .github/workflows/  # CI/CD
```

## Documentation

- [Building](docs/BUILDING.md) - Build from source
- [Release Process](docs/RELEASE.md) - Release engineering
- [Contributing](docs/CONTRIBUTING.md) - How to contribute
- [Security](docs/SECURITY.md) - Security policy and reporting

## License

- **Core fork code**: MPL 2.0 (inherited from LibreOffice)
- **Presearch integrations**: MIT
- **Brand assets**: Presearch proprietary

See [compliance/NOTICE](compliance/NOTICE) for full attribution.

## Attribution

PreOffice is based on [LibreOffice](https://www.libreoffice.org/), a trademark of The Document Foundation.

---

Part of the [Pre-suite](https://presearch.com/presuite) ecosystem.
