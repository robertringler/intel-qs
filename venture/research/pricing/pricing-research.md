# Pricing research

## Observed competitor pricing
- Trustpair: not public. Quote-based usage tiers ("Platform Access", "Custom Access" with up to $1M liability) [F] (S065).
- Eftsure: not public. Scales with annual spend and new vendors per month. Includes a $1M guarantee for contracts after 10 Mar 2025 [F] (S015).
- Account-validation data: Plaid-type APIs cost ~$0.10–0.60 per call with monthly minimums [F, secondary] (S086).
  EWS, JPM and GIACT pricing is not public (S044, S063).
- AP suites bundle verification into subscriptions (S062, S064).
- Enterprise payee-assurance ACVs are **not publicly verifiable**. We do not assert a number.

## Value-based willingness to pay
- Severity anchor [D]: ~$123k mean loss per reported BEC complaint (S001).
- Insurance anchor [F]: social-engineering sublimits are typically $100–250k, and claims can be denied without
  documented verification (S048, S049).
- Frequency anchor [D]: 63% of organisations had BEC attempts in 2024 (95% CrI 59–67%, S006, Beta posterior).
- P(successful loss | attempt) for the ICP: **insufficient evidence for statistical inference.**
  Illustrative expected-loss scenario [M]: at P(loss) = 3% per year and severity $123k, expected annual loss is ~$3.7k
  *before* insurance and reputational costs. A $3–6k subscription therefore needs either higher-risk customers,
  labour savings or insurance value to clear ROI. This is why ARPA is the most sensitive model variable.

## Pricing mechanism chosen
A hybrid model (details in ../../strategy/pricing.md):
1. **Subscription by monthly outbound payment-volume band.** Risk exposure scales with payment volume, not headcount.
2. **Included account verifications, then metered.** This passes through third-party validation costs.
3. **Annual billing as the default**, with a 15% discount. This reduces churn (S041).
4. **Free tier**: one NACHA-file screen per month and up to 25 vendors. This is the product-led entry point and has no card requirement.

Sensitivity: tiers are placed so that the modal customer lands at ~$500/month (≈$6k ARPA). The model's
ARPA range of $2.4k–$15k covers downside and upside, and stress S1 (ARPA ×0.6) halves P(NPV>0).
