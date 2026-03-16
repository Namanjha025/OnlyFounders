# Team Management & Invitations

**Module:** Workspace
**Status:** In Progress

## Overview

Founders build their team inside the workspace by inviting existing platform users. The invited user sees the invite, accepts or declines, and on acceptance is automatically added as a startup team member.

Invited users must already have an account on the platform. Inviting by email (for users not yet registered) is documented as a future enhancement.

## User Journey

1. Founder opens workspace and goes to "Team"
2. Founder searches for a user on the platform
3. Founder creates an invite:
  - Selects a **role** (CTO, advisor, engineer, etc.)
  - Enters a **title** ("Co-Founder & CTO")
  - Describes **responsibilities** ("Lead product engineering")
  - Optionally adds a personal **message**
4. Invite is sent — status is `pending`
5. Invited user sees the pending invite on their dashboard (`/me/invitations`)
6. Invited user reviews invite details and **accepts** or **declines**:
  - **Accept:** `startup_member` record auto-created with role/title/responsibilities from the invite
  - **Decline:** Status updated to `declined`, nothing else happens
7. Founder can view all sent invites and their statuses

## Technical Details

### Invitations Table


| Field              | Type        | Required | Notes                                               |
| ------------------ | ----------- | -------- | --------------------------------------------------- |
| `id`               | UUID        | Auto     | Primary key                                         |
| `startup_id`       | UUID        | Yes      | FK to startups                                      |
| `invited_by`       | UUID        | Yes      | FK to users (who sent it)                           |
| `invited_user_id`  | UUID        | Yes      | FK to users (who's invited)                         |
| `role`             | enum        | Yes      | MemberRole (founder, cofounder, cto, advisor, etc.) |
| `title`            | string(100) | No       | Proposed job title                                  |
| `responsibilities` | text        | No       | What they'll be doing                               |
| `message`          | text        | No       | Personal note from inviter                          |
| `status`           | enum        | Yes      | pending, accepted, declined, expired                |
| `expires_at`       | timestamp   | No       | Optional expiry                                     |
| `responded_at`     | timestamp   | No       | When they accepted/declined                         |
| `created_at`       | timestamp   | Auto     |                                                     |
| `updated_at`       | timestamp   | Auto     |                                                     |


### Endpoints


| Method | Path                                | Description            | Who                    |
| ------ | ----------------------------------- | ---------------------- | ---------------------- |
| POST   | `/api/v1/startups/{id}/invitations` | Send invite            | Startup owner          |
| GET    | `/api/v1/startups/{id}/invitations` | List all sent invites  | Startup owner          |
| GET    | `/api/v1/me/invitations`            | My pending invitations | Any authenticated user |
| PUT    | `/api/v1/invitations/{id}/accept`   | Accept invite          | Invited user only      |
| PUT    | `/api/v1/invitations/{id}/decline`  | Decline invite         | Invited user only      |


### Business Rules

- Only startup owner can send invitations
- Invited user must already exist on the platform
- Cannot send duplicate invite while one is `pending` for the same user + startup
- On **accept**: `startup_member` auto-created with role, title, responsibilities from invite
- On **decline**: status updated, no member created
- Expired invites cannot be accepted
- A user can be re-invited after declining (new invite row created)

## Acceptance Criteria

- Owner can send invite to any existing platform user
- Cannot invite yourself
- Cannot invite someone who's already a team member
- Cannot send duplicate pending invite to same user
- Invited user sees pending invites on their dashboard
- Accept creates `startup_member` with correct role/title/responsibilities
- Decline updates status, no member created
- Expired invites are rejected on accept attempt
- Founder can view all sent invites and statuses

## Pending / Future

- **Invite by email** for users not yet on the platform (known gap)
- In-app notifications for new invites
- Email notifications
- Bulk invite
- Revoke a pending invite
- Role-based permissions matrix (what each role can see/do)
- AI Manager sending invites on behalf of founder

