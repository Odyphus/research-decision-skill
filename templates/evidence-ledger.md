# Evidence Ledger

Schema version: 3

Trace cites evidence_id. Keep usage, claim, canonical work, artifact, study, alias, relationship, and claim-specific independence identities separate.

## E-001

```json
{
  "evidence_id": "E-001",
  "usage_ids": ["EU-001"],
  "claim_ids": ["C-001"],
  "canonical_work_id": "work:doi:10.0000/example",
  "artifact_id": "artifact:publisher-version",
  "study_id": "study:example-001",
  "aliases": ["doi:10.0000/example", "Example et al. 2026"],
  "source_identity": {
    "author_or_issuer": "Example et al.",
    "title": "Example methods paper",
    "publication_date": "2026-01-01",
    "source_type": "peer_reviewed_paper",
    "stable_locator": "https://doi.org/10.0000/example"
  },
  "relationship": "canonical",
  "independence_status": {
    "C-001": "independent"
  },
  "independence_basis": {
    "C-001": "Distinct study design, participants, and analysis."
  },
  "location": "https://example.org/source",
  "relation": "support",
  "access_status": "available",
  "verification_status": "verified",
  "license_status": "verified_open",
  "limitations": ["Illustrative placeholder; replace before use."],
  "checked_at": "2026-01-01T00:00:00Z",
  "notes": "Evidence identity is separate from artifact and study identity."
}
```
