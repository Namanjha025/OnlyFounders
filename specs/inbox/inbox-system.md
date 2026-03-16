# Inbox System

**Module:** Inbox
**Status:** Not Started

## Overview

The Inbox is a tool the Manager (and other agents) can call to pause execution and request human input. Every inbox item is tied to a specific conversation thread. When the user responds, the agent picks up the reply and resumes.

It is literally human-in-the-loop with a UI layer. The agent sends a message, execution pauses, the human responds, execution continues.

## How It Works

1. Agent is working inside a conversation thread (e.g., Manager reorganizing tasks)
2. Agent hits a point where it needs human input
3. Agent calls the **`/inbox` tool** — this:
   - Creates an inbox item with a type (approval, blocker, reminder, report, etc.)
   - Links it to the current conversation thread (startup + agent + message)
   - Pauses agent execution
4. Inbox item appears in the user's inbox feed
5. User opens the item — sees the full conversation thread with context
6. User replies in the thread (just a normal chat reply)
7. The reply is stored in the `messages` table as a user message
8. Agent detects the response and resumes execution

## User Journey

### Founder receives an approval request

1. Manager is processing a request and needs approval
2. Manager sends to inbox: "I'd like to reassign the pitch deck task from Alice to Bob since Alice is overloaded. Approve?"
3. Founder sees in their inbox: **[Approval] Manager** — "Reassign pitch deck task?"
4. Founder taps it → opens the thread where Manager was working
5. Founder replies: "Approved" (or "No, keep it with Alice")
6. Manager reads the reply and continues accordingly

### Founder receives a weekly report

1. Manager generates a weekly summary (triggered by schedule or milestone)
2. Manager sends to inbox: "Here's your weekly update: 4 tasks completed, 2 blocked, runway at 8 months..."
3. Founder sees: **[Report] Manager** — "Weekly update"
4. Founder opens, reads, optionally replies with follow-up questions
5. Manager responds in the same thread

### Agent needs a document

1. HR agent needs John's tax form to proceed
2. HR agent sends to inbox: "I need John's W-9 form to complete onboarding paperwork. Can you upload it?"
3. Founder sees: **[Blocker] HR Agent** — "Need John's W-9"
4. Founder uploads the document and replies: "Done, uploaded"
5. HR agent resumes

## Technical Details

### Inbox Items Table

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | UUID | Auto | Primary key |
| `startup_id` | UUID | Yes | FK to startups — which workspace |
| `agent_id` | UUID | Yes | FK to agents — which agent sent it |
| `recipient_id` | UUID | Yes | FK to users — who it's for |
| `thread_message_id` | UUID | Yes | FK to messages — the specific message that triggered the pause |
| `type` | enum | Yes | `approval`, `blocker`, `reminder`, `report`, `update`, `info` |
| `summary` | string | Yes | Short preview shown in inbox list |
| `status` | enum | Yes | `unread`, `read`, `resolved` |
| `requires_action` | boolean | Yes | Does the user need to do something? |
| `resolved_at` | timestamp | No | When the user responded / resolved it |
| `created_at` | timestamp | Auto | |
| `updated_at` | timestamp | Auto | |

### Inbox Item Types

| Type | Description | Requires action |
|------|-------------|----------------|
| `approval` | Agent needs a yes/no decision | Yes |
| `blocker` | Something is blocking the agent, needs human help | Yes |
| `reminder` | Upcoming deadline or follow-up | No (informational, but can reply) |
| `report` | Periodic update (weekly summary, progress report) | No (informational, but can reply) |
| `update` | Status change or event notification | No |
| `info` | General message from agent to user | No |

### Endpoints

| Method | Path | Description | Who |
|--------|------|-------------|-----|
| GET | `/api/v1/me/inbox` | List my inbox items (filterable by status, type) | Any authenticated user |
| GET | `/api/v1/me/inbox/{item_id}` | Get inbox item details | Recipient only |
| PUT | `/api/v1/me/inbox/{item_id}/read` | Mark as read | Recipient only |
| PUT | `/api/v1/me/inbox/{item_id}/resolve` | Mark as resolved | Recipient only |
| GET | `/api/v1/me/inbox/unread-count` | Get count of unread items | Any authenticated user |

### Agent-Side (Tool)

The inbox is exposed as a tool the agent can call:

```python
{
    "name": "send_to_inbox",
    "description": "Pause execution and send a message to a user's inbox. Use when you need human input, approval, or want to send a report/reminder.",
    "parameters": {
        "recipient_id": "UUID of the user (usually the founder)",
        "type": "approval | blocker | reminder | report | update | info",
        "summary": "Short preview for the inbox list",
        "message": "Full message content (saved in the conversation thread)"
    }
}
```

When the agent calls this tool:
1. The message is saved in the `messages` table (in the current thread)
2. An inbox item is created pointing to that message
3. Agent execution pauses (returns a "waiting for human input" state)

### Reply Flow

The user's reply doesn't go through a special inbox endpoint. They just reply in the conversation thread:
- `POST /api/v1/startups/{id}/chat/invoke` (for Manager threads)
- `POST /api/v1/startups/{id}/agents/{aid}/chat/invoke` (for other agent threads)

The reply:
1. Gets saved as a user message in the `messages` table
2. The inbox item status is updated to `resolved`
3. The agent picks up the reply and resumes execution

### How Replies Resume Agent Execution

Two possible approaches:

**Option A: Polling** — Agent periodically checks for new messages in the thread. Simple but not real-time.

**Option B: Event-driven** — When a user replies to a thread with a pending inbox item, trigger the agent to resume. More complex but instant.

For v1, Option A (polling or on-next-invoke) is fine. The agent resumes when the thread is next invoked.

## Acceptance Criteria

- Agents can send messages to a user's inbox via the `send_to_inbox` tool
- Each inbox item is linked to a conversation thread
- User can list their inbox items, filtered by status and type
- User can open an inbox item and see the full conversation thread
- User can reply in the thread, which resolves the inbox item
- Unread count is available for UI badges
- Inbox items have types: approval, blocker, reminder, report, update, info
- Agent execution pauses after sending to inbox
- Agent resumes when the user replies in the thread

## Pending / Future

- Push notifications (email, mobile) for new inbox items
- Priority levels for inbox items (urgent approval vs FYI report)
- Scheduled inbox items (Manager sends weekly report every Monday)
- Batch resolve (mark multiple items as read/resolved)
- Inbox filters and search
- Snooze an inbox item ("remind me in 2 hours")
- Escalation — if founder doesn't respond within X time, re-notify
