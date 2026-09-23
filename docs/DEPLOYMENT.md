# XploitX CTF Platform — Production Deployment Guide

## 1. Prerequisites

- A Linux Host (Ubuntu 22.04 LTS or 24.04 LTS recommended)
- Minimum Specs: 4 vCPU, 8 GB RAM, 50 GB SSD
- Docker Engine 24.0+ and Docker Compose v2.20+
- A registered domain name pointing to the server's public IP (e.g. `ctf.xploitx.org`)

---

## 2. Environment Configuration

1. Clone the repository:
   ```bash
   git clone https://github.com/jesinmilesh/xploitx-platform.git /opt/xploitx
   cd /opt/xploitx
   ```

2. Copy the template and generate secrets:
   ```bash
   cp .env.example .env
   ```

3. Generate secure secrets:
   ```bash
   # Generate SECRET_KEY
   python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
   
   # Generate INSTANCE_MANAGER_SECRET
   python3 -c "import secrets; print('INSTANCE_MANAGER_SECRET=' + secrets.token_hex(32))"
   
   # Generate DB Password
   python3 -c "import secrets; print('DB_PASSWORD=' + secrets.token_urlsafe(16))"
   ```

4. Configure `.env`:
   - Set `ENVIRONMENT=production`
   - Set `SESSION_COOKIE_SECURE=true`
   - Set `TRUSTED_HOSTS=ctf.xploitx.org`
   - Update SMTP / Brevo credentials for email verification and password reset.

---

## 3. Starting the Production Cluster

Run the cluster with Docker Compose:
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Verify service health:
```bash
docker compose -f docker/docker-compose.yml ps
```
All services (`ctfd`, `db`, `cache`, `nginx`, `instance-manager`) should report `healthy` or `running`.

---

## 4. Verification & Health Check

Test the public health endpoint:
```bash
curl -i http://localhost/health
```
Expected response:
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{"status": "healthy", "database": "up", "cache": "up"}
```

---

## 5. Zero-Data-Loss Update Procedure

When upgrading the platform code:
```bash
# 1. Take a pre-deployment database backup
docker compose -f docker/docker-compose.yml exec db mariadb-dump -u ctfd -p ctfd > /opt/backups/ctfd_pre_deploy_$(date +%s).sql

# 2. Pull new code
git pull origin main

# 3. Rebuild and restart application containers (database volume persists)
docker compose -f docker/docker-compose.yml up -d --build --no-deps ctfd instance-manager nginx

# 4. Verify post-deploy health
curl -f http://localhost/health || (echo "Deployment failed, rolling back" && exit 1)
```

---

## 6. Rollback Procedure

If an update fails:
```bash
# Revert code to previous commit
git checkout HEAD~1

# Restart services
docker compose -f docker/docker-compose.yml up -d --build

# If database changes need to be restored:
docker compose -f docker/docker-compose.yml exec -T db mariadb -u ctfd -p ctfd < /opt/backups/ctfd_pre_deploy_<timestamp>.sql
```
