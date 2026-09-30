# API reference (v1)

Authentication: `Authorization: Bearer pp_<prefix>_<secret>`. Create keys under **API** in the app (Growth and Scale plans).
Machine-readable spec: `GET /api/v1/openapi.json`.

| Method | Path | Scope | Description |
|---|---|---|---|
| GET | `/api/v1/health` | none | Liveness |
| POST | `/api/v1/screenings` | `screenings:write` | Multipart `file` = NACHA file. Returns run and per-entry findings (201) |
| GET | `/api/v1/screenings/{id}?include_entries=true` | `screenings:read` | Run status/findings |
| GET | `/api/v1/vendors?q=&limit=&offset=` | `vendors:read` | List vendors |
| POST | `/api/v1/vendors` | `vendors:write` | Create vendor (`name`, `legal_name`, `external_ref`, `contact_*`) |
| POST | `/api/v1/change-requests` | `changes:write` | Record a bank-detail change (`vendor_id`, `routing_number`, `account_number`, `account_type`, `channel`, `notes`). It is **not** verified or approved by this call |
| GET | `/api/v1/audit/verify` | `audit:read` | Verify the org's audit hash chain |

## Example: screen before release (ERP integration)
```bash
curl -sS -H "Authorization: Bearer $PP_KEY" -F "file=@payments_2026-10-01.ach" \
  https://app.example.com/api/v1/screenings | jq '{status, risk_level, rule_counts}'
```
`status` is `clear`, `needs_review` or `blocked`. Recommended ERP behaviour: upload to the bank only if `status == "clear"`,
or after an approver releases the run in the app. Compare the run's `file_sha256` with the file you upload.

Rule codes: R001 unknown account · R002 unverified · R003 recently changed · R004 first payment · R005 amount anomaly ·
R006 name mismatch · R007 duplicate · R008 invalid routing · R009 large round amount · R010 account shared by vendors ·
R011 previously flagged · R012 debit entry · R013 dual-approval threshold · R014 network-flagged · R015 network-verified ·
R016 IAT entry · R017 file integrity · R018 prenote.

Rate limit: 600 requests per minute per key, returning 429 with `{"error": {"code": "rate_limited"}}`.
