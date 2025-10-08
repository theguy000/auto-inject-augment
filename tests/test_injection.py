"""
Test suite for privacy protection injection.

Verifies that:
1. device-spoofer.js exists in privacy-protection directory
2. All HTML files contain the injection
3. Script tag is positioned correctly (FIRST, before telemetry)
4. Correct nonce attribute is present
"""

import pytest
from pathlib import Path
import re


# Expected HTML files to be modified
EXPECTED_HTML_FILES = [
    'main-panel.html',
    'index.html',
    'settings.html',
    'secrets-home.html',
    'memories.html',
    'history.html',
    'diff-view.html',
    'rules.html',
    'preference.html',
    'remote-agent-home.html',
    'remote-agent-diff.html',
    'next-edit-suggestions.html'
]

# Expected script tag pattern
EXPECTED_SCRIPT_PATTERN = r'<script\s+src="../privacy-protection/device-spoofer\.js".*?></script>'

# Expected nonce value
EXPECTED_NONCE = 'nonce-NdJS6eXuvR9e2+J/eS0faQ=='


class TestPrivacyInjection:
    """Test privacy protection injection."""
    
    @pytest.fixture
    def extension_dir(self):
        """Get extension directory path."""
        return Path("extracted/extension")
    
    @pytest.fixture
    def webviews_dir(self, extension_dir):
        """Get webviews directory path."""
        return extension_dir / "common-webviews"
    
    @pytest.fixture
    def privacy_dir(self, extension_dir):
        """Get privacy-protection directory path."""
        return extension_dir / "privacy-protection"
    
    def test_device_spoofer_exists(self, privacy_dir):
        """Test that device-spoofer.js exists."""
        spoofer_file = privacy_dir / "device-spoofer.js"
        
        assert spoofer_file.exists(), f"device-spoofer.js not found at {spoofer_file}"
        
        # Verify file is not empty
        content = spoofer_file.read_text(encoding='utf-8')
        assert len(content) > 0, "device-spoofer.js is empty"
        assert "Device Fingerprint Spoofing" in content, "device-spoofer.js missing expected header"
    
    def test_all_html_files_exist(self, webviews_dir):
        """Test that all expected HTML files exist."""
        for html_file in EXPECTED_HTML_FILES:
            file_path = webviews_dir / html_file
            assert file_path.exists(), f"HTML file not found: {html_file}"
    
    def test_all_html_files_modified(self, webviews_dir):
        """Test that all HTML files contain the privacy script injection."""
        for html_file in EXPECTED_HTML_FILES:
            file_path = webviews_dir / html_file
            content = file_path.read_text(encoding='utf-8')
            
            # Check for script tag
            assert 'device-spoofer.js' in content, \
                f"{html_file} does not contain device-spoofer.js reference"
            
            # Check for script tag pattern
            match = re.search(EXPECTED_SCRIPT_PATTERN, content)
            assert match is not None, \
                f"{html_file} does not contain properly formatted script tag"
    
    def test_script_tag_has_nonce(self, webviews_dir):
        """Test that script tags have correct nonce attribute."""
        for html_file in EXPECTED_HTML_FILES:
            file_path = webviews_dir / html_file
            content = file_path.read_text(encoding='utf-8')
            
            # Find script tag
            match = re.search(EXPECTED_SCRIPT_PATTERN, content)
            if match:
                script_tag = match.group(0)
                assert EXPECTED_NONCE in script_tag, \
                    f"{html_file} script tag missing correct nonce attribute"
    
    def test_script_loads_before_telemetry(self, webviews_dir):
        """Test that device-spoofer.js loads BEFORE any telemetry scripts."""
        for html_file in EXPECTED_HTML_FILES:
            file_path = webviews_dir / html_file
            content = file_path.read_text(encoding='utf-8')
            
            # Find position of device-spoofer.js
            spoofer_pos = content.find('device-spoofer.js')
            
            # Find position of telemetry-related scripts
            # These should come AFTER device-spoofer.js
            telemetry_indicators = [
                'Store-BaDlCE2f.js',  # Tracking data class
                'initialize-CXNwi7OG.js',  # Sentry initialization
            ]
            
            for indicator in telemetry_indicators:
                indicator_pos = content.find(indicator)
                if indicator_pos != -1:
                    assert spoofer_pos < indicator_pos, \
                        f"{html_file}: device-spoofer.js must load BEFORE {indicator}"
    
    def test_script_after_title_tag(self, webviews_dir):
        """Test that script is injected after </title> tag."""
        for html_file in EXPECTED_HTML_FILES:
            file_path = webviews_dir / html_file
            content = file_path.read_text(encoding='utf-8')
            
            # Find positions
            title_end = content.find('</title>')
            spoofer_pos = content.find('device-spoofer.js')
            
            assert title_end != -1, f"{html_file} missing </title> tag"
            assert spoofer_pos > title_end, \
                f"{html_file}: device-spoofer.js must come AFTER </title> tag"
    
    def test_privacy_comment_present(self, webviews_dir):
        """Test that privacy protection comment is present."""
        for html_file in EXPECTED_HTML_FILES:
            file_path = webviews_dir / html_file
            content = file_path.read_text(encoding='utf-8')
            
            # Check for comment
            assert 'PRIVACY PROTECTION' in content, \
                f"{html_file} missing privacy protection comment"


class TestDeviceSpooferContent:
    """Test device-spoofer.js content."""
    
    @pytest.fixture
    def spoofer_content(self):
        """Get device-spoofer.js content."""
        spoofer_file = Path("extracted/extension/privacy-protection/device-spoofer.js")
        return spoofer_file.read_text(encoding='utf-8')
    
    def test_contains_config(self, spoofer_content):
        """Test that spoofer contains configuration."""
        assert 'CONFIG' in spoofer_content
        assert 'DEVICE_MEMORY_OPTIONS' in spoofer_content
        assert 'HARDWARE_CONCURRENCY_OPTIONS' in spoofer_content
    
    def test_contains_spoofing_functions(self, spoofer_content):
        """Test that spoofer contains spoofing functions."""
        assert 'NavigatorSpoofer' in spoofer_content or 'applyAll' in spoofer_content
        assert 'Object.defineProperty' in spoofer_content
    
    def test_contains_machine_id_hook(self, spoofer_content):
        """Test that spoofer provides Machine ID hook."""
        assert '__getSpoofedMachineId' in spoofer_content or 'machineId' in spoofer_content


def test_extraction_directory_exists():
    """Test that extraction directory exists."""
    extracted_dir = Path("extracted")
    assert extracted_dir.exists(), "Extracted directory not found"
    
    extension_dir = extracted_dir / "extension"
    assert extension_dir.exists(), "Extension directory not found in extracted contents"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

