# Building PreOffice

This document describes how to build PreOffice from source.

## Prerequisites

### All Platforms
- Git
- Python 3.8+
- At least 16GB RAM (32GB recommended)
- 80GB+ free disk space

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install git build-essential zip \
    libcups2-dev libfontconfig1-dev gperf \
    libxrandr-dev libxinerama-dev libxcursor-dev \
    libkrb5-dev nasm libssl-dev libxslt1-dev \
    libxml2-dev libgtk-3-dev libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev libdbus-1-dev \
    ant junit4 default-jdk
```

### macOS
```bash
# Install Xcode command line tools
xcode-select --install

# Install Homebrew dependencies
brew install autoconf automake ccache nasm pkg-config
```

### Windows
- Visual Studio 2019 or 2022 with C++ workload
- Cygwin with packages: autoconf, automake, bison, flex, gcc-g++, git, gnupg, gperf, make, perl, zip
- Java JDK 11+

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/presearch/preoffice.git
cd preoffice
git submodule update --init --recursive
```

### 2. Configure the build
```bash
cd core

# Linux/macOS
./autogen.sh --with-lang="en-US" --enable-release-build

# Windows (in Cygwin)
./autogen.sh --with-lang="en-US" --enable-release-build --with-visual-studio=2022
```

### 3. Build
```bash
make
```

First build takes 2-6 hours depending on hardware. Subsequent builds are faster.

### 4. Run
```bash
# Linux
./instdir/program/soffice

# macOS
open ./instdir/LibreOffice.app

# Windows
./instdir/program/soffice.exe
```

## Build Options

| Option | Description |
|--------|-------------|
| `--enable-release-build` | Production build with optimizations |
| `--enable-debug` | Debug build with symbols |
| `--with-lang="en-US de fr"` | Include specific languages |
| `--disable-online-update` | Disable update checking |
| `--enable-symbols` | Include debug symbols |

## Incremental Builds

After the initial build, you can rebuild specific modules:
```bash
make Module_sw      # Writer only
make Module_sc      # Calc only
make Module_sd      # Impress only
```

## Troubleshooting

### Out of memory
Reduce parallel jobs:
```bash
make -j4  # Instead of default parallel jobs
```

### Missing dependencies
Run the dependency check:
```bash
./autogen.sh --help
```

### Build cache
Use ccache for faster rebuilds:
```bash
export CCACHE_DIR=$HOME/.ccache
./autogen.sh --enable-ccache
```

## CI Build

For CI environments, use:
```bash
./autogen.sh --enable-release-build --with-lang="en-US" \
    --disable-online-update --without-java
make build-nocheck
```

## Next Steps

After building:
1. Apply Presearch branding: See `presearch/brand/README.md`
2. Build installers: See `packaging/README.md`
3. Run tests: `make check`
