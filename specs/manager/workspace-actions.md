# Workspace Actions

**Module:** Manager
**Status:** Not Started

## Overview

The Manager isn't just a chatbot — it can take real actions in the workspace on behalf of the founder. Every API endpoint available in the workspace is a potential action the Manager can perform through tool calling.

Think of the Manager as having API access to the entire workspace. The founder says "invite John as CTO" and the Manager calls the invitation API. The founder says "create a task for the pitch deck" and the Manager calls the task API.

## Available Actions

The Manager can perform all workspace actions. These map directly to existing API endpoints:

### Startup Profile
| Action | What it does | API |
|--------|-------------|-----|
| Update startup info | Change name, stage, industry, description, etc. | `PUT /startups/{id}` |
| Update product details | Problem, solution, TAM, competitive advantage | `PUT /startups/{id}/product` |
| Update traction | Users, revenue, north star metric | `PUT /startups/{id}/traction` |
| Update financials | Burn rate, runway, cash | `PUT /startups/{id}/financial` |

### Team Management
| Action | What it does | API |
|--------|-------------|-----|
| Send invite | Invite a platform user to join the team | `POST /startups/{id}/invitations` |
| View pending invites | Check invitation statuses | `GET /startups/{id}/invitations` |
| Update member | Change role, title, responsibilities | `PUT /startups/{id}/members/{mid}` |
| Remove member | Remove someone from the team | `DELETE /startups/{id}/members/{mid}` |

### Task Management
| Action | What it does | API |
|--------|-------------|-----|
| Create task | Create a new task with title, description, priority | `POST /startups/{id}/tasks` |
| Assign task | Assign a task to a team member | `PUT /startups/{id}/tasks/{tid}` |
| Update task status | Mark as in progress, blocked, review, completed | `PUT /startups/{id}/tasks/{tid}` |
| Delete task | Remove a task | `DELETE /startups/{id}/tasks/{tid}` |
| Create calendar event | Add a deadline, meeting, reminder, milestone | `POST /startups/{id}/calendar` |

### Funding & Equity
| Action | What it does | API |
|--------|-------------|-----|
| Add funding round | Record a new funding event | `POST /startups/{id}/funding-rounds` |
| Update cap table | Add/update shareholders | `POST /startups/{id}/equity` |

### Documents
| Action | What it does | API |
|--------|-------------|-----|
| List documents | Show what docs exist | `GET /startups/{id}/documents` |
| Generate upload link | Help founder upload a document | `POST /startups/{id}/documents/upload-url` |

## How Actions Work (Tool Calling)

The Manager uses LLM tool calling to execute actions:

1. Founder says: "Invite sarah@example.com as our advisor"
2. Manager parses the intent → **send_invitation** tool
3. Manager looks up the user by email
4. Manager calls the invitation API with role=advisor
5. Manager confirms: "Done — I've sent Sarah an invitation to join as an advisor."

Each action is exposed as a tool the LLM can call:

```python
tools = [
    {
        "name": "send_invitation",
        "description": "Invite a platform user to join the startup team",
        "parameters": {
            "invited_user_id": "UUID of the user to invite",
            "role": "Team role (cto, advisor, employee, etc.)",
            "title": "Job title",
            "responsibilities": "What they'll be doing",
            "message": "Personal note"
        }
    },
    {
        "name": "create_task",
        "description": "Create a new task in the workspace",
        "parameters": {
            "title": "Task title",
            "description": "Task details",
            "priority": "low, medium, high, urgent",
            "assigned_to": "UUID of the team member",
            "due_date": "Deadline"
        }
    },
    # ... one tool per action
]
```

## Confirmation & Safety

- **Destructive actions** (delete member, delete task) require confirmation from the founder
- Manager says: "I'm about to remove Bob from the team. Confirm?" before executing
- **Read actions** (list tasks, view financials) execute immediately
- **Create/update actions** execute immediately but Manager confirms what was done
- All actions are logged in the conversation history

## Acceptance Criteria

- Manager can perform all workspace CRUD operations via tool calling
- Founder can ask the Manager to do anything they could do through the UI
- Manager confirms actions after executing them
- Destructive actions require explicit confirmation
- Actions respect role-based access (team member can't ask Manager to do founder-only things)
- All actions are logged in conversation history
- If an action fails, Manager explains what went wrong

## Pending / Future

- Agent-to-agent delegation (Manager assigns tasks to other AI agents)
- Scheduled actions ("remind me to follow up on Friday")
- Batch actions ("create tasks for all the items on this list")
- Undo support for recent actions
- Action approval workflows (Manager proposes, founder approves)
