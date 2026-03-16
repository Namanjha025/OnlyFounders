# Agent Registry

**Module:** Agents
**Status:** Scaffolded (CRUD endpoints exist)

## Overview

The agent registry is the catalog of all AI agents available on the platform. Each agent is a row in the `agents` table with its own name, description, tools, system prompt, and skills. Think of it as a resume for an AI employee.

Founders browse the registry, find an agent that fits their needs, and add it to their team.

## Current State

The `agents` table and basic CRUD endpoints already exist:

### Agents Table (Existing)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `name` | string | Agent name (e.g., "HR Agent") |
| `slug` | string | Unique slug |
| `description` | text | What the agent does |
| `agent_type` | enum | platform, marketplace |
| `system_prompt` | text | The agent's base system prompt |
| `skills` | JSONB | List of skills/capabilities |
| `tools` | JSONB | List of tools the agent can use |
| `is_active` | boolean | Whether the agent is available |
| `created_at` | timestamp | |
| `updated_at` | timestamp | |

### Existing Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/agents` | List all active agents |
| GET | `/api/v1/agents/{id}` | Get agent details |
| POST | `/api/v1/agents` | Create agent (admin) |
| PUT | `/api/v1/agents/{id}` | Update agent |
| GET | `/api/v1/startups/{id}/agents` | List agents on my team |
| POST | `/api/v1/startups/{id}/agents` | Add agent to team |
| DELETE | `/api/v1/startups/{id}/agents/{aid}` | Remove agent from team |

## What's Missing

- Agent "resume" — a richer profile (experience, specialties, example tasks)
- Agent categorization (HR, finance, legal, marketing, research, etc.)
- Agent capabilities declaration (what tools it can use, what APIs it can call)
- Proper admin-only access for creating/managing agents

## Acceptance Criteria

- All platform agents are registered in the agents table
- Each agent has a clear name, description, system prompt, and tools config
- Founders can browse agents and add them to their team
- Agent is added as a `startup_member` with agent_id set
- Removing an agent from the team removes the member record

## Pending / Future

- Agent categories and filtering
- Agent ratings/reviews from startups that used them
- Third-party agent creation (marketplace agents built by external developers)
- Agent versioning (update an agent without breaking existing teams)
- Agent usage analytics
