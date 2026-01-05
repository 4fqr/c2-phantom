# C2 Phantom Build Scripts

## Build executable

```powershell
# Install PyInstaller
pip install pyinstaller

# Build single executable
pyinstaller --onefile --name c2-phantom --icon=assets/icon.ico c2_phantom/cli.py

# Build with UPX compression (smaller size)
pyinstaller --onefile --name c2-phantom --upx-dir=/path/to/upx c2_phantom/cli.py
```

## Build Docker image

```powershell
# Build image
docker build -t c2-phantom:latest .

# Build with specific version
docker build -t c2-phantom:1.0.0 .

# Run container
docker run -it --rm c2-phantom:latest phantom --version
```

## Build distribution packages

```powershell
# Install build tools
pip install build twine

# Build wheel and source distribution
python -m build

# Upload to PyPI (test)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

## Development build

```powershell
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=c2_phantom --cov-report=html
```

## Platform-specific builds

### Windows

```powershell
# Build Windows executable
pyinstaller --onefile --windowed --name c2-phantom-gui c2_phantom/cli.py

# Create installer with NSIS
makensis installer.nsi
```

### Linux

```bash
# Build Linux binary
pyinstaller --onefile --name c2-phantom c2_phantom/cli.py

# Create .deb package
dpkg-deb --build c2-phantom_1.0.0_amd64

# Create .rpm package
rpmbuild -ba c2-phantom.spec
```

### macOS

```bash
# Build macOS application
pyinstaller --onefile --name c2-phantom --icon=assets/icon.icns c2_phantom/cli.py

# Create .dmg
hdiutil create -volname "C2 Phantom" -srcfolder dist/c2-phantom.app -ov -format UDZO c2-phantom.dmg
```
