/**
 * Device Fingerprint Spoofing Module
 * 
 * This module intercepts and spoofs device-identifying information
 * to prevent cross-account tracking while maintaining realistic values.
 * 
 * Features:
 * - Generates realistic random device specs
 * - Persists spoofed values during session
 * - Randomizes on new session/browser restart
 * - Intercepts navigator properties
 * - Spoofs Machine ID
 * 
 * @author istiak
 * @date 2025-01-08
 */

(function() {
  'use strict';

  // ============================================================================
  // CONFIGURATION
  // ============================================================================

  const CONFIG = {
    // Storage key for persisting spoofed values during session
    STORAGE_KEY: 'augment_spoofed_fingerprint',
    
    // Whether to log spoofing activity (disable in production)
    DEBUG_MODE: false,
    
    // Realistic value ranges
    DEVICE_MEMORY_OPTIONS: [2, 4, 8, 16, 32],  // GB
    HARDWARE_CONCURRENCY_OPTIONS: [2, 4, 6, 8, 12, 16, 24, 32],  // CPU cores
    
    TIMEZONES: [
      'America/New_York', 'America/Los_Angeles', 'America/Chicago',
      'Europe/London', 'Europe/Paris', 'Europe/Berlin',
      'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Singapore',
      'Asia/Dubai', 'Asia/Kolkata', 'Australia/Sydney'
    ],
    
    SCREEN_RESOLUTIONS: [
      { width: 1920, height: 1080 },
      { width: 2560, height: 1440 },
      { width: 3840, height: 2160 },
      { width: 1680, height: 1050 },
      { width: 1440, height: 900 },
      { width: 1366, height: 768 }
    ],
    
    PLATFORMS: ['Win32', 'MacIntel', 'Linux x86_64'],
    
    CONNECTION_TYPES: ['wifi', 'ethernet', 'cellular', '4g'],
    EFFECTIVE_TYPES: ['4g', '3g', 'slow-2g']
  };

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  /**
   * Generate random integer between min and max (inclusive)
   */
  function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  /**
   * Pick random element from array
   */
  function randomChoice(array) {
    return array[randomInt(0, array.length - 1)];
  }

  /**
   * Generate UUID v4
   */
  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  /**
   * Generate realistic Machine ID based on platform
   */
  function generateMachineId(platform) {
    // Different formats for different platforms
    if (platform === 'Win32') {
      // Windows: UUID format
      return generateUUID();
    } else if (platform === 'MacIntel') {
      // macOS: UUID format (IOPlatformUUID)
      return generateUUID().toUpperCase();
    } else {
      // Linux: 32 character hex string
      return Array.from({length: 32}, () => 
        randomInt(0, 15).toString(16)
      ).join('');
    }
  }

  /**
   * Debug logger
   */
  function log(...args) {
    if (CONFIG.DEBUG_MODE) {
      console.log('[DeviceSpoofer]', ...args);
    }
  }

  // ============================================================================
  // SPOOFED FINGERPRINT GENERATION
  // ============================================================================

  class DeviceFingerprintGenerator {
    constructor() {
      this.fingerprint = null;
    }

    /**
     * Generate a complete spoofed device fingerprint
     */
    generate() {
      const platform = randomChoice(CONFIG.PLATFORMS);
      const resolution = randomChoice(CONFIG.SCREEN_RESOLUTIONS);
      const deviceMemory = randomChoice(CONFIG.DEVICE_MEMORY_OPTIONS);
      
      // CPU cores should correlate somewhat with RAM
      const maxCores = deviceMemory >= 16 ? 32 : deviceMemory >= 8 ? 16 : 8;
      const possibleCores = CONFIG.HARDWARE_CONCURRENCY_OPTIONS.filter(c => c <= maxCores);
      const hardwareConcurrency = randomChoice(possibleCores);

      this.fingerprint = {
        // Hardware
        deviceMemory: deviceMemory,
        hardwareConcurrency: hardwareConcurrency,
        
        // Machine ID
        machineId: generateMachineId(platform),
        
        // Platform
        platform: platform,
        
        // Screen
        screenWidth: resolution.width,
        screenHeight: resolution.height,
        screenAvailWidth: resolution.width,
        screenAvailHeight: resolution.height - randomInt(30, 80), // Account for taskbar
        screenColorDepth: 24,
        screenPixelDepth: 24,
        
        // Timezone
        timezone: randomChoice(CONFIG.TIMEZONES),
        timezoneOffset: randomInt(-720, 720),
        
        // Language
        language: randomChoice(['en-US', 'en-GB', 'de-DE', 'fr-FR', 'ja-JP', 'zh-CN']),
        languages: ['en-US', 'en'],
        
        // Connection (for navigator.connection)
        connectionType: randomChoice(CONFIG.CONNECTION_TYPES),
        effectiveType: randomChoice(CONFIG.EFFECTIVE_TYPES),
        downlink: randomInt(1, 10),
        rtt: randomInt(50, 200),
        
        // Canvas fingerprint randomization
        canvasNoise: Math.random(),
        
        // Generation timestamp
        generatedAt: Date.now(),
        sessionId: generateUUID()
      };

      log('Generated new fingerprint:', this.fingerprint);
      return this.fingerprint;
    }

    /**
     * Load fingerprint from storage or generate new one
     */
    loadOrGenerate() {
      try {
        const stored = sessionStorage.getItem(CONFIG.STORAGE_KEY);
        if (stored) {
          this.fingerprint = JSON.parse(stored);
          log('Loaded fingerprint from session storage');
          return this.fingerprint;
        }
      } catch (e) {
        log('Failed to load stored fingerprint:', e);
      }
      
      return this.generate();
    }

    /**
     * Save fingerprint to session storage
     */
    save() {
      try {
        sessionStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(this.fingerprint));
        log('Saved fingerprint to session storage');
      } catch (e) {
        log('Failed to save fingerprint:', e);
      }
    }

    /**
     * Get current fingerprint
     */
    get() {
      if (!this.fingerprint) {
        this.loadOrGenerate();
        this.save();
      }
      return this.fingerprint;
    }
  }

  // ============================================================================
  // NAVIGATOR PROPERTY SPOOFING
  // ============================================================================

  class NavigatorSpoofer {
    constructor(fingerprint) {
      this.fingerprint = fingerprint;
      this.originalNavigator = {};
    }

    /**
     * Override a navigator property
     */
    overrideProperty(property, value) {
      try {
        // Save original value
        this.originalNavigator[property] = navigator[property];
        
        // Override with spoofed value
        Object.defineProperty(navigator, property, {
          get: () => value,
          configurable: true,
          enumerable: true
        });
        
        log(`Spoofed navigator.${property}:`, value);
      } catch (e) {
        log(`Failed to spoof navigator.${property}:`, e);
      }
    }

    /**
     * Apply all navigator spoofing
     */
    applyAll() {
      const fp = this.fingerprint;

      // Hardware
      this.overrideProperty('deviceMemory', fp.deviceMemory);
      this.overrideProperty('hardwareConcurrency', fp.hardwareConcurrency);
      
      // Platform
      this.overrideProperty('platform', fp.platform);
      
      // Language
      this.overrideProperty('language', fp.language);
      this.overrideProperty('languages', fp.languages);

      // Connection API
      if (navigator.connection) {
        const originalConnection = navigator.connection;
        Object.defineProperty(navigator, 'connection', {
          get: () => ({
            ...originalConnection,
            effectiveType: fp.effectiveType,
            type: fp.connectionType,
            downlink: fp.downlink,
            rtt: fp.rtt,
            saveData: false
          }),
          configurable: true
        });
        log('Spoofed navigator.connection');
      }
    }

    /**
     * Restore original navigator properties
     */
    restore() {
      Object.keys(this.originalNavigator).forEach(property => {
        try {
          Object.defineProperty(navigator, property, {
            value: this.originalNavigator[property],
            configurable: true,
            enumerable: true
          });
        } catch (e) {
          log(`Failed to restore navigator.${property}:`, e);
        }
      });
      log('Restored original navigator properties');
    }
  }

  // ============================================================================
  // SCREEN PROPERTY SPOOFING
  // ============================================================================

  class ScreenSpoofer {
    constructor(fingerprint) {
      this.fingerprint = fingerprint;
      this.originalScreen = {};
    }

    /**
     * Override screen property
     */
    overrideProperty(property, value) {
      try {
        this.originalScreen[property] = screen[property];
        
        Object.defineProperty(screen, property, {
          get: () => value,
          configurable: true,
          enumerable: true
        });
        
        log(`Spoofed screen.${property}:`, value);
      } catch (e) {
        log(`Failed to spoof screen.${property}:`, e);
      }
    }

    /**
     * Apply all screen spoofing
     */
    applyAll() {
      const fp = this.fingerprint;
      
      this.overrideProperty('width', fp.screenWidth);
      this.overrideProperty('height', fp.screenHeight);
      this.overrideProperty('availWidth', fp.screenAvailWidth);
      this.overrideProperty('availHeight', fp.screenAvailHeight);
      this.overrideProperty('colorDepth', fp.screenColorDepth);
      this.overrideProperty('pixelDepth', fp.screenPixelDepth);
    }

    /**
     * Restore original screen properties
     */
    restore() {
      Object.keys(this.originalScreen).forEach(property => {
        try {
          Object.defineProperty(screen, property, {
            value: this.originalScreen[property],
            configurable: true,
            enumerable: true
          });
        } catch (e) {
          log(`Failed to restore screen.${property}:`, e);
        }
      });
      log('Restored original screen properties');
    }
  }

  // ============================================================================
  // TIMEZONE SPOOFING
  // ============================================================================

  class TimezoneSpoofer {
    constructor(fingerprint) {
      this.fingerprint = fingerprint;
      this.originalDate = Date;
    }

    /**
     * Apply timezone spoofing
     */
    applyAll() {
      const fp = this.fingerprint;
      const spoofedOffset = fp.timezoneOffset;
      
      // Override Date.prototype methods
      const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
      Date.prototype.getTimezoneOffset = function() {
        return spoofedOffset;
      };

      log('Spoofed timezone offset:', spoofedOffset);
    }
  }

  // ============================================================================
  // MACHINE ID SPOOFING (for backend)
  // ============================================================================

  /**
   * Intercept Machine ID requests
   * This creates a global hook that can be called by extension code
   */
  window.__getSpoofedMachineId = function() {
    const generator = new DeviceFingerprintGenerator();
    const fp = generator.get();
    return fp.machineId;
  };

  // ============================================================================
  // MAIN INITIALIZATION
  // ============================================================================

  class DeviceSpooferMain {
    constructor() {
      this.generator = new DeviceFingerprintGenerator();
      this.navigatorSpoofer = null;
      this.screenSpoofer = null;
      this.timezoneSpoofer = null;
      this.isActive = false;
    }

    /**
     * Initialize and activate all spoofing
     */
    init() {
      if (this.isActive) {
        log('Spoofer already active');
        return;
      }

      log('Initializing Device Fingerprint Spoofer...');
      
      // Generate or load fingerprint
      const fingerprint = this.generator.loadOrGenerate();
      this.generator.save();

      // Apply navigator spoofing
      this.navigatorSpoofer = new NavigatorSpoofer(fingerprint);
      this.navigatorSpoofer.applyAll();

      // Apply screen spoofing
      this.screenSpoofer = new ScreenSpoofer(fingerprint);
      this.screenSpoofer.applyAll();

      // Apply timezone spoofing
      this.timezoneSpoofer = new TimezoneSpoofer(fingerprint);
      this.timezoneSpoofer.applyAll();

      this.isActive = true;
      
      log('✓ Device Fingerprint Spoofer activated');
      log('✓ Machine ID:', fingerprint.machineId);
      log('✓ Device Memory:', fingerprint.deviceMemory, 'GB');
      log('✓ CPU Cores:', fingerprint.hardwareConcurrency);
      log('✓ Platform:', fingerprint.platform);
      log('✓ Screen:', `${fingerprint.screenWidth}x${fingerprint.screenHeight}`);
      log('✓ Timezone:', fingerprint.timezone);
    }

    /**
     * Deactivate spoofing
     */
    deactivate() {
      if (!this.isActive) {
        return;
      }

      if (this.navigatorSpoofer) {
        this.navigatorSpoofer.restore();
      }
      
      if (this.screenSpoofer) {
        this.screenSpoofer.restore();
      }

      this.isActive = false;
      log('Device Fingerprint Spoofer deactivated');
    }

    /**
     * Get current spoofed fingerprint
     */
    getFingerprint() {
      return this.generator.get();
    }

    /**
     * Generate new fingerprint and reapply
     */
    regenerate() {
      this.deactivate();
      this.generator.generate();
      this.generator.save();
      this.init();
      log('Regenerated fingerprint');
    }
  }

  // ============================================================================
  // EXPORT & AUTO-INIT
  // ============================================================================

  // Create global instance
  window.__deviceSpoofer = new DeviceSpooferMain();

  // Auto-initialize on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      window.__deviceSpoofer.init();
    });
  } else {
    window.__deviceSpoofer.init();
  }

  log('Device Fingerprint Spoofer loaded');

})();

