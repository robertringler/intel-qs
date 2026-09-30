# Deployment

PayeeProof ships as one container image with three commands: `serve` (web), `worker`, and `migrate`
(plus `provision-db`, `gen-keys`, `verify-audit`, `rotate-encryption`).

## Requirements
- PostgreSQL 14+ (16 tested) with PITR backups. Managed options: AWS RDS/Aurora, GCP Cloud SQL, Azure Flexible Server, Neon, Crunchy.
- A container platform: ECS/Fargate, Cloud Run, Fly.io, Render, or Kubernetes.
- TLS termination in front of the web service (a load balancer or reverse proxy).
- SMTP provider (Postmark, SES, SendGrid or similar) with SPF, DKIM and DMARC for your sending domain.
- Optional: Redis (shared rate limits across replicas), Stripe (billing), Sentry (errors).

## 1. Build the image
```bash
docker build -t registry.example.com/payeeproof:1.0.0 .
# behind a TLS-inspecting proxy: docker build --secret id=extra_ca,src=/path/ca.pem -t ... .
docker push registry.example.com/payeeproof:1.0.0
```
Dependencies install from `requirements.lock` with `--require-hashes --only-binary=:all:`. The image runs as UID 10001,
works with a read-only root filesystem (mount `/tmp` as tmpfs), and needs no Linux capabilities.

## 2. Generate secrets (once per environment)
```bash
docker run --rm registry.example.com/payeeproof:1.0.0 payeeproof gen-keys
```
Store the output in your secret manager (AWS Secrets Manager, GCP Secret Manager, Vault or Doppler), **never in git**.
Keys:
| Variable | Purpose | Rotation |
|---|---|---|
| `PP_FIELD_ENCRYPTION_KEYS` | AES-256-GCM keyring `kid:key[,kid:key…]` (first = primary) | Prepend a new key, deploy, run `payeeproof rotate-encryption`, then remove the old key |
| `PP_FINGERPRINT_KEY` | Per-tenant account matching | Do not rotate casually: matching history depends on it |
| `PP_NETWORK_FINGERPRINT_KEY` | Opt-in network fingerprints | As above |
| `PP_AUDIT_CHAIN_KEY` | Audit chain HMAC | Never rotate without a chain-epoch migration (not implemented) |
| `PP_METRICS_TOKEN` | Bearer token for `/metrics` | Any time |

## 3. Provision the database (once)
```bash
export PP_OWNER_DB_PASSWORD=... PP_APP_DB_PASSWORD=...   # from the secret manager
payeeproof provision-db --admin-url postgresql://ADMIN:PASS@HOST:5432/postgres --db-name payeeproof
```
This creates `payeeproof_owner` (schema owner, used only for migrations) and `payeeproof_app` (runtime: no superuser,
no BYPASSRLS, no DDL). On managed Postgres, run it with the master user.

## 4. Configure environment
Copy `.env.example`. Production requirements are enforced at startup, and the process refuses to start otherwise:
- `PP_ENV=production`, `PP_BASE_URL=https://…`, `PP_COOKIE_SECURE=true`, `PP_EMAIL_BACKEND=smtp`.
- MFA cannot be disabled, and the default database password is rejected.
- `PP_DATABASE_URL` uses `payeeproof_app`. `PP_MIGRATION_DATABASE_URL` uses `payeeproof_owner` and is needed only by the migrate job.
- Behind one proxy, set `PP_TRUSTED_PROXY_COUNT=1` so rate limits see the real client IP.
- With more than one web replica, set `PP_REDIS_URL`.

## 5. Release procedure (every deploy)
1. Run `payeeproof migrate` as a one-off job/task (owner credentials). Migrations are transactional.
2. Roll the `web` service (`payeeproof serve --workers 2` per container; scale horizontally). Health check `GET /healthz`;
   readiness `GET /readyz` (DB + schema version).
3. Roll the `worker` service (`payeeproof worker`). One or more replicas is safe, because job claiming uses `SKIP LOCKED`.

## 6. Stripe (optional; billing stays disabled until both secrets are set)
1. Create Products and Prices: Starter, Growth and Scale, each monthly and annual (strategy/pricing.md). Put the price IDs in
   `PP_STRIPE_PRICE_*`.
2. Add a webhook endpoint `https://YOUR_HOST/billing/webhook` for events `checkout.session.completed`,
   `customer.subscription.created|updated|deleted` and `invoice.payment_failed`. Set `PP_STRIPE_WEBHOOK_SECRET`.
3. Configure the Customer Portal in the Stripe dashboard.
4. Test with Stripe test keys and `stripe trigger customer.subscription.updated`.
   **The live Stripe API has not been exercised from this repository.** Signature verification, event handling
   and checkout parameter construction are tested locally, with the Stripe HTTP client mocked at its boundary.

## 7. Local stack
```bash
cp .env.example .env   # fill in passwords + gen-keys output
docker compose up --build
```

## Verified in this repository
- The image built, and `provision-db`, `migrate`, `serve` and `worker` ran from it against PostgreSQL 16 in
  `PP_ENV=production` mode: read-only root FS, `--cap-drop ALL`, `no-new-privileges`, UID 10001.
- `/healthz` and `/readyz` returned ok and ready (schema 0001). The container health check reported healthy.
  HSTS and CSP headers were present.
- Not verified here: a cloud deployment, real SMTP delivery, and live Stripe. No credentials were available.
