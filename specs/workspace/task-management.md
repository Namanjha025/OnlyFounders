# Task Management

**Module:** Workspace
**Status:** Backend endpoints built

## Overview

The task board for the startup workspace. Tasks are the core unit of work. The AI Manager coordinates task creation and assignment, helping founders break down goals into actionable items and track progress across the team.

Includes calendar events for deadlines, meetings, reminders, and milestones.

## User Journey

1. Founder (or AI Manager) creates a task in the workspace
2. Task gets a title, description, priority, and optionally assigned to a team member
3. Task appears on the task board with status `pending`
4. Assigned team member sees their tasks
5. Team member updates status as they progress: pending -> in_progress -> review -> completed
6. Due dates appear on the workspace calendar
7. AI Manager can suggest tasks, reprioritize, and nudge on overdue items

## Technical Details

### Task Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `startup_id` | UUID | FK to startups |
| `title` | string | Task title |
| `description` | text | Detailed description |
| `status` | enum | pending, in_progress, blocked, review, completed |
| `priority` | enum | low, medium, high, urgent |
| `assigned_to` | UUID | FK to startup_members |
| `due_date` | date | When it's due |
| `completed_at` | timestamp | When marked completed |
| `created_at` | timestamp | |
| `updated_at` | timestamp | |

### Calendar Event Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `startup_id` | UUID | FK to startups |
| `title` | string | Event title |
| `event_type` | enum | task_due, meeting, reminder, milestone, deadline |
| `start_time` | timestamp | Event start |
| `end_time` | timestamp | Event end |

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/startups/{id}/tasks` | List tasks (filterable by status, assignee) |
| POST | `/api/v1/startups/{id}/tasks` | Create task |
| GET | `/api/v1/startups/{id}/tasks/{tid}` | View task |
| PUT | `/api/v1/startups/{id}/tasks/{tid}` | Update status/assignee/priority |
| DELETE | `/api/v1/startups/{id}/tasks/{tid}` | Delete task |
| GET | `/api/v1/startups/{id}/calendar` | List calendar events |
| POST | `/api/v1/startups/{id}/calendar` | Create event |
| DELETE | `/api/v1/startups/{id}/calendar/{eid}` | Delete event |

## Acceptance Criteria

- Tasks can be created with title, description, status, priority, assignee
- Status flows: pending -> in_progress -> review -> completed (or -> blocked)
- Tasks filterable by status and assignee
- Calendar events track deadlines, meetings, reminders, milestones
- Due dates visible on calendar

## Pending / Future

- AI Manager creating/assigning tasks from conversations
- Task comments and activity log
- Subtasks / checklists
- Task dependencies
- Notifications for assignments and due dates
- Recurring tasks
