# XploitX CTF Platform

[![Production Security CI](https://github.com/jesinmilesh/xploitx-platform/actions/workflows/security-ci.yml/badge.svg)](https://github.com/jesinmilesh/xploitx-platform/actions/workflows/security-ci.yml)
[![OWASP ASVS 5.0](https://img.shields.io/badge/Security-OWASP%20ASVS%205.0-blue.svg)](docs/SECURITY-CHECKLIST.md)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](docs/LICENSE)

**XploitX** is a production-grade, highly resilient, real-time Capture The Flag (CTF) platform built for high-stakes cybersecurity competitions, training academies, and enterprise defense exercises.

---

## Key Capabilities

- **Production Security Architecture**: Conforms to the OWASP ASVS 5.0 baseline with Strict CSP, HSTS, secure cookie attributes, CSRF nonces, and deny-by-default role-based access control.
- **Isolated Challenge Instance Manager**: Provisions on-demand, isolated Docker containers per participant/team with strict cgroup limits (CPU/RAM/PIDs), dropped Linux capabilities, and automated lifecycle reaping.
- **Zero-Data-Loss Database Persistence**: Engineered to survive Git updates, container rebuilds, and cold restarts with connection pooling, automated migrations, and schema validation.
- **Real-Time Scoreboard & Notifications**: Event-driven architecture powered by Server-Sent Events (SSE) and Redis for zero-polling scoreboard and competition updates.
- **Anti-Abuse & Rate Limiting**: Layered rate limiting across Nginx, Redis, and application endpoints protecting flag submissions, registrations, and logins.
- **Observability & Request Correlation**: Integrated `X-Request-ID` tracing, automated sensitive credential redaction, and standard `/health` endpoints.

---

## Architecture

```text
INTERNET ──► Nginx Reverse Proxy (SSL / Rate Limits / Security Headers)
                   │
                   ▼
             XploitX Core API (Flask / Gunicorn / RBAC)
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
    MariaDB 10.11 Redis 7  Instance Manager (Isolated Microservice)
   (Persistent)  (SSE/Cache) │
                             ▼
                     Docker Host Runtime (Isolated Containers)
```

---

## Repository Structure

```text
├── README.md               # Main project documentation & quickstart
├── vercel.json             # Vercel serverless deployment configuration
├── .gitignore              # Git ignore rules for builds, secrets, and caches
├── .vercelignore           # Vercel ignore rules for builds & serverless artifacts
├── api/                    # Vercel serverless functions and API dependencies
│   ├── index.py            # WSGI entrypoint for Vercel
│   └── requirements.txt    # Python requirements
├── conf/                   # Configuration files (Nginx, environment, linters, tools)
│   ├── .env.example        # Environment variable template
│   ├── nginx/              # Nginx reverse proxy configuration
│   └── ...                 # Build, lint, and packaging configurations
├── CTFd/                   # Core application codebase, themes, and plugins
├── docker/                 # Container definitions & compose setups
│   ├── Dockerfile          # Multi-stage production container
│   ├── docker-compose.yml  # Multi-container orchestration
│   ├── docker-entrypoint.sh# Container bootstrap script
│   └── instance_manager/   # Isolated dynamic challenge runner microservice
├── docs/                   # Full operational and architecture documentation
├── migrations/             # Database migration versions
├── scripts/                # Utility, maintenance, and execution scripts
│   ├── serve.py            # Local development server runner
│   ├── manage.py           # CLI management commands
│   ├── ping.py             # Database connectivity healthcheck
│   ├── scan_secrets.py     # Pre-commit secret scanning engine
│   └── sanitize_db.py      # Database credential sanitization tool
└── tests/                  # Automated test suites
```

---

## Quickstart

### 1. Local Development (Python 3.10+)
```bash
# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r api/requirements.txt

# Run development server
python scripts/serve.py
```

### 2. Production Docker Deployment
```bash
# 1. Configure Environment
cp conf/.env.example .env
nano .env

# 2. Launch Services with Docker Compose
docker compose -f docker/docker-compose.yml up -d --build

# 3. Verify System Health
curl -i http://localhost/health
```

### 3. Vercel Serverless Deployment
The repository is pre-configured with `vercel.json` pointing to `api/index.py`:
```bash
vercel deploy
```

---

## Documentation

Detailed architecture and operational guides are available in the [`docs/`](docs/) directory:

- [Security Policy & Vulnerability Disclosure](docs/SECURITY.md)
- [System Architecture & Data Flow](docs/ARCHITECTURE.md)
- [Step-by-Step Production Deployment](docs/DEPLOYMENT.md)
- [Database Persistence & Zero-Data-Loss Policy](docs/DATABASE.md)
- [Isolated Challenge Instance Architecture](docs/INSTANCE-ARCHITECTURE.md)
- [Monitoring, Health Checks & Tracing](docs/MONITORING.md)
- [Disaster Recovery & Backup Strategy](docs/DISASTER-RECOVERY.md)
- [OWASP ASVS 5.0 Verification Matrix](docs/SECURITY-CHECKLIST.md)

---

## License

XploitX is open source software licensed under the [Apache 2.0 License](docs/LICENSE).
