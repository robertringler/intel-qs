# Operations runbook

## Monitoring
- **Health:** `/healthz` (process) and `/readyz` (database and schema). Alert on readiness failing for more than 2 minutes.
- **Metrics:** `GET /metrics` with `Authorization: Bearer $PP_METRICS_TOKEN` (Prometheus). Key series:
  - `pp_http_requests_total{status}`: alert on a 5xx rate above 1% over 5 minutes.
  - `pp_http_request_seconds`: alert on p95 above 1 s.
  - `pp_login_failures_total`: spikes indicate credential stuffing.
  - `pp_jobs_total{result="error"}`: see the jobs section below.
  - `pp_screenings_total`, `pp_screening_findings_total{rule}`: product usage and fraud signals.
- **Logs:** JSON on stdout with `request_id`. API keys and secrets are redacted. Ship them to your log platform.
- **Errors:** set `PP_SENTRY_DSN` to enable Sentry. Request bodies, cookies and headers are scrubbed.

## Jobs
- Inspect: `SELECT kind, status, attempts, last_error FROM jobs WHERE status <> 'done' ORDER BY id DESC LIMIT 50;`
- Failed jobs stop after `max_attempts`, with exponential backoff (15 s doubling, capped at 1 h). To retry one:
  `UPDATE jobs SET status='queued', attempts=0, run_at=now() WHERE id=…;`
- Stale `running` jobs (worker crash) are re-queued automatically after 15 minutes.
- The daily reminder job (`daily_reminders`, 14:00 UTC) schedules itself.

## Backups and disaster recovery
- **RPO 5 min / RTO 1 h target.** Use managed PostgreSQL with point-in-time recovery (WAL archiving) and daily
  snapshots retained 35 days. Keep a cross-region snapshot copy.
- Keys live in the secret manager, not the database. **Back up the keys separately.** Without
  `PP_FIELD_ENCRYPTION_KEYS`, account numbers are unrecoverable. Without `PP_AUDIT_CHAIN_KEY`, audit chains cannot be verified.
- **Quarterly restore drill:**
  1. Restore a snapshot into staging.
  2. Run `payeeproof migrate` (no-op), then `payeeproof verify-audit --org <id>` for a sample of orgs.
  3. Open the app and screen a test file.
- **Region loss:** restore the latest PITR into the secondary region, point the services at it, update DNS.

## Incident response
1. **Suspected data breach:**
   - Revoke sessions: `UPDATE sessions SET revoked_at=now() WHERE revoked_at IS NULL;`
   - Rotate DB passwords, then rotate `PP_FIELD_ENCRYPTION_KEYS` (prepend a new key, deploy, `payeeproof rotate-encryption`).
   - Preserve logs. Notify affected customers per contract and state law.
2. **Customer reports a fraud loss:** export the evidence pack and audit CSV for the period. Verify the chain
   (`/audit/verify` or CLI). Provide the screening certificate(s) for the run in question.
3. **Audit chain verification fails:** treat it as a security incident. The failing `seq` identifies the first altered
   event. Compare against backups.

## Routine tasks
- Rotate `PP_METRICS_TOKEN` and the SMTP credentials yearly.
- Refresh lock files monthly (`uv pip compile --generate-hashes`), then run `pip-audit` and rebuild.
- Tenant deletion (contract end plus retention period): as the schema owner, with the audit trigger temporarily disabled,
  in one transaction, delete from `organizations` (cascades), then re-enable the trigger. Record the action in a ticket.
