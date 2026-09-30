"""Bayesian estimate of annual payment-fraud exposure for a US organisation.

Data [F]: AFP 2025 survey, n=521, 79% experienced attempted/actual payments
fraud in 2024; BEC cited by 63% (S006). Counts are reconstructed as
round(p*n) -- the published percentages are rounded, so the counts carry
+/-0.5pp rounding error, which is small relative to the posterior width.

Prior: Beta(1,1) (uninformative). Posterior: Beta(1+k, 1+n-k).
Caveat [I]: AFP respondents skew toward larger organisations with treasury
functions; the estimate is NOT directly transferable to 20-499-employee firms.
"""
from scipy import stats

n = 521
for label, p in [("any payments fraud (attempted/actual)", 0.79), ("BEC attempted/actual", 0.63)]:
    k = round(p * n)
    post = stats.beta(1 + k, 1 + n - k)
    lo, hi = post.ppf([0.025, 0.975])
    print(f"{label}: k={k}/{n}; posterior mean {post.mean():.3f}; 95% credible interval [{lo:.3f}, {hi:.3f}]")

# Expected annual loss for a firm with no controls, as a scenario (not a fact):
# P(successful BEC loss | attempt) is not published by AFP -> insufficient
# evidence for inference; we report the IC3 per-complaint mean as a severity anchor.
print("IC3 2025 mean reported BEC loss per complaint: $%.0f (3.046e9 / 24768) [D]" % (3.046e9 / 24768))
print("P(loss | attempt) for mid-market: insufficient evidence for statistical inference.")
