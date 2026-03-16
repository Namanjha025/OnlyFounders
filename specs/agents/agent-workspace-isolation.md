# Agent Workspace Isolation

**Module:** Agents
**Status:** Not Started

## Overview

When an agent is added to a startup's team, it gets its own isolated space within the workspace. It shares the same task management system as everyone else, but can only see what's assigned to it. It has its own memory, conversation thread, and calendar.

Clear separation of concerns — an HR agent doesn't see the finance agent's tasks. Each agent operates in its own lane.

## What Each Agent Gets

| Resource | Shared or Isolated | How it works |
|----------|-------------------|--------------|
| **Tasks** | Shared table, scoped view | Agent only sees tasks where `assigned_to = agent_member_id` |
| **Calendar** | Shared table, scoped view | Agent only sees events relevant to its tasks/deadlines |
| **Thread** | Isolated | Agent has its own conversation thread (`messages` filtered by `agent_id`) |
| **Memory** | Isolated | Agent has its own persistent memory per workspace (new table) |
| **Documents** | Shared table, scoped access | Agent can access workspace documents relevant to its tasks |

## Agent Memory

Each agent needs persistent knowledge that survives across conversations — facts it learned, decisions made, context it should remember.

### Agent Memory Table (New)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | UUID | Auto | Primary key |
| `agent_id` | UUID | Yes | FK to agents — which agent |
| `startup_id` | UUID | Yes | FK to startups — which workspace |
| `key` | string | Yes | Memory key (topic/label) |
| `content` | text | Yes | The memory content |
| `created_at` | timestamp | Auto | |
| `updated_at` | timestamp | Auto | |

Unique constraint on `(agent_id, startup_id, key)` — one memory per topic per agent per workspace.

Examples:
```
key: "team_preferences"
content: "The founder prefers async communication. CTO wants detailed technical specs."

key: "hiring_status"
content: "Currently hiring for 2 frontend engineers. Budget is $120k-150k."

key: "recurring_tasks"
content: "Weekly standup summary due every Monday. Monthly investor update due first Friday."
```

## How Scoping Works

### Tasks
When an agent fetches its tasks:
```sql
SELECT * FROM tasks
WHERE startup_id = :startup_id
AND assigned_to = :agent_member_id
```

The agent never sees tasks assigned to other members.

### Calendar
When an agent fetches its calendar:
```sql
SELECT * FROM calendar_events
WHERE startup_id = :startup_id
AND (related_task_id IN (agent's tasks) OR created_by = :agent_member_id)
```

### Thread
When loading conversation history:
```sql
SELECT * FROM messages
WHERE startup_id = :startup_id
AND agent_id = :agent_id
ORDER BY created_at ASC
```

Each agent has completely separate conversation threads.

### Memory
When loading agent memory:
```sql
SELECT * FROM agent_memory
WHERE startup_id = :startup_id
AND agent_id = :agent_id
```

## Agent Execution Context

When an agent is invoked, its context includes:

1. **Agent config** — name, role, system prompt, tools (from `agents` table)
2. **Its tasks** — only tasks assigned to it (from `tasks` table, scoped)
3. **Its memory** — persistent knowledge (from `agent_memory` table)
4. **Its thread** — conversation history (from `messages` table, scoped)
5. **Workspace basics** — startup name, stage, team roster (read-only context)

The agent does NOT see:
- Other agents' tasks
- Other agents' memory
- Other agents' threads
- Financials, cap table, funding (unless explicitly granted)
- Other members' private conversations

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/startups/{id}/agents/{aid}/tasks` | Agent's assigned tasks |
| GET | `/api/v1/startups/{id}/agents/{aid}/memory` | Agent's memory entries |
| PUT | `/api/v1/startups/{id}/agents/{aid}/memory/{key}` | Update a memory entry |
| DELETE | `/api/v1/startups/{id}/agents/{aid}/memory/{key}` | Delete a memory entry |

(Thread/chat endpoints already exist in the agents router)

## Acceptance Criteria

- Agent only sees tasks assigned to it
- Agent has its own persistent memory per workspace
- Agent has its own isolated conversation thread
- Agent cannot access other agents' data
- Agent memory survives across conversations
- Agent execution context includes its config, tasks, memory, and thread
- Memory is scoped per agent per workspace

## Pending / Future

- Agent-to-agent communication (HR agent asks Manager to create a task)
- Agent access permissions (grant an agent access to specific data beyond its scope)
- Agent activity log (what the agent did, when, and why)
- Memory summarization (compress old memories to save tokens)
- Agent performance metrics (tasks completed, response quality)
