# XploitX CTF Platform — Monitoring & Observability

## 1. Health Endpoints

XploitX exposes standard health endpoints for load balancers, container orchestrators, and uptime monitors:

### `GET /health` or `GET /healthcheck`
Returns HTTP 200 when all core components are operational:
```json
{
  "status": "healthy",
  "database": "up",
  "cache": "up"
}
```
If either the database or the cache is unreachable, returns HTTP 503 Service Unavailable:
```json
{
  "status": "unhealthy",
  "database": "down",
  "cache": "up"
}
```

---

## 2. Request Correlation & Tracing

Every incoming request is tagged with an `X-Request-ID` header:
- If provided upstream by Cloudflare/Nginx (`X-Request-ID`), XploitX adopts it.
- If missing, XploitX generates a random 32-character hexadecimal UUID.
- The request ID is returned in the HTTP response headers and prefixed to all application logs for easy distributed tracing:
  ```text
  [8f9a2b1c4e0d...] [2026-09-23 11:45:00 UTC] 10.0.0.1 - successful login for admin
  ```

---

## 3. Log Redaction & Security

XploitX automatically redacts sensitive attributes in logs:
- `password`
- `secret`
- `token`
- `nonce`
- `api_key`
- `flag`
- Authorization header tokens (`Bearer [REDACTED]`)

Logs are stored in structured JSON format by Nginx and rotating text files in `/var/log/CTFd/`.
