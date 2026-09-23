# XploitX CTF Platform — OWASP ASVS 5.0 Security Verification Checklist

This document maps the security architecture and controls implemented in XploitX against the **OWASP Application Security Verification Standard (ASVS 5.0)**.

| ASVS Category | Requirement & Verification Control | Implementation in XploitX | Status |
| :--- | :--- | :--- | :---: |
| **V1: Architecture** | Security architecture baseline, component isolation, secure defaults | Microservice boundary separating Web API from isolated Docker instance runner (`docker/instance_manager/server.py`). Non-destructive migration rules. | **PASS** |
| **V2: Authentication** | Strong password hashing, brute-force mitigation, account lockout | Bcrypt hashing with cost >= 12 (`CTFd/utils/crypto`). Nginx & Redis rate limits on `/login`, `/register`, `/reset_password`. | **PASS** |
| **V3: Session Management** | Secure cookie flags (`Secure`, `HttpOnly`, `SameSite`), session invalidation | `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`. Complete session revocation on password changes. | **PASS** |
| **V4: Access Control** | Deny-by-default RBAC, IDOR/BOLA protection, server-side role enforcement | Explicit role checks (`is_admin()`, team captain checks). All instance APIs verify object ownership before performing actions. | **PASS** |
| **V5: Validation & Sanitization** | Input validation, parameter allowlists, SQL/NoSQL injection prevention | Parameter sanitization, SQLAlchemy parameterized queries, strict regex validation for container image names. | **PASS** |
| **V6: Cryptography** | Secure random generation, constant-time comparisons, secret management | Secrets managed exclusively via `.env`. Cryptographic randomness via `os.urandom` and `secrets.token_hex`. Secret scanner in CI. | **PASS** |
| **V7: Error Handling & Logging** | No sensitive data in logs, request correlation, no stack traces in prod | Centralized `log()` redacts sensitive parameters. `X-Request-ID` attached to all logs and responses. Debug endpoints disabled in production. | **PASS** |
| **V8: Data Protection** | Sensitive data at rest and in transit, HTTPS enforcement | HTTPS-enforced cookies, HSTS (`max-age=31536000; includeSubDomains`), persistent volumes for production DB. | **PASS** |
| **V9: Communication** | TLS everywhere, secure cipher suites, HSTS | Nginx configured with modern TLS and automated HTTP to HTTPS redirection. | **PASS** |
| **V10: Malicious Code** | Container escape prevention, malicious archive defense | Zip Slip and Zip Bomb mitigations in `exports`. Challenge containers execute with `CAP_DROP = ALL`, `no-new-privileges`, and cgroup limits. | **PASS** |
| **V11: Business Logic** | Atomic flag scoring, anti-race conditions, quota limits | Database unique constraints on `solves(challenge_id, team_id)`. 1-instance-per-team quota enforcement. | **PASS** |
| **V12: File Uploads** | Path traversal prevention, random storage filenames, size limits | `FilesystemUploader` and `S3Uploader` sanitize paths and generate random hex subdirectories. Nginx client body size capped at 50MB. | **PASS** |
| **V13: API & Web Service** | RESTful security, Content-Type enforcement, CORS controls | Standard JSON response schemas. CORS origins restricted to trusted domains. Restrictive Content Security Policy. | **PASS** |
| **V14: Configuration** | Secure headers, dependency scanning, zero default secrets | CSP, HSTS, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, and CI vulnerability scanning. | **PASS** |
