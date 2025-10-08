# Technical Documentation - Privacy Protection Implementation

## Overview

This document provides detailed technical information about the device fingerprint spoofing implementation for the Augment VSCode extension.

## Architecture

### Components

1. **device-spoofer.js**: Core spoofing module (522 lines)
2. **Injection Scripts**: Python scripts to modify HTML files
3. **Build Pipeline**: Automated download, extract, inject, test, package
4. **GitHub Actions**: CI/CD for automated releases

### Data Flow

```
Download VSIX → Extract → Inject Privacy Script → Test → Package → Release
```

## Device Fingerprinting Analysis

### What Augment Tracks

Based on analysis of `extension/common-webviews/assets/initialize-CXNwi7OG.js` (Sentry SDK):

1. **Hardware Identifiers**
   - `navigator.deviceMemory` - RAM in GB
   - `navigator.hardwareConcurrency` - CPU core count
   - `navigator.platform` - OS platform

2. **Screen Information**
   - `screen.width` / `screen.height` - Display resolution
   - `screen.colorDepth` - Color bit depth

3. **Network Data**
   - `navigator.connection.effectiveType` - Connection speed
   - `navigator.connection.rtt` - Round-trip time
   - `navigator.connection.downlink` - Download speed

4. **Machine ID**
   - Platform-specific unique identifier
   - Persists across browser sessions

5. **Timezone**
   - `Date.prototype.getTimezoneOffset()`
   - Timezone string

### Cross-Account Tracking

Combination of these values creates a unique fingerprint:

```
Fingerprint = Hash(MachineID + RAM + CPU + Screen + Timezone + Platform)
```

This fingerprint persists even when:
- Using different Augment accounts
- Clearing browser data
- Using incognito mode

## Spoofing Mechanism

### Approach: API Interception

We intercept at the JavaScript API level using `Object.defineProperty()`:

```javascript
Object.defineProperty(navigator, 'deviceMemory', {
  get: () => spoofedValue,
  configurable: true,
  enumerable: true
});
```

### Why Not Code Modification?

The Sentry SDK (`initialize-CXNwi7OG.js`) is:
- **Minified**: Single line, no whitespace
- **Bundled**: Webpack/Rollup output
- **No Source Maps**: Cannot map to original code
- **Fragile**: Any edit breaks the extension

### Advantages of API Interception

1. **Safe**: No modification of original code
2. **Stable**: Works across Augment updates
3. **Effective**: Sentry SDK reads spoofed values
4. **Undetectable**: Appears as normal API calls

## Implementation Details

### Fingerprint Generation

```javascript
class DeviceFingerprintGenerator {
  generate() {
    return {
      deviceMemory: randomChoice([2, 4, 8, 16, 32]),
      hardwareConcurrency: randomChoice([2, 4, 6, 8, 12, 16, 24, 32]),
      machineId: generateUUID(),
      platform: randomChoice(['Win32', 'MacIntel', 'Linux x86_64']),
      screenWidth: randomChoice([1920, 2560, 3840, ...]),
      screenHeight: randomChoice([1080, 1440, 2160, ...]),
      timezone: randomChoice(['America/New_York', 'Europe/London', ...]),
      // ... more properties
    };
  }
}
```

### Realistic Value Correlation

CPU cores correlate with RAM to avoid impossible combinations:

```javascript
// If RAM >= 16GB, allow up to 32 cores
// If RAM >= 8GB, allow up to 16 cores
// Otherwise, max 8 cores
const maxCores = deviceMemory >= 16 ? 32 : deviceMemory >= 8 ? 16 : 8;
```

### Session Persistence

Fingerprint persists during VSCode session using `sessionStorage`:

```javascript
sessionStorage.setItem('augment_spoofed_fingerprint', JSON.stringify(fingerprint));
```

New fingerprint generated on:
- VSCode restart
- Browser session end
- Manual regeneration

## Injection Process

### HTML Modification

Script tag injected after `</title>` tag:

```html
<head>
  <title>Augment</title>
  <!-- PRIVACY PROTECTION: Load device spoofer FIRST before any telemetry -->
  <script src="../privacy-protection/device-spoofer.js" nonce="nonce-NdJS6eXuvR9e2+J/eS0faQ=="></script>
  <!-- Other scripts... -->
</head>
```

### Load Order Guarantee

1. `device-spoofer.js` loads FIRST
2. Spoofing activates immediately
3. Sentry SDK loads AFTER
4. Sentry reads spoofed values

### Content Security Policy (CSP)

Script tag includes nonce for CSP compliance:

```html
nonce="nonce-NdJS6eXuvR9e2+J/eS0faQ=="
```

