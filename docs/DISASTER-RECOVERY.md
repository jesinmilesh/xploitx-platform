# XploitX CTF Platform — Disaster Recovery & Backup Plan

## 1. Recovery Objectives

- **Recovery Point Objective (RPO)**: <= 1 Hour (Maximum acceptable data loss in catastrophic event).
- **Recovery Time Objective (RTO)**: <= 15 Minutes (Target time to restore platform service).

---

## 2. Automated Backup Strategy

### Database Snapshots
Run an hourly cron job on the production host or utilize cloud managed database automated backups (Point-in-Time Recovery):

```bash
#!/usr/bin/env bash
# /opt/scripts/backup_xploitx.sh
BACKUP_DIR="/opt/backups/xploitx"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"

# MariaDB/MySQL Backup
docker compose -f /opt/xploitx/docker/docker-compose.yml exec -T db \
  mariadb-dump -u ctfd --password="$DB_PASSWORD" --single-transaction --quick ctfd \
  | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Retain backups for 14 days
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +14 -delete
```

### Uploads & Static Assets
Challenge files and uploaded assets in `/var/uploads` should be synced continuously or backed up daily:
```bash
rsync -avz /opt/xploitx/.data/CTFd/uploads/ /opt/backups/xploitx/uploads/
```

---

## 3. Disaster Recovery Scenarios

| Disaster Scenario | Mitigation & Recovery Steps |
| :--- | :--- |
| **Database Corruption / Crash** | Stop ctfd container, restore latest uncorrupted snapshot using `mariadb < backup.sql`, restart cluster. |
| **Host VM Failure** | Provision new VM, clone repository, copy `.env`, restore database from offsite backup, run `docker compose up -d`. |
| **Accidental Bad Deployment** | Run `git checkout <previous_commit> && docker compose up -d --build`. Data in database volume remains intact. |
| **Challenge Instance Host DoS** | Restart `instance-manager` service. The reaper automatically terminates runaway or hung containers. |
