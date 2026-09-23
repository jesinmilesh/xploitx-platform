# XploitX CTF Platform — Production Architecture Map

## 1. System Topology Overview

```
                                  INTERNET
                                     │
                                     ▼
                           ┌──────────────────┐
                           │ CDN / WAF / TLS  │
                           └────────┬─────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Nginx Reverse Proxy │
                         │  - Rate Limiting     │
                         │  - SSL Termination   │
                         │  - Security Headers  │
                         │  - Request Tracking  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   XploitX Web/API    │
                         │   - Flask 2.1 / WSGI │
                         │   - Session Auth     │
                         │   - CSRF & RBAC      │
                         │   - Solve Validation │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  ▼                 ▼                 ▼
         ┌────────────────┐ ┌───────────────┐ ┌───────────────┐
         │ Persistent DB  │ │  Redis 7      │ │Instance Client│
         │ - MariaDB 10.11│ │  - Sessions   │ │- Internal API │
         │   or Postgres  │ │  - SSE Stream │ │- HMAC Auth    │
         │ - Alembic Migr.│ │  - Rate Limits│ └───────┬───────┘
         └────────────────┘ └───────────────┘         │
                                                      ▼
                                           ┌────────────────────┐
                                           │  Instance Manager  │
                                           │  - Port Allocation │
                                           │  - Lifecycle Reaper│
                                           └──────────┬─────────┘
                                                      │
                                                      ▼
                                           ┌────────────────────┐
                                           │   Docker Runtime   │
                                           │   - cgroups limits │
                                           │   - cap_drop: ALL  │
                                           │   - no-new-privs   │
                                           │ ┌──────┐ ┌──────┐  │
                                           │ │CTF 1 │ │CTF 2 │  │
                                           │ └──────┘ └──────┘  │
                                           └────────────────────┘
```

---

## 2. Component Boundaries & Responsibilities

### A. Edge / Reverse Proxy Layer (`nginx`)
- **Port**: 80 / 443
- **Network**: `default` (public access)
- **Role**: Terminates TLS, enforces rate limiting on sensitive routes (`/login`, `/register`), injects standard security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`), and generates unique `X-Request-ID` correlation identifiers.

### B. Core Web Application (`ctfd`)
- **Runtime**: Python 3.11 / Flask / Gunicorn
- **Network**: `default` + `internal`
- **Role**: Handles user registrations, team management, challenge display, flag validation, dynamic scoring, and real-time SSE broadcasts. Communicates with `db` and `cache` exclusively across the private `internal` Docker network.

### C. Persistent Storage (`db`)
- **Engine**: MariaDB 10.11 or PostgreSQL
- **Network**: `internal` (strictly unexposed to public internet)
- **Volume**: Named persistent volume or managed cloud DB (`.data/mysql` or AWS RDS).
- **Rule**: Survives deployments, restarts, and crashes. Migrations are non-destructive.

### D. Distributed Cache & Real-Time Engine (`cache`)
- **Engine**: Redis 7 Alpine
- **Network**: `internal`
- **Role**: Stores active sessions, coordinates SSE event pub/sub for scoreboard updates, and maintains distributed rate-limiting counters.

### E. Isolated Challenge Instance Manager (`instance-manager`)
- **Runtime**: Dedicated microservice
- **Network**: `internal` + `challenge-network`
- **Role**: Provisions, tracks, and reaps dynamic containers for participants.
- **Security Boundary**: The Docker daemon socket (`/var/run/docker.sock`) is accessed ONLY by this isolated service and is never exposed to the web application or participant containers.

---

## 3. Data Flow: Flag Submission & Real-time Scoring

```
User Browser
    │
    │ 1. POST /api/v1/challenges/attempt (Flag + Nonce)
    ▼
Nginx Reverse Proxy (Rate limiting check)
    │
    ▼
XploitX Core API (Session verify + CSRF nonce check)
    │
    ├─► Flag Validation (Constant-time comparison)
    │
    ├─► Database Transaction (Atomic):
    │     - Insert Solves row (Unique constraint on [challenge_id, team_id])
    │     - Update dynamic challenge decay value
    │     - Record Audit Tracking entry
    │
    ├─► Redis Pub/Sub:
    │     - Broadcast scoreboard delta event
    │
    └─► SSE Feed:
          - Real-time notification delivered to all connected browsers
```
