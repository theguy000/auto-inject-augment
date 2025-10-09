# Augment VSCode Extension - Privacy Protected Auto-Build

[![Build and Release](https://github.com/theguy000/auto-inject-augment/actions/workflows/build-release.yml/badge.svg)](https://github.com/theguy000/auto-inject-augment/actions/workflows/build-release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository automatically downloads the latest Augment VSCode extension, injects privacy protection (device fingerprint spoofing), and creates a modified VSIX package.

## 🎯 What This Does

1. **Downloads** the latest Augment extension from VS Marketplace
2. **Injects** privacy protection code directly into `extension.js`
3. **Packages** a privacy-protected VSIX file
4. **Releases** automatically on every push to main branch

## 📊 Status

- **Latest Augment Version**: 0.585.0
- **Build Status**: Check [Actions](https://github.com/theguy000/auto-inject-augment/actions) tab
- **Latest Release**: [Releases](https://github.com/theguy000/auto-inject-augment/releases)

## 🔒 Privacy Protection Features

- **Device Fingerprint Spoofing**: Randomizes hardware identifiers
- **Cross-Account Tracking Prevention**: Different fingerprint per session
- **Session ID Randomization**: Prevents session correlation
- **Request Interception**: Modifies telemetry data in transit
- **System Command Spoofing**: Fakes hardware info from OS commands
- **Deep Integration**: Injected at extension entry point (runs first)

### What Gets Spoofed

#### Device Identifiers
- **Machine ID**: Windows GUID, macOS IOPlatformUUID, Linux machine-id
- **Serial Numbers**: Product ID, IOPlatformSerialNumber
- **Board ID**: Mac board identifier

#### Session & Network
- **Session IDs**: UUID v4 format, randomized per session
- **Request Headers**: `x-request-session-id` header spoofing
- **Telemetry Data**: Chat blobs, feature vectors

#### System Commands
- **macOS**: `ioreg` output (IOPlatformUUID, IOPlatformSerialNumber, board-id)
- **Windows**: `REG.exe`, `wmic`, `systeminfo` output
- **Git**: Command output suppression

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

After installing, you can verify the injection worked:

### Check Injection Marker
Open `extension/extension.js` in the installed extension:
```bash
# Find extension location
code --list-extensions --show-versions | grep augment

# On Windows
%USERPROFILE%\.vscode\extensions\augment.vscode-augment-*\extension\extension.js

# On macOS/Linux
~/.vscode/extensions/augment.vscode-augment-*/extension/extension.js
```

The file should start with:
```javascript
// __AUG_INIT
(function(){
  const cfg = 'CihmdW5jdGlvbigpIHsK...';
  // ...
})();
```

### Runtime Verification
The privacy protection runs automatically when the extension loads. Check VSCode's Output panel (View → Output → Augment) for any errors. If the extension loads normally, privacy protection is active.

Each time you restart VSCode, device fingerprints and session IDs will be randomized.

## 📁 Repository Structure

```
auto-inject-augment/
├── .github/
│   └── workflows/
│       └── build-release.yml    # Auto-build on push
├── scripts/
│   ├── download_extension.py    # Downloads latest VSIX
│   ├── extract_vsix.py          # Extracts VSIX contents
│   ├── inject_privacy.py        # Injects into extension.js
│   ├── package_vsix.py          # Packages modified extension
│   └── compare_character_counts.py  # Diff analysis
├── privacy-protection/
│   ├── device-spoofer.js        # Privacy protection (readable)
│   ├── test.js                  # Minified injection payload
│   └── diff_summary.md          # Quick reference
├── output/
│   ├── diff_summary.md          # Detailed technical docs
│   └── *.vsix                   # Generated packages
├── tests/
│   └── test_injection.py        # Verifies extension.js injection
├── build.py                     # Main build orchestrator
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔄 Automated Workflow

On every push to `main` branch:

1. GitHub Actions triggers
2. Downloads latest Augment extension
3. Extracts VSIX contents
4. Injects privacy protection into `extension/extension.js`
5. Runs verification tests
6. Packages modified VSIX
7. Creates GitHub Release with artifact

## 🧩 How It Works

### 1. Download Phase
```python
# Uses VS Marketplace API to get latest version
download_extension.py --publisher augment --extension vscode-augment
```

### 2. Extraction Phase
```python
# Extracts VSIX (ZIP format) to extracted/ directory
extract_vsix.py
```

### 3. Injection Phase
```python
# Injects privacy protection into extension.js
inject_privacy.py
```

**What Gets Injected:**

The script reads `privacy-protection/test.js`, Base64-encodes it, and prepends this to `extension/extension.js`:

```javascript
// __AUG_INIT
(function(){
  const cfg = 'CihmdW5jdGlvbigpIHsKICBmdW5jdGlvbiBfX0FVR192YWxpZGF0ZUNvbmZpZygpIHsK...';
  const dec = (d) => Buffer.from(d, 'base64').toString('utf8');
  eval(dec(cfg));
})();

// Original extension code follows...
```

**How It Works:**
1. Self-executing function runs when extension loads
2. Decodes Base64 payload using `Buffer.from()`
3. Executes decoded code using `eval()`
4. Decoded code hooks into Node.js modules (`http`, `https`, `child_process`)
5. Intercepts and spoofs device identifiers, session IDs, and telemetry

**Modified File:**
- `extension/extension.js` (+7 lines at the beginning)

### 4. Packaging Phase
```bash
# Uses vsce to create VSIX
vsce package --no-dependencies --out augment-privacy-protected-{version}.vsix
```

## 🧪 Testing

```bash
# Run verification tests
python -m pytest tests/ -v

# Tests verify:
# - extension.js has // __AUG_INIT marker
# - Injection is at beginning of file
# - Base64 payload is present and valid
# - Self-executing function structure is correct
# - Decoded payload contains all privacy features
```

## 🛠️ Development

### Modify Privacy Protection Logic

Edit `privacy-protection/test.js` to change the injected code:

```javascript
// This file contains the actual privacy protection code
// It gets Base64-encoded and injected into extension.js

function __AUG_validateConfig() {
  // Validation logic
}

// Add your custom spoofing logic here
```

After modifying, rebuild:
```bash
python build.py
```

### Update Validation Expiration

The injection has a time-based validation. To update:

1. Generate new timestamp:
   ```javascript
   // JavaScript console
   Date.now()  // e.g., 1759479478344
   ```

2. Create config string:
   ```javascript
   btoa('active:1759479478344')  // Base64 encode
   ```

3. Update in `privacy-protection/test.js`:
   ```javascript
   function __AUG_validateConfig() {
     const cfg = "YOUR_NEW_BASE64_STRING";
     // ...
   }
   ```

### Debug Injection

Enable debug mode by modifying the decoded payload to log activity:
```javascript
// In test.js, add console.log statements
console.log('[Privacy] Session ID:', __AUG_SESSION_ID);
console.log('[Privacy] Fake Machine ID:', __AUG_FAKE.windowsGuid);
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

- **Deep Integration**: Injected at extension entry point (runs before any extension code)
- **Module Hooking**: Intercepts Node.js core modules (`http`, `https`, `child_process`)
- **Request Modification**: Alters outgoing requests before they leave
- **Command Spoofing**: Fakes system command outputs
- **Session-Based**: New fingerprint per VSCode session
- **Base64 Obfuscation**: Payload encoded to avoid casual detection
- **Time-Based Validation**: Optional expiration mechanism

## 📚 Technical Details

See documentation for detailed information:
- **[output/diff_summary.md](output/diff_summary.md)**: Complete technical documentation
- **[privacy-protection/diff_summary.md](privacy-protection/diff_summary.md)**: Quick reference guide
- **[TECHNICAL.md](TECHNICAL.md)**: Original design rationale (may be outdated)

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

