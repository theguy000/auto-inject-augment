# Quick Start Guide

## For Users: Install Pre-Built Extension

### Option 1: Download from Releases

1. Go to [Releases](../../releases)
2. Download the latest `augment-privacy-protected-{version}.vsix`
3. Install in VSCode:
   ```bash
   code --install-extension augment-privacy-protected-{version}.vsix
   ```

### Option 2: Install via VSCode UI

1. Open VSCode
2. Go to Extensions (`Ctrl+Shift+X` or `Cmd+Shift+X`)
3. Click `...` menu → `Install from VSIX...`
4. Select the downloaded `.vsix` file

### Verify Installation

1. Open VSCode Developer Console:
   - Windows/Linux: `Ctrl+Shift+I`
   - macOS: `Cmd+Option+I`

2. Run these commands:
   ```javascript
   navigator.deviceMemory        // Should show random value (2-32)
   navigator.hardwareConcurrency // Should show random value (2-32)
   window.__getSpoofedMachineId() // Should return UUID
   ```

3. Restart VSCode and check again - values should be different!

## For Developers: Build Locally

### Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 18 or higher
- **npm**: Latest version
- **Git**: For cloning repository

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd auto-inject-augment
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install vsce (VSCode Extension Manager)**
   ```bash
   npm install -g @vscode/vsce
   ```

4. **Run Build**
   ```bash
   python build.py
   ```

   This will:
   - Download latest Augment extension
   - Extract VSIX contents
   - Inject privacy protection
   - Run verification tests
   - Package modified VSIX

5. **Install Built Extension**
   ```bash
   code --install-extension output/augment-privacy-protected-*.vsix
   ```

### Build Output

```
auto-inject-augment/
├── download/              # Downloaded original VSIX
├── extracted/             # Extracted extension files
├── output/                # Final privacy-protected VSIX
└── logs/                  # Build logs
```

## Testing

### Run Verification Tests

```bash
python -m pytest tests/ -v
```

Tests verify:
- ✅ `device-spoofer.js` exists
- ✅ All 12 HTML files modified
- ✅ Script loads before telemetry
- ✅ Correct nonce attribute
- ✅ Privacy comment present

### Manual Testing

1. **Install Extension**
   ```bash
   code --install-extension output/augment-privacy-protected-*.vsix
   ```

2. **Open Developer Console**
   - `Ctrl+Shift+I` (Windows/Linux)
   - `Cmd+Option+I` (macOS)

3. **Check Spoofed Values**
   ```javascript
   // Hardware spoofing
   navigator.deviceMemory        // Random: 2, 4, 8, 16, or 32
   navigator.hardwareConcurrency // Random: 2-32 cores
   navigator.platform            // Random: Win32, MacIntel, or Linux x86_64
   
   // Screen spoofing
   screen.width                  // Random resolution
   screen.height                 // Random resolution
   
   // Machine ID
   window.__getSpoofedMachineId() // UUID format
   
   // Full fingerprint
   window.__deviceSpoofer.getFingerprint()
   ```

4. **Restart VSCode**
   - Close and reopen VSCode
   - Check values again - they should be different!

## Troubleshooting

### Build Fails

**Error**: `vsce command not found`
```bash
npm install -g @vscode/vsce
```

**Error**: `Python module not found`
```bash
pip install -r requirements.txt
```

**Error**: `Download failed`
- Check internet connection
- Try again (marketplace may be temporarily unavailable)

### Installation Fails

**Error**: `Extension is not compatible`
- Check VSCode version (requires 1.82.0+)
- Update VSCode to latest version

**Error**: `Extension already installed`
```bash
# Uninstall existing version first
code --uninstall-extension augment.vscode-augment
# Then install privacy-protected version
code --install-extension output/augment-privacy-protected-*.vsix
```

### Spoofing Not Working

**Check 1**: Verify script is loaded
```javascript
// Should return object
window.__deviceSpoofer
```

**Check 2**: Check for errors
- Open Developer Console
- Look for red error messages
- Check if CSP violations reported

**Check 3**: Verify HTML injection
- Extract VSIX: `unzip output/augment-privacy-protected-*.vsix`
- Check `extension/common-webviews/main-panel.html`
- Should contain: `<script src="../privacy-protection/device-spoofer.js"`

## Advanced Usage

### Enable Debug Mode

1. Extract VSIX
2. Edit `extension/privacy-protection/device-spoofer.js`
3. Change `DEBUG_MODE: false` to `DEBUG_MODE: true`
4. Repackage VSIX
5. Reinstall extension

Console will show:
```
[DeviceSpoofer] Generated new fingerprint: {...}
[DeviceSpoofer] Spoofed navigator.deviceMemory: 16
[DeviceSpoofer] ✓ Device Fingerprint Spoofer activated
```

### Regenerate Fingerprint

Without restarting VSCode:

```javascript
window.__deviceSpoofer.regenerate()
```

### Customize Spoofing Ranges

Edit `privacy-protection/device-spoofer.js`:

```javascript
const CONFIG = {
  DEVICE_MEMORY_OPTIONS: [4, 8, 16],  // Only 4-16 GB
  HARDWARE_CONCURRENCY_OPTIONS: [4, 8, 12],  // Only 4-12 cores
  // ...
};
```

## GitHub Actions (For Repository Maintainers)

### Automatic Builds

Every push to `main` branch triggers:
1. Download latest Augment extension
2. Inject privacy protection
3. Run tests
4. Create GitHub Release
5. Upload VSIX artifact

### Manual Trigger

1. Go to Actions tab
2. Select "Build and Release" workflow
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow" button

### Release Naming

Releases are tagged as:
```
v{version}-privacy
```

Example: `v0.585.0-privacy`

## Next Steps

- Read [TECHNICAL.md](TECHNICAL.md) for implementation details
- Check [README.md](README.md) for full documentation
- Report issues on [GitHub Issues](../../issues)

## Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Documentation**: [README.md](README.md) and [TECHNICAL.md](TECHNICAL.md)

