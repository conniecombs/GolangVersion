# Architecture Analysis & Roadmap

## Executive Summary

**Status:** The application is now **functionally stable** after resolving the critical stderr pipe deadlock and implementing timeout/rate-limiting fixes. However, **significant architectural debt** remains that will hinder long-term scalability and maintenance.

## Recent Fixes (v2.1.0)

### ✅ RESOLVED: Timeout Issues
- **Problem:** Aggressive 10-second `ResponseHeaderTimeout` caused large uploads to fail
- **Fix:** Increased timeouts to realistic values:
  - Client timeout: 180s (3 minutes)
  - Response header timeout: 60s
  - Context timeout: 180s per file
- **Impact:** Large files (10-50MB) and slow connections now work reliably

### ✅ RESOLVED: Rate Limiting (IP Ban Prevention)
- **Problem:** No throttling meant 8 concurrent workers could bombard services instantly
- **Fix:** Implemented per-service rate limiters using `golang.org/x/time/rate`
  - 2 requests/second with burst of 5 for image hosts
  - 1 request/second with burst of 3 for forums (ViperGirls)
- **Impact:** Significantly reduced risk of automated IP bans

### ✅ RESOLVED: Global State Bottleneck
- **Problem:** Single global `stateMutex` locked all services during session checks
- **Fix:** Refactored to per-service state structs with individual `sync.RWMutex`
  - `viprState`, `turboState`, `imageBamState`, `viperGirlsState`
- **Impact:** Reduced lock contention; parallel uploads to different services no longer block each other

---

## Remaining Architectural Issues

### 🔴 CRITICAL: The "Split-Brain" Architecture

**The Problem:**
Python has a dynamic plugin system (`modules/plugins/*.py`) that allows dropping in new service implementations. However, Go uses a **hardcoded switch statement** (uploader.go:431-445):

```go
switch job.Service {
case "imx.to":
    url, thumb, err = uploadImx(ctx, fp, job)
case "pixhost.to":
    url, thumb, err = uploadPixhost(ctx, fp, job)
// ...
default:
    err = fmt.Errorf("unknown service: %s", job.Service)
}
```

**The Consequence:**
- You **cannot** simply drop in a new Python plugin
- You **must** modify Go code and recompile the binary
- This **defeats the entire purpose** of having a plugin system

**Evidence:**
- Python: `modules/plugins/imx_plugin.py`, `pixhost_plugin.py`, etc.
- Go: Hardcoded service logic in `uploadImx()`, `uploadPixhost()`, etc.
- Configuration: Hardcoded mappings in `upload_manager.py:159-166`

---

### 🟡 MEDIUM: Fragile Configuration Mapping

**The Problem:**
`UploadManager` (Python) manually maps configuration keys to what Go expects:

```python
"imx_thumb_id": self._map_imx_size(cfg.get("thumbnail_size")),
# Maps: {"180": "2", "250": "3", ...}
```

**The Risk:**
- If a plugin changes its options, the hardcoded map breaks
- Mapping logic belongs in the **plugin**, not the manager
- Adding a new service requires updating **3 files** (plugin, manager, Go)

---

### 🟡 MEDIUM: Lack of Input Sanitization (Go Side)

**The Problem:**
- Python has `sanitize_filename()`, but Go trusts all file paths from JSON
- A malicious plugin could theoretically trick Go into reading arbitrary files

**Mitigation:**
- Low risk in a desktop app context (user controls plugins)
- Should still validate file paths are within expected directories

---

## Recommended Roadmap

### Phase 1: Immediate (Next Release)
*Already completed in v2.1.0:*
- ✅ Fix timeouts
- ✅ Implement rate limiting
- ✅ Refactor global state

### Phase 2: Architectural Refactor (High Priority)

**Option A: Make Go a "Dumb HTTP Runner" (Recommended)**

Convert Go to a generic HTTP executor that accepts fully-formed requests from Python:

```python
# Python Plugin Sends:
{
  "action": "http_upload",
  "url": "https://api.imx.to/v1/upload.php",
  "method": "POST",
  "headers": {"X-API-KEY": "..."},
  "multipart_fields": {
    "image": {"type": "file", "path": "/path/to/file.jpg"},
    "format": {"type": "text", "value": "json"}
  }
}
```

**Benefits:**
- Restores Python plugin power
- Go becomes service-agnostic
- New services = drop-in Python plugins
- No recompilation needed

**Implementation:**
1. Create `handleHttpUpload(job JobRequest)` in Go
2. Parse generic multipart/form-data from Python
3. Update all plugins to generate HTTP requests
4. Remove hardcoded service functions

**Estimated Effort:** 2-3 days of refactoring

---

**Option B: Port All Logic to Go**

Move plugin logic entirely to Go and treat Python purely as UI.

**Benefits:**
- Single language
- Better performance (no IPC overhead)

**Drawbacks:**
- Loses Python's rapid prototyping advantage
- Harder for non-Go developers to contribute
- Still requires recompilation for new services

**Estimated Effort:** 1-2 weeks

---

### Phase 3: Enhancements

After architectural refactor:

1. **Credential Encryption:** Store API keys/passwords encrypted at rest
2. **Retry Logic:** Automatic retry with exponential backoff for transient failures
3. **Progress Streaming:** Real-time upload progress (currently only status changes)
4. **Plugin Sandboxing:** Limit plugin file system access
5. **Configuration Validation:** JSON schema validation for plugin configs

---

## Security Assessment

### Current State

✅ **Good:**
- Credentials passed via stdin (not environment/CLI args)
- TLS verification enabled (no `InsecureSkipVerify`)
- Uses crypto/rand for randomness

⚠️ **Needs Improvement:**
- No input sanitization on Go side
- ViperGirls uses MD5 (legacy forum requirement, documented)
- Credentials stored in plaintext SQLite

### Recommendations

1. Add file path validation in Go (must be absolute, within user directory)
2. Consider encrypting stored credentials (using OS keychain on desktop)
3. Add rate limit for login attempts to prevent brute force

---

## Performance Characteristics

**Current Bottlenecks:**
1. ~~Global state mutex~~ ✅ FIXED
2. ~~Aggressive timeouts~~ ✅ FIXED
3. Worker pool size hardcoded to 8 (should be configurable)

**Scalability:**
- Handles ~100-200 files/batch reliably
- Beyond 500 files: UI may become unresponsive (consider background mode)

**Memory:**
- Streaming uploads (pipe-based) keep memory low
- Each worker holds ~5-10MB during upload

---

## Testing Strategy

**Current Coverage:**
- Integration tests exist (`test_integration.py`)
- No unit tests for Go code

**Recommended:**
1. Add Go unit tests for rate limiter logic
2. Add mock service tests (fake HTTP servers)
3. Stress test with 1000+ files
4. Test timeout/retry scenarios

---

## Conclusion

The application is **production-ready** for basic use cases after the v2.1.0 fixes. However, the split-brain architecture will become a **maintenance nightmare** as more services are added.

**Priority Recommendation:** Implement Option A (Dumb Runner) to restore plugin flexibility while keeping Go's concurrency benefits.

---

## Version History

- **v2.1.0** (2025-01-09): Fixed timeouts, added rate limiting, refactored state
- **v2.0.0** (Previous): Fixed stderr pipe deadlock
- **v1.x**: Initial Python/Go hybrid implementation
