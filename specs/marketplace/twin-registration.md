# Twin Registration

**Module:** Marketplace (TwinVerse)
**Status:** Not Started

## Overview

Any user on OnlyFounders can create their AI Twin on the marketplace. The Twin is their receptionist — it knows about them and represents them to anyone who discovers their profile.

Registration is AI-guided. An AI walks the user through providing their info — role, background, services, portfolio, docs. The more they add, the smarter their Twin becomes. The Twin only knows what's in its own table — no workspace data, no cross-contamination.

## User Journey

1. User is signed in on OnlyFounders
2. User navigates to TwinVerse — "Create your Twin"
3. AI-guided registration begins:
   - "What do you do?" → role/title
   - "Tell me about yourself" → bio, background
   - "What services do you offer?" → services list
   - "Upload your portfolio or relevant docs" → documents
   - "Anything else your Twin should know?" → textual memory
   - "Drop your Calendly link for bookings" → calendly URL
4. Twin is created and live on the marketplace
5. User can update their Twin anytime — add more info, update services, upload new docs
6. People start discovering and chatting with the Twin

## Technical Details

### Twins Table

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | UUID | Auto | Primary key |
| `user_id` | UUID | Yes | FK to users — who owns this Twin |
| `display_name` | string | Yes | Name shown on marketplace |
| `title` | string | Yes | Role/title (e.g., "Startup Mentor", "Angel Investor") |
| `category` | enum | Yes | mentor, investor, advisor, freelancer, student, club, accelerator, vc, other |
| `bio` | text | No | Short bio for the marketplace listing |
| `about` | text | No | Detailed about section — background, experience, expertise |
| `services` | JSONB | No | List of services offered (e.g., [{name, description, type}]) |
| `calendly_url` | string | No | Calendly link for booking calls |
| `portfolio_url` | string | No | External portfolio link |
| `memory` | text | No | Free-form textual memory — anything the user wants the Twin to know |
| `system_prompt` | text | No | Auto-generated or custom system prompt for the Twin's AI |
| `is_active` | boolean | Yes | Whether the Twin is visible on marketplace |
| `created_at` | timestamp | Auto | |
| `updated_at` | timestamp | Auto | |

### Twin Documents Table

Separate from workspace documents. These are portfolio pieces, resumes, case studies, etc.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | UUID | Auto | Primary key |
| `twin_id` | UUID | Yes | FK to twins |
| `name` | string | Yes | Document name |
| `s3_key` | string | Yes | S3 object key |
| `file_type` | string | No | MIME type |
| `file_size` | integer | No | Size in bytes |
| `category` | enum | No | resume, portfolio, case_study, certification, other |
| `created_at` | timestamp | Auto | |

### Twin Services (within JSONB)

```json
[
  {
    "name": "1:1 Mentorship Call",
    "description": "30-min call to discuss your startup strategy",
    "type": "call"
  },
  {
    "name": "Pitch Deck Review",
    "description": "Detailed feedback on your pitch deck",
    "type": "async"
  },
  {
    "name": "Investment Screening",
    "description": "I'll review your startup for potential investment",
    "type": "call"
  }
]
```

### Endpoints

| Method | Path | Description | Who |
|--------|------|-------------|-----|
| POST | `/api/v1/twins` | Create your Twin | Authenticated user |
| GET | `/api/v1/twins/me` | Get my Twin | Twin owner |
| PUT | `/api/v1/twins/me` | Update my Twin | Twin owner |
| DELETE | `/api/v1/twins/me` | Deactivate my Twin | Twin owner |
| POST | `/api/v1/twins/me/documents/upload-url` | Upload a doc to Twin profile | Twin owner |
| POST | `/api/v1/twins/me/documents/confirm-upload` | Confirm doc upload | Twin owner |
| GET | `/api/v1/twins/me/documents` | List my Twin's documents | Twin owner |
| DELETE | `/api/v1/twins/me/documents/{doc_id}` | Delete a Twin document | Twin owner |

### Privacy Model

- The Twin ONLY has access to data in the `twins` table and `twin_documents` table
- No access to workspace data (startups, tasks, financials, etc.)
- No access to other users' data
- The Twin's AI system prompt is built exclusively from its own table data
- Clear sandboxing — the Twin is its own isolated context

## Acceptance Criteria

- User can create a Twin with display name, title, and category
- AI-guided registration collects info progressively
- User can upload portfolio documents to their Twin profile
- Twin data is completely isolated from workspace data
- User can update/deactivate their Twin anytime
- Services are stored as structured JSON
- Calendly link is stored for booking integration

## Pending / Future

- AI-guided registration conversation flow
- Auto-generate system prompt from Twin data
- Twin analytics (how many people chatted, how many booked calls)
- Verification/badge system for Twins
- Reviews/ratings from people who interacted with the Twin
- Pricing for paid services (billing integration)
