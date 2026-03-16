# Register a Startup

**Module:** Workspace
**Status:** Backend endpoints built, AI conversational onboarding not yet implemented

## Overview

The entry point to the workspace. A user who just signed up lands on the platform with no role. They see an "Add Workspace" option, enter their startup name, and a workspace is created instantly. The AI Manager then greets them and starts a conversational onboarding flow to progressively fill in the startup profile.

Minimum required: just the startup name. Everything else is optional and filled in over time.

## User Journey

1. User signs up and lands on the platform (no role assigned)
2. User sees "Add Workspace" button
3. User enters their startup name
4. Workspace is created instantly:
   - Slug auto-generated from the name
   - User auto-added as team member with **founder** role
   - AI **Manager agent** auto-assigned
5. User lands in their new workspace
6. AI Manager greets them and begins conversational onboarding:
   - "Welcome! Tell me about [Startup Name] — what are you building?"
   - Each answer updates the startup profile in real time
7. User can skip the conversation and fill in details manually later

## Technical Details

### Minimum Required Fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | The only required input |

### Auto-Generated on Creation

| Field | Notes |
|-------|-------|
| `slug` | Auto-generated from name (lowercase, hyphenated) |
| Founder team member | Auto-created in `startup_members` table |
| Manager agent | Auto-assigned AI Manager agent |

### Full Startup Profile Fields (All Optional)

| Field | Type | Notes |
|-------|------|-------|
| `tagline` | string(80) | Short tagline |
| `short_description` | string(500) | Brief description |
| `logo_url` | string | URL to uploaded logo |
| `website_url` | string | Startup website |
| `stage` | enum | idea, pre_seed, seed, series_a, series_b, growth |
| `industry` | enum | 15 options (saas, fintech, healthtech, edtech, etc.) |
| `founded_date` | date | When the startup was founded |
| `hq_city` | string | Headquarters city |
| `hq_country` | string | Headquarters country |
| `is_remote` | boolean | Remote-first? |
| `team_size` | integer | Current team size |

### Related Tables (Filled Progressively)

- **Product details** — problem, solution, TAM, business model, product stage
- **Traction metrics** — users, revenue, north star metric, milestones
- **Financial details** — burn rate, runway, cash, fundraising status
- **Funding rounds** — type, amount, date, investors
- **Equity / cap table** — shareholders, ownership %, vesting
- **Documents** — pitch decks, incorporation docs, financials

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/startups` | Create workspace (just name) |
| GET | `/api/v1/startups/mine` | List my startups |
| GET | `/api/v1/startups/{id}` | Get startup details |
| PUT | `/api/v1/startups/{id}` | Update startup profile |

## Acceptance Criteria

- User can create a workspace with just a startup name
- Slug is auto-generated from the name
- Founder is auto-added as a team member
- Manager agent is auto-assigned
- AI Manager initiates conversational onboarding after creation
- All other profile fields can be updated later
- Duplicate slugs handled gracefully

## Pending / Future

- AI conversational onboarding flow (Manager greeting + profile Q&A)
- Logo upload during onboarding
- Profile completion progress indicator
- Public startup profile page (visible to investors)
