# API design

- Base path `/api/v1`. Authentication is `Authorization: Bearer pp_<prefix>_<secret>`. API access is available on the Growth and Scale plans.
- Scopes: `vendors:read`, `vendors:write`, `changes:write`, `screenings:read`, `screenings:write`, `audit:read`.
- Errors: `{"error": {"code": "...", "message": "...", "details"?: [...]}}` with HTTP status 401, 402 (plan), 403 (scope),
  404, 409, 422 or 429.
- The OpenAPI document is served at `/api/v1/openapi.json`.
- Design rule: **the API can record change requests but cannot verify or approve them.** Verification and approval
  are human, out-of-band and MFA-protected, so the API cannot become a bypass of the control it evidences.

Endpoint reference: docs/api.md.