This matches the CSP nonce used by other scripts in the HTML files.

## Testing

### Verification Tests

1. **File Existence**: `device-spoofer.js` in `privacy-protection/`
2. **HTML Injection**: All 12 HTML files contain script tag
3. **Load Order**: Spoofer loads before telemetry scripts
4. **Nonce Attribute**: Correct CSP nonce present
5. **Comment Presence**: Privacy protection comment exists

### Manual Verification

Open VSCode Developer Console:

```javascript
// Check spoofed values
navigator.deviceMemory        // Should be random (2-32)
navigator.hardwareConcurrency // Should be random (2-32)
navigator.platform            // Should be spoofed

// Get Machine ID
window.__getSpoofedMachineId() // Returns UUID

// Access spoofer instance
window.__deviceSpoofer.getFingerprint() // Full fingerprint object
```

## Build Pipeline

### Automated Workflow

```yaml
1. Download latest VSIX from VS Marketplace
2. Extract VSIX contents (ZIP archive)
3. Copy device-spoofer.js to extension/privacy-protection/
4. Inject script tags into 12 HTML files
5. Run pytest verification tests
6. Package modified extension with vsce
7. Create GitHub Release with VSIX artifact
```

### GitHub Actions Triggers

- **Push to main**: Automatic build and release
- **Manual dispatch**: On-demand build

### Version Handling

Version extracted from downloaded VSIX filename:

```
augment.vscode-augment-0.585.0.vsix → 0.585.0
```

Release tagged as:

```
v0.585.0-privacy
```

## Security Considerations

### What's Protected

✅ Device fingerprinting via hardware specs
✅ Cross-account tracking via Machine ID
✅ Screen resolution tracking
✅ Timezone-based tracking

### What's NOT Protected

❌ IP address tracking (network level)
❌ Account-based tracking (login credentials)
❌ Code execution tracking (extension behavior)
❌ File access patterns

### Privacy Model

```
Layer 1: Account (Login credentials) - NOT PROTECTED
Layer 2: Device (Hardware fingerprint) - PROTECTED ✓
Layer 3: Network (IP address) - NOT PROTECTED
```

## Performance Impact

- **Load Time**: +5-10ms (script execution)
- **Memory**: +50KB (fingerprint storage)
- **CPU**: Negligible (one-time generation)
- **Runtime**: No ongoing performance impact

## Compatibility

### Tested Platforms

- ✅ Windows 10/11
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu, Fedora)

### VSCode Versions

- ✅ VSCode 1.82.0+
- ✅ VSCode Insiders

### Augment Versions

- ✅ 0.585.0 (current)
- ⚠️ Future versions may require updates

## Maintenance

### When Augment Updates

1. GitHub Actions auto-downloads latest version
2. Injection process runs automatically
3. Tests verify successful injection
4. New release created

### If Tests Fail

Possible causes:
- New HTML files added (update `HTML_FILES` list)
- HTML structure changed (update injection logic)
- CSP nonce changed (update `SCRIPT_TAG`)

### Updating Spoofing Logic

Edit `privacy-protection/device-spoofer.js`:

```javascript
const CONFIG = {
  DEBUG_MODE: false,  // Set true for debugging
  DEVICE_MEMORY_OPTIONS: [2, 4, 8, 16, 32],  // Modify ranges
  // ...
};
```

## Debugging

### Enable Debug Mode

Edit `device-spoofer.js`:

```javascript
const CONFIG = {
  DEBUG_MODE: true,  // Enable logging
  // ...
};
```

Console output:

```
[DeviceSpoofer] Generated new fingerprint: {...}
[DeviceSpoofer] Spoofed navigator.deviceMemory: 16
[DeviceSpoofer] Spoofed navigator.hardwareConcurrency: 12
[DeviceSpoofer] ✓ Device Fingerprint Spoofer activated
```

### Common Issues

**Issue**: Script not loading
- Check: HTML file contains script tag
- Check: `device-spoofer.js` exists in `privacy-protection/`

**Issue**: Values not spoofed
- Check: Script loads BEFORE telemetry scripts
- Check: No JavaScript errors in console

**Issue**: CSP violation
- Check: Nonce attribute matches other scripts
- Check: CSP header allows script execution

## References

- [Sentry SDK Documentation](https://docs.sentry.io/platforms/javascript/)
- [Navigator API](https://developer.mozilla.org/en-US/docs/Web/API/Navigator)
- [Object.defineProperty()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)

## Contributing

See main [README.md](README.md) for contribution guidelines.

## License

MIT License - See [LICENSE](LICENSE) file

