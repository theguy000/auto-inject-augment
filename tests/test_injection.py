"""
Test suite for privacy protection injection into extension.js.

Verifies that:
1. extension.js has been modified with privacy protection code
2. Injection marker (// __AUG_INIT) is present
3. Base64 encoded payload is present
4. Injection is at the beginning of the file
5. Self-executing function structure is correct
6. Privacy protection code contains all required features
"""

import pytest
from pathlib import Path
import re
import base64


class TestExtensionJsInjection:
    """Test privacy protection injection into extension.js."""
    
    @pytest.fixture
    def extension_js_path(self):
        """Get extension.js file path."""
        return Path("extracted/extension/out/extension.js")
    
    @pytest.fixture
    def extension_js_content(self, extension_js_path):
        """Get extension.js content."""
        assert extension_js_path.exists(), f"extension.js not found at {extension_js_path}"
        return extension_js_path.read_text(encoding='utf-8')
    
    def test_extension_js_exists(self, extension_js_path):
        """Test that extension.js exists."""
        assert extension_js_path.exists(), f"extension.js not found at {extension_js_path}"
    
    def test_injection_marker_present(self, extension_js_content):
        """Test that // __AUG_INIT marker is present."""
        assert '// __AUG_INIT' in extension_js_content, \
            "Injection marker // __AUG_INIT not found"
    
    def test_injection_at_beginning(self, extension_js_content):
        """Test that injection is at the very beginning of the file."""
        first_line = extension_js_content.split('\n')[0]
        assert first_line == '// __AUG_INIT', \
            f"File must start with // __AUG_INIT marker, got: {first_line[:50]}"
    
    def test_self_executing_function_structure(self, extension_js_content):
        """Test that self-executing function structure is correct."""
        # Should have (function(){ ... })();
        assert '(function(){' in extension_js_content or '(function() {' in extension_js_content, \
            "Self-executing function not found"
        
        # Check for closing })();
        lines = extension_js_content.split('\n')
        found_closing = False
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            if '})();' in line:
                found_closing = True
                break
        
        assert found_closing, "Self-executing function closing })(); not found in first 20 lines"
    
    def test_base64_config_present(self, extension_js_content):
        """Test that Base64 encoded config is present."""
        assert "const cfg = '" in extension_js_content, \
            "Base64 config declaration not found"
        
        # Extract the Base64 string
        match = re.search(r"const cfg = '([A-Za-z0-9+/=]+)';", extension_js_content)
        assert match is not None, "Could not extract Base64 config string"
        
        base64_string = match.group(1)
        assert len(base64_string) > 100, \
            f"Base64 string too short ({len(base64_string)} chars), expected > 100"
    
    def test_decoder_function_present(self, extension_js_content):
        """Test that decoder function is present."""
        # Should have: const dec = (d) => Buffer.from(d, 'base64').toString('utf8');
        assert 'const dec = ' in extension_js_content, \
            "Decoder function declaration not found"
        
        assert "Buffer.from" in extension_js_content, \
            "Buffer.from() not found in decoder"
        
        assert "'base64'" in extension_js_content or '"base64"' in extension_js_content, \
            "base64 encoding parameter not found"
        
        assert "'utf8'" in extension_js_content or '"utf8"' in extension_js_content, \
            "utf8 encoding parameter not found"
    
    def test_eval_execution_present(self, extension_js_content):
        """Test that eval() execution is present."""
        assert 'eval(dec(cfg))' in extension_js_content, \
            "eval(dec(cfg)) execution not found"
    
    def test_injection_size(self, extension_js_content):
        """Test that injection adds approximately 7 lines."""
        lines = extension_js_content.split('\n')
        
        # Find the end of injection (empty line after })();)
        injection_end = 0
        for i, line in enumerate(lines):
            if '})();' in line:
                injection_end = i + 1
                break
        
        assert injection_end > 0, "Could not find end of injection"
        assert injection_end <= 10, \
            f"Injection too large ({injection_end} lines), expected ~7 lines"
    
    def test_original_code_preserved(self, extension_js_content):
        """Test that original extension code is preserved after injection."""
        # Original code should start with "use strict" or similar
        lines = extension_js_content.split('\n')
        
        # Find first line after injection
        found_original = False
        for i, line in enumerate(lines):
            if i > 0 and ('"use strict"' in line or "'use strict'" in line or 'var ' in line or 'Object.create' in line):
                found_original = True
                break
        
        assert found_original, "Original extension code not found after injection"


