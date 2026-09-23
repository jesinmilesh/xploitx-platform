# XploitX CTF Platform — Database Architecture & Persistence Policy

## 1. Zero-Data-Loss Invariant

> [!CAUTION]
> Under **NO circumstances** may any code deployment, container reboot, or background task execute:
> - `DROP DATABASE`
> - `DROP TABLE`
> - `TRUNCATE`
> - Destructive automated reset/seed scripts in production.

All production data (users, teams, challenges, submissions, solves, awards, tracking) must survive:
- Git pulls / updates
- Container rebuilds (`docker compose down && docker compose up`)
- Server restarts
- Temporary database connectivity interruptions

---

## 2. Storage & Persistence Engine

### Production Setup
- **Storage Layer**: Dedicated Docker persistent volume (`../.data/mysql:/var/lib/mysql`) or managed cloud database (AWS RDS Aurora / PostgreSQL / Azure Database).
- **Charset & Collation**: `utf8mb4` with `utf8mb4_unicode_ci` ensuring full international character support and emoji compatibility for team/user names.
- **Connection Pooling**:
  ```python
  SQLALCHEMY_ENGINE_OPTIONS = {
      "pool_size": 10,
      "max_overflow": 20,
      "pool_pre_ping": True,  # Automatically recycles stale/broken connections
      "pool_recycle": 3600,   # Recycles connections every hour
  }
  ```

---

## 3. Database Indexes

Key collections have explicit indexes and constraints to ensure sub-millisecond query performance during high-concurrency competition rushes:

| Table | Index Columns | Purpose |
| :--- | :--- | :--- |
| `users` | `email` (UNIQUE), `name` (UNIQUE) | Fast authentication and registration lookup |
| `teams` | `name` (UNIQUE), `captain_id` | Fast team validation and captain verification |
| `challenges` | `id`, `category`, `state` | Fast challenge listing and category filtering |
| `solves` | `(challenge_id, user_id)` (UNIQUE) | Race condition prevention on user flag submission |
| `solves` | `(challenge_id, team_id)` (UNIQUE) | Race condition prevention on team flag submission |
| `tracking` | `(user_id, date)`, `ip` | IP tracking and suspicious activity correlation |
| `challenge_instances` | `instance_id` (UNIQUE), `user_id`, `expires_at` | Rapid instance lookup and lifecycle reaping |

---

## 4. Migration Strategy

- Schema changes are managed via **Flask-Migrate (Alembic)**.
- Migrations are versioned and stored under `migrations/versions/`.
- Every migration must be non-destructive (adding nullable columns or columns with safe defaults).
- Destructive column removals are executed only after multi-phase deprecation.
- To apply migrations manually:
  ```bash
  python scripts/manage.py db upgrade
  ```
