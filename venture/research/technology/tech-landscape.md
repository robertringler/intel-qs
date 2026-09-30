# Technology landscape

## NACHA file format (the product's primary input)
- Fixed-width, 94-character records: File Header (1), Batch Header (5), Entry Detail (6), Addenda (7),
  Batch Control (8), File Control (9). Blocking factor 10, padded with '9' records.
- Entry Detail carries: transaction code (22/23/24/27/28/29/32/33/34/37/38/39 …), receiving DFI routing (8 digits +
  check digit), DFI account number (17), amount in cents (10), individual ID (15), receiver name (22), trace number.
- Routing check digit: 3·(d1+d4+d7) + 7·(d2+d5+d8) + (d3+d6+d9) ≡ 0 mod 10.
- Prenote: zero-dollar entry (transaction codes 23/28/33/38) used to validate account structure.
  It is a Nacha-recognised validation method and needs no third-party vendor (S076).
- ERPs produce these files natively (S083). Screening them before upload is therefore a zero-integration wedge.

## Account validation methods
| Method | Proves | Cost | Availability |
|---|---|---|---|
| Callback to previously known contact | Requester authenticity | Staff time | Universal |
| Prenote | Account exists and accepts entries (weak on ownership) | ~Free | Universal via ODFI |
| Micro-deposits | Control of account | Days | Universal |
| Account-owner validation APIs (EWS, GIACT/LSEG, JPM AVS) | Ownership/status match | Per inquiry, contract required | Commercial (S044, S063) |
| Vendor self-attestation via secure link | Vendor intent (weak if email is compromised) | Free | Built-in |

PayeeProof orchestrates these through a provider interface. v1 ships the callback, prenote and attestation methods,
all of which work without third-party contracts. Commercial validation APIs plug into the same interface once a
contract exists. **No commercial adapter is shipped or claimed in v1.**

## AI
Considered for parsing vendor change-request emails. Deferred: prompt injection through attacker-controlled emails
is a direct attack path, and deterministic rules cover the named high-risk events. See architecture/architecture.md
§AI for the decision record.
