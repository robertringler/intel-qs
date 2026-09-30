# Pricing

Mechanism: **tiered subscription by outbound payment-volume band**, annual billing by default at a 15% discount.
Rationale in research/pricing/pricing-research.md.

| Plan | Monthly (annual) | Vendors | File screenings / mo | Users | API | Target buyer |
|---|---|---|---|---|---|---|
| Free | $0 | 25 | 1 | 1 | — | Evaluation; PLG entry |
| Starter | $249 ($2,540/yr) | 150 | 20 | 3 | — | <$2M/month outbound |
| Growth | $599 ($6,110/yr) | 1,000 | unlimited | 10 | yes | $2–20M/month outbound |
| Scale | $1,499 ($15,290/yr) | 5,000 | unlimited | 25 | yes | >$20M/month, multi-entity |

- Plan limits are enforced in code (`payeeproof/billing/plans.py`).
- Metered add-on, available once a provider contract exists: commercial account-owner validation passed through at cost plus 30%.
- **Price sensitivity**: stress test S1 (ARPA ×0.6) halves P(NPV>0) from 79% to 49%. Discounting below Starter is
  therefore value-destroying unless it lifts conversion by more than ~40% [D from the model]. Price tests are run on new
  cohorts only, never by repricing existing customers.
- **Value framing**: sell against expected loss (~$123k mean reported BEC loss, S001), insurance eligibility (S049) and
  audit/bank evidence. Do not sell against a checkbox.
