# PostgreSQL backup and disaster recovery

## Current recovery capability

The production target is one verified PostgreSQL custom-format backup per day.
This supports recovery to a backup point, not point-in-time recovery. WAL
archiving/PITR is deliberately out of scope until it is configured and tested.

- Target RPO: up to 24 hours, based on successful daily backups.
- Target RTO: to be defined by the production hosting and deployment plan.

Backups must be stored privately, encrypted, access-controlled, and copied to
storage separate from the PostgreSQL host. Do not put backup files in Git,
static files, media files, or any public bucket.

## Backup database role

The runtime database role must remain a non-superuser without `BYPASSRLS`.
Because all protected application tables use `FORCE ROW LEVEL SECURITY`, the
backup job instead uses a separate non-superuser `BACKUP_DATABASE_USER` with
`BYPASSRLS`, `CONNECT`, schema usage, and read-only table/sequence grants. It
must not be used by Django or the application API. Its password belongs in the
deployment secret manager, not this repository.

## Daily operational workflow

Run from the production environment with database variables provided by a
secret manager or protected deployment environment:

```bash
scripts/backups/backup_postgres.sh
scripts/backups/cleanup_old_backups.sh
```

The backup script verifies the custom archive before marking it complete. A
production scheduler can run this at 02:00 server time, then upload the
verified file to private encrypted off-server storage. Alert on failures, file
size anomalies, failed upload, or failed restore tests; never log credentials,
connection URLs containing passwords, JWTs, or user passwords.

## Restore test

At least regularly, restore the latest verified backup into an isolated
database—not the live database:

```bash
scripts/backups/verify_backup.sh /secure/backups/fotabo_hashi_YYYYMMDD_HHMMSS.dump
scripts/backups/restore_postgres.sh /secure/backups/fotabo_hashi_YYYYMMDD_HHMMSS.dump fotabo_hashi_recovery
```

After restore, verify tables, row counts, foreign keys, migration records,
indexes, RLS enabled/forced flags, RLS policies, login, profile ownership,
blood-request ownership, public content, and audit records. The restore script
refuses to overwrite `DATABASE_NAME` unless `ALLOW_LIVE_RESTORE=true` is set
explicitly; that override is for a controlled emergency only.

## Incident procedures

### Database corruption

1. Stop application writes and preserve evidence.
2. Identify the last verified backup.
3. Restore it into an isolated database.
4. Run integrity and application/RLS verification.
5. Approve the cutover, switch the application, then monitor.

### Server failure

1. Provision replacement infrastructure and PostgreSQL.
2. Retrieve a verified encrypted off-server backup.
3. Restore into the replacement database and run migrations/checks.
4. Verify RLS and application behavior before deploying the backend.

### Accidental deletion

1. Identify the likely deletion time and select the appropriate backup.
2. Restore an isolated copy.
3. Extract only the required records and validate relationships.
4. Apply a reviewed, controlled recovery to production.

Never blindly restore over the live database.
