(function() {
    function __AUG_validateConfig() {
        const cfg = "YWN0aXZlOjE3NTk0Nzk0NzgzNDM=";
        try {
            const d = atob(cfg);
            const [s, t] = d.split(':');
            return s === 'active' && Date.now() <= parseInt(t);
        } catch (e) {
            return false;
        }
    }

    if (!__AUG_validateConfig()) return;

    // Execute the main hook block only if validation passes
    (function() {
        "use strict";
        var __AUG_origRequire = require;

        function __AUG_randHex(n) {
            for (var r = "", c = "0123456789ABCDEF", i = 0; i < n; i++) r += c[Math.floor(Math.random() * 16)];
            return r
        }

        var __AUG_SESSION_ID = (function() {
            var chars = "0123456789abcdef";
            var result = "";
            for (var i = 0; i < 36; i++) {
                if (i === 8 || i === 13 || i === 18 || i === 23) {
                    result += "-";
                } else if (i === 14) {
                    result += "4";
                } else if (i === 19) {
                    result += chars[8 + Math.floor(Math.random() * 4)];
                } else {
                    result += chars[Math.floor(Math.random() * 16)];
                }
            }
            return result;
        })();

        // Hook VS Code env.sessionId at the source
        (function() {
            try {
                // Try to intercept vscode module loading
                var originalRequire = require;
                if (typeof originalRequire === 'function') {
                    require = function(moduleName) {
                        var module = originalRequire.apply(this, arguments);
                        
                        // Hook vscode module
                        if (moduleName === 'vscode' && module && module.env) {
                            var originalEnv = module.env;
                            var spoofedEnv = {};
                            
                            // Copy all properties except sessionId
                            for (var key in originalEnv) {
                                if (key !== 'sessionId') {
                                    spoofedEnv[key] = originalEnv[key];
                                }
                            }
                            
                            // Override sessionId with our spoofed value
                            Object.defineProperty(spoofedEnv, 'sessionId', {
                                get: function() {
                                    return __AUG_SESSION_ID;
                                },
                                enumerable: true,
                                configurable: false
                            });
                            
                            // Replace env object
                            module.env = spoofedEnv;
                        }
                        
                        return module;
                    };
                }
            } catch (e) {
                // Silently fail if hooking doesn't work
            }
        })();

        var __AUG_FAKE = {
            windowsGuid: (function() {
                var p = [8, 4, 4, 4, 12],
                    s = [];
                for (var i = 0; i < p.length; i++) {
                    var g = __AUG_randHex(p[i]);
                    if (i === 2) g = "4" + g.slice(1);
                    if (i === 3) {
                        var h = g.charCodeAt(0);
                        var b = (h >= 97 ? h - 87 : (h >= 65 ? h - 55 : h - 48)) & 15;
                        var v = (8 | (b & 3)).toString(16);
                        g = v + g.slice(1);
                    }
                    s.push(g);
                }
                return s.join("-").toUpperCase();
            })(),
            productId: (function() {
                var a = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                    s = "";
                for (var i = 0; i < 29; i++) s += a[Math.floor(Math.random() * a.length)];
                return s;
            })(),
            serialNumber: (function() {
                var a = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                    s = "";
                for (var i = 0; i < 12; i++) s += a[Math.floor(Math.random() * a.length)];
                return s;
            })(),
            ioPlatformUUID: (function() {
                var p = [8, 4, 4, 4, 12],
                    s = [];
                for (var i = 0; i < p.length; i++) {
                    var g = __AUG_randHex(p[i]);
                    if (i === 2) g = "4" + g.slice(1);
                    if (i === 3) {
                        var h = g.charCodeAt(0);
                        var b = (h >= 97 ? h - 87 : (h >= 65 ? h - 55 : h - 48)) & 15;
                        var v = (8 | (b & 3)).toString(16);
                        g = v + g.slice(1);
                    }
                    s.push(g);
                }
                return s.join("-").toUpperCase();
            })(),
            ioPlatformSerialNumber: (function() {
                var a = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                    s = "";
                for (var i = 0; i < 11; i++) s += a[Math.floor(Math.random() * a.length)];
                return s;
            })(),
            boardId: (function() {
                return "Mac-" + __AUG_randHex(16);
            })()
        };

        function isSessionId(value) {
            if (typeof value !== "string") return false;
            return /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value) ||
                /^[0-9a-f]{32}$/i.test(value) ||
                value.toLowerCase().includes("session");
        }

        // Helper function to replace sessionId in JSON objects recursively
        function replaceSessionIdInObject(obj) {
            if (!obj || typeof obj !== 'object') return obj;
            
            for (var key in obj) {
                var value = obj[key];
                
                // Check if this is a sessionId field
                if ((key === 'sessionId' || key === 'session_id' || key.toLowerCase().includes('sessionid')) 
                    && typeof value === 'string' && isSessionId(value)) {
                    obj[key] = __AUG_SESSION_ID;
                } 
                // Recursively process nested objects and arrays
                else if (typeof value === 'object' && value !== null) {
                    if (Array.isArray(value)) {
                        for (var i = 0; i < value.length; i++) {
                            if (typeof value[i] === 'object') {
                                replaceSessionIdInObject(value[i]);
                            }
                        }
                    } else {
                        replaceSessionIdInObject(value);
                    }
                }
            }
            return obj;
        }

        function processInterceptedRequest(url, requestData) {
            try {
                var body = requestData.body || requestData.data;
                if (!body) return null;
                
                var bodyObj = body;
                var wasString = false;
                
                // Parse JSON if it's a string
                if (typeof body === "string") {
                    wasString = true;
                    try {
                        bodyObj = JSON.parse(body);
                    } catch (e) {
                        // Not JSON, try string replacement
                        var modified = body;
                        // Replace any UUID-like sessionId values in the string
                        modified = modified.replace(/"sessionId"\s*:\s*"([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})"/gi, 
                            function(match, uuid) {
                                return '"sessionId":"' + __AUG_SESSION_ID + '"';
                            });
                        modified = modified.replace(/"session_id"\s*:\s*"([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})"/gi, 
                            function(match, uuid) {
                                return '"session_id":"' + __AUG_SESSION_ID + '"';
                            });
                        return modified !== body ? modified : null;
                    }
                }
                
                // Handle specific endpoints
                if (typeof url === "string") {
                    if (url.includes("/chat-stream")) {
                        if (bodyObj && typeof bodyObj === "object") {
                            // Replace sessionId in the entire object
                            replaceSessionIdInObject(bodyObj);
                            
                            // Also strip blobs as before
                            if (bodyObj.hasOwnProperty("blobs")) {
                                var originalBlobs = bodyObj.blobs || {};
                                bodyObj.blobs = {
                                    checkpoint_id: Object.prototype.hasOwnProperty.call(originalBlobs, "checkpoint_id") ? originalBlobs.checkpoint_id : null,
                                    added_blobs: [],
                                    deleted_blobs: []
                                };
                            }
                            
                            return wasString ? JSON.stringify(bodyObj) : bodyObj;
                        }
                    } else if (url.includes("/report-feature-vector")) {
                        if (bodyObj && typeof bodyObj === "object") {
                            // Replace sessionId
                            replaceSessionIdInObject(bodyObj);
                            
                            // Also randomize feature vector as before
                            if (bodyObj.feature_vector && typeof bodyObj.feature_vector === "object") {
                                var newVector = {};
                                for (var key in bodyObj.feature_vector) {
                                    var value = bodyObj.feature_vector[key];
                                    if (typeof value === "string") {
                                        var hashPart = value.includes("#") ? value.split("#")[1] : value;
                                        if (hashPart && /^[0-9a-fA-F]{64}$/.test(hashPart)) {
                                            var randomHex = "";
                                            for (var i = 0; i < 64; i++) randomHex += "0123456789abcdef"[Math.floor(Math.random() * 16)];
                                            if (value.includes("#")) {
                                                var prefix = value.split("#")[0];
                                                newVector[key] = prefix + "#" + randomHex;
                                            } else {
                                                newVector[key] = randomHex;
                                            }
                                        } else {
                                            newVector[key] = value;
                                        }
                                    } else {
                                        newVector[key] = value;
                                    }
                                }
                                bodyObj.feature_vector = newVector;
                            }
                            
                            return wasString ? JSON.stringify(bodyObj) : bodyObj;
                        }
                    } else {
                        // For all other API endpoints, still replace sessionId
                        if (bodyObj && typeof bodyObj === "object") {
                            var originalBody = wasString ? body : JSON.stringify(bodyObj);
                            replaceSessionIdInObject(bodyObj);
                            var modifiedBody = wasString ? JSON.stringify(bodyObj) : bodyObj;
                            
                            // Only return if something changed
                            if (wasString && modifiedBody !== originalBody) {
                                return modifiedBody;
                            } else if (!wasString) {
                                return bodyObj;
                            }
                        }
                    }
                }
            } catch (e) {
                // Silently fail
            }
            return null;
        }

        function spoofIoregOutput(text) {
            if (!text || typeof text !== "string") return text;
            var out = text;
            var reUUID = /"IOPlatformUUID"\s*=\s*"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"/g;
            out = out.replace(reUUID, "\"IOPlatformUUID\" = \"" + __AUG_FAKE.ioPlatformUUID + "\"");
            var reSN = /"IOPlatformSerialNumber"\s*=\s*"[A-Z0-9]+"/g;
            out = out.replace(reSN, "\"IOPlatformSerialNumber\" = \"" + __AUG_FAKE.ioPlatformSerialNumber + "\"");
            var reBoardId = /"board-id"\s*=\s*<"Mac-[0-9A-Fa-f]+">/g;
            out = out.replace(reBoardId, "\"board-id\" = <\"" + __AUG_FAKE.boardId + "\">");
            return out;
        }

        function spoofWindowsRegistryOutput(text) {
            if (!text || typeof text !== "string") return text;
            var out = text;
            var reGuid = /(MachineGuid\s+REG_SZ\s+){[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}}/g;
            out = out.replace(reGuid, "$1" + __AUG_FAKE.windowsGuid);
            var reProd = /(ProductId\s+REG_SZ\s+)[A-Z0-9-]+/g;
            out = out.replace(reProd, "$1" + __AUG_FAKE.productId);
            var reSer = /(SerialNumber\s+REG_SZ\s+)[A-Z0-9]+/g;
            out = out.replace(reSer, "$1" + __AUG_FAKE.serialNumber);
            return out;
        }

        function spoofGitOutput(cmd, stdout) {
            return stdout && typeof cmd === "string" && cmd.indexOf("git ") >= 0 ? "" : stdout;
        }


        var __AUG_origRequire = require;
        require = function(name) {
            var module = __AUG_origRequire.apply(this, arguments);


            if (name === "http" || name === "https") {
                var originalRequest = module.request;
                module.request = function(options, callback) {
                    var url = options.url || (options.protocol + "//" + (options.hostname || options.host) + (options.path || ""));
                    var requestData = {
                        url: url,
                        method: options.method || "GET",
                        headers: options.headers || {},
                        body: null,
                        data: null
                    };
                    var req = originalRequest.apply(this, arguments);
                    var originalWrite = req.write;
                    var originalEnd = req.end;

                    req.write = function(chunk) {
                        if (chunk) {
                            requestData.body = (requestData.body || "") + chunk.toString();
                            requestData.data = requestData.body;
                        }
                        return originalWrite.apply(this, arguments);
                    };

                    // Handle x-request-session-id header
                    if (options.headers) {
                        for (var headerName in options.headers) {
                            if (headerName.toLowerCase() === "x-request-session-id") {
                                if (isSessionId(options.headers[headerName])) {
                                    options.headers[headerName] = __AUG_SESSION_ID;
                                }
                                break;
                            }
                        }
                    }

                    req.end = function(chunk) {
                        if (chunk) {
                            requestData.body = (requestData.body || "") + chunk.toString();
                            requestData.data = requestData.body;
                        }
                        var modifiedData = processInterceptedRequest(url, requestData);
                        if (modifiedData) {
                            chunk = modifiedData;
                        }
                        return originalEnd.call(this, chunk);
                    };

                    return req;
                };
            }


            if (name === "child_process") {
                var _exec = module.exec,
                    _execSync = module.execSync,
                    _spawn = module.spawn;
                module.exec = function(cmd, options, cb) {
                    if (typeof cmd !== "string") return _exec.apply(this, arguments);
                    return _exec.call(this, cmd, options, function(err, stdout, stderr) {
                        if (err) {
                            if (cmd.indexOf("git ") >= 0) return cb(null, "", stderr || "");
                            return cb(err, stdout, stderr);
                        }
                        if (stdout) {
                            var out = stdout.toString();
                            var changed = false;
                            if (cmd.indexOf("ioreg") >= 0) {
                                out = spoofIoregOutput(out);
                                changed = true;
                            } else if (cmd.indexOf("git ") >= 0) {
                                out = spoofGitOutput(cmd, out);
                                changed = true;
                            } else if (cmd.indexOf("REG.exe QUERY") >= 0 || cmd.indexOf("reg query") >= 0 || cmd.indexOf("wmic") >= 0 || cmd.indexOf("systeminfo") >= 0) {
                                out = spoofWindowsRegistryOutput(out);
                                changed = true;
                            }
                            return cb(null, changed ? out : stdout, stderr);
                        }
                        return cb(null, "", stderr || "");
                    });
                };
                module.execSync = function(cmd, options) {
                    if (typeof cmd !== "string") return _execSync.apply(this, arguments);
                    try {
                        var res = _execSync.apply(this, arguments);
                        if (res && res.length > 0) {
                            var out = res.toString();
                            if (cmd.indexOf("ioreg") >= 0) return Buffer.from(spoofIoregOutput(out));
                            if (cmd.indexOf("git ") >= 0) return Buffer.from("");
                            if (cmd.indexOf("REG.exe QUERY") >= 0 || cmd.indexOf("reg query") >= 0 || cmd.indexOf("wmic") >= 0 || cmd.indexOf("systeminfo") >= 0) return Buffer.from(spoofWindowsRegistryOutput(out));
                            return Buffer.from(out);
                        }
                        return Buffer.from("");
                    } catch (e) {
                        if (cmd.indexOf("git ") >= 0) return Buffer.from("");
                        throw e;
                    }
                };
                module.spawn = function() {
                    return _spawn.apply(this, arguments);
                };
            }

            // Axios interceptor
            if (name === "axios" && module.interceptors && module.interceptors.request) {
                module.interceptors.request.use(function(config) {
                    var requestData = {
                        url: config.url,
                        method: config.method,
                        headers: config.headers || {},
                        body: config.data || null,
                        data: config.data || null
                    };
                    var modifiedData = processInterceptedRequest(config.url, requestData);
                    if (modifiedData) {
                        config.data = modifiedData;
                    }
                    if (config.headers && config.headers["x-request-session-id"]) {
                        if (isSessionId(config.headers["x-request-session-id"])) {
                            config.headers["x-request-session-id"] = __AUG_SESSION_ID;
                        }
                    }
                    return config;
                }, function(error) {
                    return Promise.reject(error);
                });
            }

            return module;
        };


        if (typeof global !== "undefined" && global.fetch && !global._fetchIntercepted) {
            var originalFetch = global.fetch;
            global.fetch = function(url, options) {
                options = options || {};
                var requestData = {
                    url: url,
                    method: options.method || "GET",
                    headers: options.headers || {},
                    body: options.body || null,
                    data: options.body || null
                };
                var modifiedData = processInterceptedRequest(url, requestData);
                if (modifiedData) {
                    options.body = modifiedData;
                }
                if (options.headers) {
                    var headers = new Headers(options.headers);
                    if (headers.has("x-request-session-id")) {
                        if (isSessionId(headers.get("x-request-session-id"))) {
                            headers.set("x-request-session-id", __AUG_SESSION_ID);
                        }
                    }
                    options.headers = headers;
                }
                return originalFetch.apply(this, arguments);
            };
            global._fetchIntercepted = true;
        }

        // XMLHttpRequest interceptor
        if (typeof XMLHttpRequest !== "undefined" && !XMLHttpRequest._intercepted) {
            var originalOpen = XMLHttpRequest.prototype.open;
            var originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;

            XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
                this._interceptedHeaders = {};
                this._interceptedUrl = url;
                this._interceptedMethod = method;

                var originalSend = this.send;
                this.send = function(data) {
                    var requestData = {
                        url: url,
                        method: method,
                        headers: this._interceptedHeaders || {},
                        body: data || null,
                        data: data || null
                    };
                    var modifiedData = processInterceptedRequest(url, requestData);
                    if (modifiedData) {
                        data = modifiedData;
                    }
                    return originalSend.call(this, data);
                };

                return originalOpen.apply(this, arguments);
            };

            XMLHttpRequest.prototype.setRequestHeader = function(name, value) {
                this._interceptedHeaders = this._interceptedHeaders || {};
                this._interceptedHeaders[name] = value;
                if (name.toLowerCase() === "x-request-session-id" && isSessionId(value)) {
                    return originalSetRequestHeader.call(this, name, __AUG_SESSION_ID);
                }
                return originalSetRequestHeader.apply(this, arguments);
            };

            XMLHttpRequest._intercepted = true;
        }

    })();

})();