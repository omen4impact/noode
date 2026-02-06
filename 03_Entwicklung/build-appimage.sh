#!/bin/bash
# Noode AppImage Build Script
# Target: Linux Mint
# 
# Prerequisites:
#   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 libcairo2-dev libgirepository1.0-dev

set -e

APP_NAME="Noode"
APP_VERSION="0.5.0"
APP_DIR="AppDir"
ARCH="x86_64"

echo "🚀 Building Noode AppImage v${APP_VERSION}"
echo ""

# Check for GTK dependencies (use system Python, not venv)
if ! /usr/bin/python3 -c "import gi" 2>/dev/null; then
    echo "❌ GTK dependencies not found. Please install:"
    echo "   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
    exit 1
fi

echo "✅ GTK dependencies found"

# Clean previous builds
rm -rf build dist *.AppImage "${APP_DIR}"

# Create AppDir structure
mkdir -p "${APP_DIR}/usr/bin"
mkdir -p "${APP_DIR}/usr/lib/python3/dist-packages"
mkdir -p "${APP_DIR}/usr/share/applications"
mkdir -p "${APP_DIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${APP_DIR}/usr/share/metainfo"

# Install Python package (without PyGObject - we use system)
echo "📦 Installing Python package..."

# Create a temporary requirements file without PyGObject
cat > /tmp/noode-requirements.txt << EOF
litellm>=1.50.0
pydantic>=2.0
sqlalchemy>=2.0
structlog>=24.0.0
httpx>=0.28.0
typer>=0.15.0
rich>=13.9.0
EOF

pip install --target="${APP_DIR}/usr/lib/python3/dist-packages" \
    -r /tmp/noode-requirements.txt \
    --quiet 2>/dev/null || pip install --target="${APP_DIR}/usr/lib/python3/dist-packages" \
    -r /tmp/noode-requirements.txt

# Copy noode package
echo "📁 Copying Noode package..."
cp -r src/noode "${APP_DIR}/usr/lib/python3/dist-packages/"

# Copy system GTK bindings
echo "📦 Copying GTK bindings..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
SITE_PACKAGES="/usr/lib/python3/dist-packages"

# Copy gi module
if [ -d "${SITE_PACKAGES}/gi" ]; then
    cp -r "${SITE_PACKAGES}/gi" "${APP_DIR}/usr/lib/python3/dist-packages/"
fi

# Copy cairo module
if [ -f "${SITE_PACKAGES}/cairo/__init__.py" ]; then
    cp -r "${SITE_PACKAGES}/cairo" "${APP_DIR}/usr/lib/python3/dist-packages/"
fi

# Create launcher script
cat > "${APP_DIR}/usr/bin/noode-desktop" << 'LAUNCHER'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
LIB="${HERE}/../lib/python3/dist-packages"

export PYTHONPATH="${LIB}:${PYTHONPATH}"
export GI_TYPELIB_PATH="/usr/lib/x86_64-linux-gnu/girepository-1.0:${GI_TYPELIB_PATH}"
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"

exec python3 -m noode.desktop "$@"
LAUNCHER
chmod +x "${APP_DIR}/usr/bin/noode-desktop"

# CLI launcher
cat > "${APP_DIR}/usr/bin/noode" << 'LAUNCHER'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
LIB="${HERE}/../lib/python3/dist-packages"

export PYTHONPATH="${LIB}:${PYTHONPATH}"

exec python3 -m noode.cli "$@"
LAUNCHER
chmod +x "${APP_DIR}/usr/bin/noode"

# Create desktop entry
cat > "${APP_DIR}/usr/share/applications/noode.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Noode
GenericName=AI Development Platform
Comment=Autonome Software-Entwicklung mit AI-Agents
Exec=noode-desktop
Icon=noode
Categories=Development;IDE;
Terminal=false
StartupNotify=true
Keywords=AI;Development;Agents;Code;
EOF

# Copy to AppDir root
cp "${APP_DIR}/usr/share/applications/noode.desktop" "${APP_DIR}/"

# Create icon
cat > "${APP_DIR}/usr/share/icons/hicolor/256x256/apps/noode.svg" << 'ICON'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0A2621"/>
      <stop offset="100%" style="stop-color:#0E3A33"/>
    </linearGradient>
  </defs>
  <rect width="256" height="256" rx="48" fill="url(#bg)"/>
  <circle cx="128" cy="128" r="60" fill="none" stroke="#C1FF72" stroke-width="8"/>
  <circle cx="128" cy="128" r="20" fill="#C1FF72"/>
  <path d="M128 68 L128 48" stroke="#C1FF72" stroke-width="6" stroke-linecap="round"/>
  <path d="M128 208 L128 188" stroke="#C1FF72" stroke-width="6" stroke-linecap="round"/>
  <path d="M68 128 L48 128" stroke="#C1FF72" stroke-width="6" stroke-linecap="round"/>
  <path d="M208 128 L188 128" stroke="#C1FF72" stroke-width="6" stroke-linecap="round"/>
</svg>
ICON

ln -sf usr/share/icons/hicolor/256x256/apps/noode.svg "${APP_DIR}/noode.svg"

# Create AppStream metadata
cat > "${APP_DIR}/usr/share/metainfo/noode.appdata.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>dev.noode.Noode</id>
  <name>Noode</name>
  <summary>Autonome AI Development Platform</summary>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <description>
    <p>
      Noode ist eine autonome Entwicklungsplattform, die AI-Agents nutzt
      um Software zu entwickeln. Beschreibe einfach was du möchtest und
      Noode's spezialisierte Agents designen, implementieren und reviewen
      deine Anwendung.
    </p>
  </description>
  <launchable type="desktop-id">noode.desktop</launchable>
  <url type="homepage">https://noode.dev</url>
  <releases>
    <release version="${APP_VERSION}" date="2026-02-06"/>
  </releases>
</component>
EOF

# Create AppRun
cat > "${APP_DIR}/AppRun" << 'APPRUN'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}

export PATH="${HERE}/usr/bin:${PATH}"
export PYTHONPATH="${HERE}/usr/lib/python3/dist-packages:${PYTHONPATH}"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"
export GI_TYPELIB_PATH="/usr/lib/x86_64-linux-gnu/girepository-1.0:${GI_TYPELIB_PATH}"
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"

exec "${HERE}/usr/bin/noode-desktop" "$@"
APPRUN
chmod +x "${APP_DIR}/AppRun"

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "📥 Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
        -O appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
echo "🔨 Creating AppImage..."
ARCH=${ARCH} ./appimagetool-x86_64.AppImage --no-appstream "${APP_DIR}" "Noode-${APP_VERSION}-${ARCH}.AppImage" 2>/dev/null

if [ -f "Noode-${APP_VERSION}-${ARCH}.AppImage" ]; then
    echo ""
    echo "════════════════════════════════════════════════════"
    echo "✅ Build erfolgreich!"
    echo "════════════════════════════════════════════════════"
    echo ""
    echo "📦 AppImage: Noode-${APP_VERSION}-${ARCH}.AppImage"
    echo "📊 Größe:    $(du -h "Noode-${APP_VERSION}-${ARCH}.AppImage" | cut -f1)"
    echo ""
    echo "Ausführen:"
    echo "  chmod +x Noode-${APP_VERSION}-${ARCH}.AppImage"
    echo "  ./Noode-${APP_VERSION}-${ARCH}.AppImage"
    echo ""
else
    echo "❌ AppImage-Erstellung fehlgeschlagen"
    exit 1
fi
