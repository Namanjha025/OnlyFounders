# Marketplace Discovery

**Module:** Marketplace (TwinVerse)
**Status:** Not Started

## Overview

The discovery layer — how startups find the right people on the marketplace. Browse, search, filter Twins by category, skills, services. View profiles. Talk to Twins before committing.

## User Journey

1. Founder navigates to TwinVerse marketplace
2. Sees a browsable directory of Twins organized by category
3. Can filter by: category (mentor, investor, advisor, etc.), services offered, keywords
4. Can search by name or description
5. Clicks on a Twin → sees their full profile (title, bio, about, services, portfolio)
6. Clicks "Chat" → starts a conversation with the Twin
7. If there's a fit → invites the human to their startup team (existing invite flow)

## Technical Details

### Endpoints

| Method | Path | Description | Who |
|--------|------|-------------|-----|
| GET | `/api/v1/marketplace/twins` | Browse/search all active Twins | Any authenticated user |
| GET | `/api/v1/marketplace/twins/{twin_id}` | View a Twin's full profile | Any authenticated user |
| GET | `/api/v1/marketplace/categories` | List available categories with counts | Any authenticated user |

### Query Parameters for Browse

| Param | Type | Description |
|-------|------|-------------|
| `category` | string | Filter by category (mentor, investor, etc.) |
| `search` | string | Full-text search on name, title, bio, about |
| `service_type` | string | Filter by service type (call, async) |
| `page` | int | Pagination |
| `limit` | int | Results per page |

### Response Format

```json
{
  "twins": [
    {
      "id": "uuid",
      "display_name": "Sarah Chen",
      "title": "Angel Investor & Startup Mentor",
      "category": "investor",
      "bio": "10+ years investing in early-stage startups...",
      "services": [...],
      "is_active": true
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 20
}
```

## Acceptance Criteria

- Users can browse all active Twins on the marketplace
- Twins are filterable by category and searchable by keywords
- Twin profiles show all public info (title, bio, about, services, portfolio)
- Paginated results for large marketplaces
- Only active Twins are shown

## Pending / Future

- Recommended Twins based on startup profile/needs
- Featured/promoted Twin listings
- "Similar to" suggestions
- Sort by popularity, rating, recent activity
- AI-powered matching ("Find me a mentor who knows fintech fundraising")
