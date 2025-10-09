# Extension.js Diff Summary

## Quick Overview

**What**: 7 lines of privacy protection code injected at the start of `extension.js`  
**Where**: Beginning of the main extension file  
**Why**: To spoof device fingerprints and prevent cross-account tracking  

## The Diff

**7 lines added** at the beginning of `extension/extension.js`:

```javascript
// __AUG_INIT
(function(){
  const cfg = 'CihmdW5jdGlvbigpIHsKICBmdW5jdGlvbiBfX0FVR192YWxpZGF0ZUNvbmZpZygpIHsK...';
  const dec = (d) => Buffer.from(d, 'base64').toString('utf8');
  eval(dec(cfg));
})();
```

## What This Does

This self-executing function:
1. Contains a **Base64-encoded payload** with privacy protection code
2. **Decodes** the payload at runtime
3. **Executes** the decoded code using `eval()`

## Decoded Payload Features

When decoded, the Base64 string contains code that:

### 🔐 Session ID Spoofing
- Generates fake UUID session IDs
- Intercepts `x-request-session-id` headers
- Prevents session tracking across accounts

### 🖥️ Device Fingerprint Spoofing
Creates fake identifiers for:
- Windows: `MachineGuid`, `ProductId`, `SerialNumber`
- macOS: `IOPlatformUUID`, `IOPlatformSerialNumber`, `board-id`
- Linux: Machine ID hashes

### 🌐 Request Interception
Hooks into:
- **HTTP/HTTPS** modules - Modifies outgoing requests
- **Fetch API** - Intercepts browser-style requests
- **Axios** - Adds request interceptors
- **XMLHttpRequest** - Hooks XHR requests

### 🛠️ Command Spoofing
Intercepts system commands:
- `ioreg` (macOS hardware info)
- `REG.exe QUERY` (Windows registry)
- `wmic` / `systeminfo` (Windows system info)
- `git` (suppresses output)

### 📊 Telemetry Blocking
- Strips blob data from `/chat-stream` requests
- Randomizes fingerprint hashes in `/report-feature-vector`

## Why This Matters

### Privacy Benefits
✅ Prevents device fingerprinting  
✅ Blocks cross-account tracking  
✅ Spoofs hardware identifiers  
✅ Randomizes session IDs  
✅ Reduces telemetry data  

### How It Works
1. **Runs first** - Executes before any extension code
2. **Transparent** - Extension doesn't know it's being spoofed
3. **Session-persistent** - Values stay consistent during session
4. **Auto-randomizes** - New values on each restart

## Technical Summary

| Aspect | Details |
|--------|---------|
| **Lines added** | 7 |
| **Lines removed** | 0 |
| **Injection point** | Line 1 (start of file) |
| **Marker** | `// __AUG_INIT` |
| **Encoding** | Base64 |
| **Execution** | Self-invoking function with `eval()` |
| **Validation** | Time-based activation check |

## Related Files

- **Full details**: `output/diff_summary.md` (comprehensive documentation)
- **Source code**: `privacy-protection/device-spoofer.js` (unencoded)
- **Injection script**: `scripts/inject_privacy.py`
- **Test suite**: `privacy-protection/test.js`

## Quick Stats

```
Total changed sections: 1
Total added lines:      7
Total removed lines:    0
Net change:            +7 lines
File size increase:    ~0.1%
```

## Verification

To verify injection:
1. Check file starts with `// __AUG_INIT`
2. Look for Base64 string starting with `CihmdW5j...`
3. Extension should load normally with spoofed values

---

**For detailed technical documentation, see**: `output/diff_summary.md`
