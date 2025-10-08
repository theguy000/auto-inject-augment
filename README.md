# Augment VSCode Extension - Privacy Protected Auto-Build

[![Build and Release](https://github.com/theguy000/auto-inject-augment/actions/workflows/build-release.yml/badge.svg)](https://github.com/theguy000/auto-inject-augment/actions/workflows/build-release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository automatically downloads the latest Augment VSCode extension, injects privacy protection (device fingerprint spoofing), and creates a modified VSIX package.

## 🎯 What This Does

1. **Downloads** the latest Augment extension from VS Marketplace
2. **Injects** device fingerprint spoofing into all HTML webviews
3. **Packages** a privacy-protected VSIX file
4. **Releases** automatically on every push to main branch

## 📊 Status

- **Latest Augment Version**: 0.585.0
- **Build Status**: Check [Actions](https://github.com/theguy000/auto-inject-augment/actions) tab
- **Latest Release**: [Releases](https://github.com/theguy000/auto-inject-augment/releases)

## 🔒 Privacy Protection Features

- **Device Fingerprint Spoofing**: Randomizes hardware identifiers
- **Cross-Account Tracking Prevention**: Different fingerprint per session
- **Realistic Values**: Generates believable device specs
- **No Code Modification**: Intercepts at API level (safe & stable)

### What Gets Spoofed

- Machine ID (UUID format)
- RAM (deviceMemory): 2-32 GB
- CPU cores (hardwareConcurrency): 2-32 cores
- Screen resolution: Various realistic sizes
- Timezone: 12 global options
- Platform: Win32/MacIntel/Linux
- Network connection type/speed

## 🚀 Quick Start

### Option 1: Install Pre-Built Release (Recommended)

1. Go to [Releases](https://github.com/theguy000/auto-inject-augment/releases)
2. Download the latest `augment-privacy-protected-{version}.vsix`
3. Install in VSCode:
   ```bash
   code --install-extension augment-privacy-protected-{version}.vsix
   ```
   Or via VSCode UI: Extensions → `...` menu → Install from VSIX

### Option 2: Build Locally

```bash
# Clone repository
git clone <repo-url>
cd auto-inject-augment

# Install dependencies
pip install -r requirements.txt
npm install -g @vscode/vsce

# Run build script
python build.py

# Install the generated VSIX
code --install-extension output/augment-privacy-protected-*.vsix
```

## 🧪 Verify Privacy Protection

After installing, open VSCode Developer Console (`Ctrl+Shift+I` or `Cmd+Option+I`):

```javascript
// Check spoofed values
navigator.deviceMemory        // Should show random value (2-32)
navigator.hardwareConcurrency // Should show random value (2-32)
navigator.platform            // Should show spoofed platform

// Check Machine ID spoofing
window.__getSpoofedMachineId() // Should return UUID
```

Each time you restart VSCode, these values will be different.

## 📁 Repository Structure

```
auto-inject-augment/
├── .github/
│   └── workflows/
│       └── build-release.yml    # Auto-build on push
├── scripts/
│   ├── download_extension.py    # Downloads latest VSIX
│   ├── inject_privacy.py        # Injects device-spoofer.js
│   └── package_vsix.py          # Packages modified extension
├── privacy-protection/
│   └── device-spoofer.js        # Privacy protection script
├── tests/
│   └── test_injection.py       # Verifies HTML modifications
├── build.py                     # Main build orchestrator
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔄 Automated Workflow

On every push to `main` branch:

1. GitHub Actions triggers
2. Downloads latest Augment extension
3. Extracts VSIX contents
4. Injects `device-spoofer.js` into all HTML files
5. Runs verification tests
6. Packages modified VSIX
7. Creates GitHub Release with artifact

## 🧩 How It Works

### 1. Download Phase
```python
# Uses VS Marketplace API to get latest version
download_extension.py --publisher augment --extension vscode-augment
```

### 2. Injection Phase
```python
# Injects privacy script into 12 HTML files
inject_privacy.py --input extracted/ --output modified/
```

**Modified Files:**
- `main-panel.html`
- `index.html`
- `settings.html`
- `secrets-home.html`
- `memories.html`
- `history.html`
- `diff-view.html`
- `rules.html`
- `preference.html`
- `remote-agent-home.html`
- `remote-agent-diff.html`
- `next-edit-suggestions.html`

**Injection Point:**
```html
<head>
  <title>Augment</title>
  <!-- PRIVACY PROTECTION: Load device spoofer FIRST before any telemetry -->
  <script src="../privacy-protection/device-spoofer.js" nonce="nonce-NdJS6eXuvR9e2+J/eS0faQ=="></script>
  <!-- Rest of scripts... -->
</head>
```

### 3. Packaging Phase
```bash
# Uses vsce to create VSIX
vsce package --no-dependencies --out augment-privacy-protected-{version}.vsix
```

## 🧪 Testing

```bash
# Run verification tests
python -m pytest tests/

# Tests verify:
# - device-spoofer.js exists
# - All 12 HTML files contain injection
# - Script tag is FIRST (before telemetry)
# - Correct nonce attribute
```

## 🛠️ Development

### Add New HTML File

If Augment adds new webview HTML files:

1. Update `inject_privacy.py`:
   ```python
   HTML_FILES = [
       'main-panel.html',
       'new-file.html',  # Add here
       # ...
   ]
   ```

2. Update `test_injection.py`:
   ```python
   def test_all_html_files_modified():
       expected_files = [
           'main-panel.html',
           'new-file.html',  # Add here
           # ...
       ]
   ```

### Modify Spoofing Logic

Edit `privacy-protection/device-spoofer.js`:

```javascript
const CONFIG = {
  DEBUG_MODE: false,  // Set true for logging
  DEVICE_MEMORY_OPTIONS: [2, 4, 8, 16, 32],
  // Modify ranges as needed
};
```

## 📋 Requirements

- **Python**: 3.8+
- **Node.js**: 18+
- **npm**: Latest
- **vsce**: `npm install -g @vscode/vsce`

## ⚠️ Important Notes

1. **No Warranty**: Use at your own risk
2. **Extension Updates**: Workflow auto-downloads latest version
3. **Breaking Changes**: Augment updates may require script adjustments
4. **Testing**: Always test in isolated environment first
5. **Compliance**: Ensure usage complies with Augment's terms of service

## 🔐 Security Considerations

- **API Interception**: Spoofing happens at JavaScript API level
- **No Code Modification**: Original Sentry/telemetry code unchanged
- **Session-Based**: New fingerprint per VSCode session
- **Realistic Values**: Avoids detection via impossible combinations

## 📚 Technical Details

See [TECHNICAL.md](TECHNICAL.md) for:
- Detailed spoofing mechanism
- Sentry SDK analysis
- Telemetry tracking breakdown
- Cross-account tracking prevention

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🙏 Credits

- **Original Extension**: [Augment Code](https://marketplace.visualstudio.com/items?itemName=augment.vscode-augment)
- **Privacy Protection**: Community contribution
- **Automation**: GitHub Actions

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

---

**Disclaimer**: This is an unofficial modification. Not affiliated with Augment.

