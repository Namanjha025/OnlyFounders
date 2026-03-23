# Phase 3: Co-founder Finder (Founder-to-Founder Matching)

**Status:** Not Started
**Estimated:** 2 weeks

## Overview

A separate co-founder browse section where founders can find other founders with complementary skills. Uses preference-based weighted scoring across 5 dimensions, two-sided interest expression (both must opt in), and match score precomputation.

Gated behind **profile_score >= 70** to ensure quality matches.

## What to Build

### Matching Algorithm

V1 uses **preference-based weighted scoring** across 5 dimensions (no ML required):

| Dimension | Weight | Logic |
|-----------|--------|-------|
| Skill complementarity | 30% | Founders want *different* skills — score higher when skill overlap is low |
| Industry alignment | 20% | Same or adjacent industry = higher score |
| Stage alignment | 15% | Same startup stage = higher score |
| Preference match | 20% | Does A want what B offers and vice versa (looking_for_roles ↔ skills) |
| Location / remote compatibility | 15% | Both remote_ok, or same city = higher score |

**Match score** = weighted sum, stored as DECIMAL(5,4) in range 0.0000–1.0000.

### Two-sided Interest

Follows Y Combinator's co-founder matching model:
- Founder A expresses interest in Founder B → unidirectional
- If B also expresses interest in A → **mutual match** (both notified)
- Only mutual matches unlock full profile details + contact info
- Prevents spam — you can't see who's interested in you until you also express interest

### New Tables

**`cofounder_interests`** — tracks expressed interest:

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| from_profile_id | UUID FK → marketplace_profiles.id | Who expressed interest |
| to_profile_id | UUID FK → marketplace_profiles.id | Who they're interested in |
| match_score | DECIMAL(5,4) | Computed affinity 0–1 |
| is_mutual | BOOLEAN DEFAULT false | Set true when reciprocated |
| created_at | TIMESTAMPTZ | |

**Unique constraint:** `UNIQUE(from_profile_id, to_profile_id)` — can't express interest twice.

**`cofounder_matches`** — precomputed match scores (optional, for batch compute):

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| profile_a_id | UUID FK | |
| profile_b_id | UUID FK | |
| score | DECIMAL(5,4) | Weighted match score |
| computed_at | TIMESTAMPTZ | When last calculated |

**Unique constraint:** `UNIQUE(profile_a_id, profile_b_id)` — one score per pair.

### Existing Table Changes

`founder_marketplace_profiles` gets additional fields (already present from Phase 1):
- `looking_for_roles` — JSONB array (CTO, Designer, Marketing Lead)
- `equity_offered` — VARCHAR
- `commitment_level` — ENUM
- `remote_ok` — BOOLEAN

No migration needed — these columns already exist.

### Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/marketplace/cofounders` | Browse co-founder profiles (founders only, score >= 70) | Founders only |
| GET | `/api/v1/marketplace/cofounders/matches` | Get computed match scores for current founder | Founders only |
| POST | `/api/v1/marketplace/cofounders/interest/{profile_id}` | Express interest in a founder | Founders, score >= 70 |
| DELETE | `/api/v1/marketplace/cofounders/interest/{profile_id}` | Withdraw interest | Founders |
| GET | `/api/v1/marketplace/cofounders/mutual-matches` | View mutual matches (both sides interested) | Founders |

### Business Rules

- **Gate:** Only founders with `profile_score >= 70` can access co-founder features
- **Excludes self:** Never show the requesting user's own profile in results
- **Sort by match_score** when `sort_by=match_score` — computes affinity relative to the requesting founder
- **Rate limit:** Max 10 interest expressions per day
- **Duplicate prevention:** 409 if interest already expressed
- **Mutual detection:** On expressing interest, check if the other side already expressed interest → if yes, set `is_mutual = true` on both records
- **Contact unlock:** Full profile details (email, phone, linkedin) only visible for mutual matches

### Match Score Computation

For small datasets (<10K founders), compute **on-demand** per request:

```python
def compute_match_score(founder_a, founder_b) -> float:
    skill_score = 1 - jaccard_similarity(a.skills, b.skills)  # Want different skills
    industry_score = 1.0 if a.industry == b.industry else 0.5 if adjacent(a, b) else 0.0
    stage_score = 1.0 if a.startup_stage == b.startup_stage else 0.5
    pref_score = overlap(a.looking_for_roles, b.skills) + overlap(b.looking_for_roles, a.skills)
    location_score = 1.0 if (a.remote_ok and b.remote_ok) else 1.0 if same_city(a, b) else 0.3

    return (
        0.30 * skill_score +
        0.20 * industry_score +
        0.15 * stage_score +
        0.20 * pref_score +
        0.15 * location_score
    )
```

For larger datasets: precompute in batch (nightly job via ARQ/Celery) and store in `cofounder_matches`.

### Frontend

New page at `/marketplace/cofounders`:
- Only visible to founders with score >= 70
- Cards show match % ring, skills comparison, "What they're looking for"
- "Express Interest" button → after click, shows "Interest Sent"
- Mutual matches section: shows profiles where both sides matched + full contact info
- Filter by: role needed, stage, industry, commitment, remote

### Migration

One new migration:
- Create `cofounder_interests` table
- Create `cofounder_matches` table (optional — can defer to V2)
- Add indexes on from_profile_id, to_profile_id

### Tests

~15 tests:
- Browse cofounders (founders only, excludes self)
- Express interest (creates record, detects mutual)
- Withdraw interest
- Mutual matches endpoint
- Rate limiting (10/day)
- Profile score gate (< 70 rejected)
- Match score computation logic

## Future (V2+)

- **Embedding-based similarity:** Use pgvector to embed profiles, cosine similarity for initial candidate retrieval, then preference scoring as re-ranker
- **Gale-Shapley stable matching:** For periodic "Co-Founder Speed Dating" batch events
- **Notifications:** Real-time alerts when a mutual match is created
- **Chat thread:** Auto-create a messaging thread on mutual match
