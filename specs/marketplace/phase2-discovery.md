# Phase 2: Discovery Layer (Search, Filter, Browse)

**Status:** Complete
**Built:** 2026-03-23

## Overview

Upgraded marketplace discovery from basic ILIKE text search to production-quality PostgreSQL-native full-text search with relevance ranking, type-specific filters, faceted counts, and a SearchBackend abstraction for future Elasticsearch swap.

## What Was Built

### SearchBackend Abstraction

`app/services/search.py` — abstracts search behind an interface:

```
SearchBackend (abstract)
  └── PostgresSearchBackend (implementation)
        ├── websearch_to_tsquery full-text search
        ├── ts_rank_cd relevance ranking
        ├── JSONB @> containment filters
        ├── Type-specific JOINs (professional/advisor/founder)
        └── Faceted COUNT queries
```

Swap to Elasticsearch later by implementing `ElasticsearchSearchBackend` — same interface, no endpoint changes.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/marketplace/discover` | Browse all profiles (refactored to use SearchBackend) |
| GET | `/api/v1/marketplace/discover/professionals` | Browse professionals with type-specific filters |
| GET | `/api/v1/marketplace/discover/advisors` | Browse advisors with type-specific filters |
| GET | `/api/v1/marketplace/discover/founders` | Browse founders with type-specific filters |
| GET | `/api/v1/marketplace/search` | Unified full-text search with tsvector relevance ranking |
| GET | `/api/v1/marketplace/search/facets` | Facet counts for filter sidebar |

### Query Parameters

**All endpoints share:**
- `q` — full-text search (uses `websearch_to_tsquery`, supports quotes, negation, OR)
- `skills` — comma-separated skill filter (JSONB containment)
- `location` — partial match
- `sort_by` — `score` (default), `relevance`, `newest`, `rate_low`, `rate_high`
- `page`, `page_size` — pagination
- `include_facets` — return facet counts in response

**Professional-specific (`/discover/professionals`):**
- `min_rate`, `max_rate` — hourly rate range
- `availability` — available, busy, open_to_offers, not_available
- `min_experience` — minimum years of experience

**Advisor-specific (`/discover/advisors`):**
- `domain_expertise` — comma-separated expertise filter
- `investment_stages` — comma-separated stage filter (pre_seed, seed, series_a)
- `fee_structure` — hourly, retainer, equity, pro_bono, success_fee
- `has_booking` — only advisors with cal booking link

**Founder-specific (`/discover/founders`):**
- `looking_for` — filter by role they need (e.g., cto)
- `startup_stage` — idea, pre_seed, seed, series_a
- `industry` — saas, fintech, healthtech, etc.
- `commitment` — full_time, part_time, flexible, advisory
- `remote_ok` — boolean

### Facets Response

Returned when `include_facets=true`:

```json
{
  "profile_types": [{"value": "professional", "count": 5}],
  "skills": [{"value": "python", "count": 8}, {"value": "react", "count": 5}],
  "availability": [{"value": "available", "count": 3}],
  "hourly_rate_ranges": [
    {"value": "0-50", "count": 1},
    {"value": "100-200", "count": 4},
    {"value": "200+", "count": 2}
  ],
  "locations": [{"value": "San Francisco, CA", "count": 3}]
}
```

- Skills: top 20, unnested from JSONB array
- Locations: top 15, grouped by exact location string
- Rate ranges: bucketed via SQL CASE
- All facets respect `is_public = true` and `profile_score >= 40` base filters

### Search Architecture

**Three search layers:**

1. **Full-text search** — `search_vector @@ websearch_to_tsquery('english', query)` with weighted ranking (headline A, bio B, skills C). Handles quoted phrases, negation, OR operators safely.

2. **Structured filtering** — B-tree indexes on typed columns (hourly_rate, availability_status), GIN indexes on JSONB arrays (skills, domain_expertise). Uses `@>` containment for "has ALL these skills" queries.

3. **Sort options** — `ts_rank_cd` for relevance (only when text search active), `created_at DESC` for newest, `profile_score DESC` for top score, `hourly_rate ASC/DESC` for rate sorting.

**Base filters always applied:**
```sql
WHERE is_public = true AND profile_score >= 40
```

### Frontend

Updated `Marketplace.tsx`:
- **Tab bar:** All | Professionals | Advisors | Founders (each calls its own endpoint)
- **Filter sidebar** (toggle via filter icon): skills with counts, availability, hourly rate ranges, locations — all populated from facets API
- **Sort dropdown:** Top Score, Newest, Relevance, Rate Low→High, Rate High→Low
- **Active filter count** badge on filter button
- **Clear filters** action
- Grid adjusts columns when sidebar is open

### Database

**No new tables or migrations.** Phase 2 uses infrastructure created in Phase 1:
- `search_vector` TSVECTOR column (maintained by trigger)
- GIN index on `search_vector` (full-text)
- GIN index on `skills` JSONB (containment)
- GIN trigram index on `headline` (fuzzy matching)
- `pg_trgm` extension (enabled)

## Files

| File | Action | Description |
|------|--------|-------------|
| `app/services/search.py` | Created | SearchBackend + PostgresSearchBackend |
| `app/routers/marketplace.py` | Modified | 6 search endpoints (was 1) |
| `app/schemas/marketplace_profile.py` | Modified | FacetBucket, FacetResponse, PaginatedProfileResponse |
| `frontend/src/lib/api.ts` | Modified | 6 new API functions |
| `frontend/src/pages/Marketplace.tsx` | Modified | Tabs, filters, sort, facets UI |
| `tests/test_marketplace_search.py` | Created | 20 tests |

## Tests

20 new tests covering:
- Discover with filters (type, skills, location)
- Professional-specific filters (rate, availability, experience)
- Advisor-specific filters (expertise, fee structure)
- Founder-specific filters (industry)
- Unified search with relevance ranking
- Facets endpoint with and without type filter
- Sort options

**Total test suite: 211 passed, 0 failures.**