class TestDecodedPayload:
    """Test the decoded privacy protection payload."""
    
    @pytest.fixture
    def extension_js_content(self):
        """Get extension.js content."""
        path = Path("extracted/extension/extension.js")
        return path.read_text(encoding='utf-8')
    
    @pytest.fixture
    def decoded_payload(self, extension_js_content):
        """Extract and decode the Base64 payload."""
        match = re.search(r"const cfg = '([A-Za-z0-9+/=]+)';", extension_js_content)
        assert match is not None, "Could not extract Base64 config"
        
        base64_string = match.group(1)
        decoded = base64.b64decode(base64_string).decode('utf-8')
        return decoded
    
    def test_validation_function_present(self, decoded_payload):
        """Test that __AUG_validateConfig function is present."""
        assert '__AUG_validateConfig' in decoded_payload, \
            "Validation function not found in decoded payload"
    
    def test_session_id_spoofing(self, decoded_payload):
        """Test that session ID spoofing code is present."""
        assert '__AUG_SESSION_ID' in decoded_payload, \
            "Session ID spoofing not found"
        
        assert 'x-request-session-id' in decoded_payload, \
            "Session ID header interception not found"
    
    def test_device_fingerprint_spoofing(self, decoded_payload):
        """Test that device fingerprint spoofing is present."""
        assert '__AUG_FAKE' in decoded_payload, \
            "Device fingerprint spoofing object not found"
        
        # Check for specific spoofed values
        assert 'windowsGuid' in decoded_payload, "Windows GUID spoofing not found"
        assert 'productId' in decoded_payload, "Product ID spoofing not found"
        assert 'serialNumber' in decoded_payload, "Serial number spoofing not found"
        assert 'ioPlatformUUID' in decoded_payload or 'ioplatformUUID' in decoded_payload, \
            "macOS UUID spoofing not found"
        assert 'boardId' in decoded_payload, "Board ID spoofing not found"
    
    def test_http_interception(self, decoded_payload):
        """Test that HTTP/HTTPS interception is present."""
        assert 'http' in decoded_payload or 'https' in decoded_payload, \
            "HTTP module interception not found"
        
        assert 'request' in decoded_payload, \
            "HTTP request interception not found"
    
    def test_child_process_interception(self, decoded_payload):
        """Test that child_process interception is present."""
        assert 'child_process' in decoded_payload, \
            "child_process module interception not found"
        
        assert 'exec' in decoded_payload, \
            "exec function interception not found"
        
        assert 'execSync' in decoded_payload, \
            "execSync function interception not found"
    
    def test_command_spoofing(self, decoded_payload):
        """Test that system command spoofing is present."""
        # macOS commands
        assert 'ioreg' in decoded_payload, \
            "ioreg command spoofing not found"
        
        # Windows commands
        assert 'REG.exe' in decoded_payload or 'reg query' in decoded_payload, \
            "Windows registry command spoofing not found"
        
        assert 'wmic' in decoded_payload or 'systeminfo' in decoded_payload, \
            "Windows system info command spoofing not found"
        
        # Git suppression
        assert 'git' in decoded_payload, \
            "Git command suppression not found"
    
    def test_request_modification(self, decoded_payload):
        """Test that request modification functions are present."""
        assert 'processInterceptedRequest' in decoded_payload, \
            "Request processing function not found"
        
        assert '/chat-stream' in decoded_payload, \
            "Chat stream endpoint interception not found"
        
        assert '/report-feature-vector' in decoded_payload, \
            "Feature vector endpoint interception not found"
    
    def test_axios_interception(self, decoded_payload):
        """Test that Axios interception is present."""
        assert 'axios' in decoded_payload, \
            "Axios interception not found"
        
        assert 'interceptors' in decoded_payload, \
            "Axios interceptors not found"
    
    def test_fetch_interception(self, decoded_payload):
        """Test that Fetch API interception is present."""
        assert 'fetch' in decoded_payload, \
            "Fetch API interception not found"
        
        assert 'originalFetch' in decoded_payload or '_fetchIntercepted' in decoded_payload, \
            "Fetch API hook not found"
    
    def test_xhr_interception(self, decoded_payload):
        """Test that XMLHttpRequest interception is present."""
        assert 'XMLHttpRequest' in decoded_payload, \
            "XMLHttpRequest interception not found"


class TestInjectionIntegrity:
    """Test injection integrity and structure."""
    
    def test_no_syntax_errors_in_injection(self):
        """Test that injection doesn't introduce syntax errors."""
        extension_js = Path("extracted/extension/extension.js")
        content = extension_js.read_text(encoding='utf-8')
        
        # Basic syntax checks
        # Count opening and closing braces in first 20 lines
        injection_lines = content.split('\n')[:20]
        injection_text = '\n'.join(injection_lines)
        
        open_braces = injection_text.count('{')
        close_braces = injection_text.count('}')
        
        # Should be balanced or close to balanced (within injection block)
        assert abs(open_braces - close_braces) <= 1, \
            f"Unbalanced braces in injection: {open_braces} open, {close_braces} close"
    
    def test_injection_is_compact(self):
        """Test that injection is compact (around 7 lines)."""
        extension_js = Path("extracted/extension/extension.js")
        content = extension_js.read_text(encoding='utf-8')
        
        lines = content.split('\n')
        
        # Count lines until we hit original code
        injection_lines = 0
        for i, line in enumerate(lines):
            if i == 0:
                continue  # Skip marker
            if line.strip() == '' and i > 5:
                injection_lines = i
                break
            if '"use strict"' in line or "'use strict'" in line:
                injection_lines = i
                break
        
        assert 5 <= injection_lines <= 10, \
            f"Injection size unexpected: {injection_lines} lines (expected 5-10)"
    
    def test_base64_is_valid(self):
        """Test that Base64 string is valid and can be decoded."""
        extension_js = Path("extracted/extension/extension.js")
        content = extension_js.read_text(encoding='utf-8')
        
        match = re.search(r"const cfg = '([A-Za-z0-9+/=]+)';", content)
        assert match is not None, "Could not extract Base64 string"
        
        base64_string = match.group(1)
        
        # Try to decode
        try:
            decoded = base64.b64decode(base64_string)
            decoded_str = decoded.decode('utf-8')
            assert len(decoded_str) > 0, "Decoded payload is empty"
        except Exception as e:
            pytest.fail(f"Failed to decode Base64 payload: {e}")


def test_extraction_directory_exists():
    """Test that extraction directory exists."""
    extracted_dir = Path("extracted")
    assert extracted_dir.exists(), "Extracted directory not found. Run extract_vsix.py first."
    
    extension_dir = extracted_dir / "extension"
    assert extension_dir.exists(), "Extension directory not found in extracted contents"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
