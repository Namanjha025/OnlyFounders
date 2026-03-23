# Workspaces

**Module:** Workspace
**Status:** In Progress

## Overview

A workspace is the primary unit of work on OnlyFounders. It's a project room where a founder and their agents (and optionally humans) collaborate toward a goal or an ongoing responsibility.

Workspaces can be **goal-based** (incorporate in Delaware — has an end state) or **ongoing** (Marketing — runs continuously like an employee). Agents are added to workspaces and work alongside the founder — proactively completing tasks, surfacing attention items, and organizing deliverables into dynamic sections.

## Core Concepts

### Workspace Types

| Type | Description | Example | End state |
|------|-------------|---------|-----------|
| **Goal-based** | Created to accomplish a specific objective | "Delaware Incorporation", "Seed Fundraise" | Completes when goal is done |
| **Ongoing** | Continuous workstream, like hiring an employee | "Marketing", "Finance & Compliance" | No end state — always active |

### What's Inside a Workspace

| Element | Description |
|---------|-------------|
| **Chat** | Primary interaction — talk to agents, see their activity, approve actions |
| **Inbox** | Attention items from agents — things needing your review/approval |
| **Tasks** | What's done and what's pending — created by agents or the founder |
| **Team** | Agents + humans in this workspace |
| **Brief** | Auto-maintained by agents — goal + current status summary |
| **Dynamic sections** | Folders/sections created by agents as they work (e.g., "Content Drafts", "SEO Reports") |

### Agents in Workspaces

Agents are the workers. They don't just respond to chat — they work proactively:

- Post results from autonomous work (completed tasks, generated files)
- Surface attention items when they need founder approval
- Create and organize dynamic sections as deliverables accumulate
- Create tasks for themselves and suggest tasks for the founder
- Maintain the workspace brief with current status

### Chat Stream

The workspace chat is three things interleaved:

1. **User messages** — founder talking to agents
2. **Agent responses** — agents replying to the founder
3. **Agent activity** — agents posting results from autonomous work

Agents are identified by name/avatar in the chat. The founder can @mention a specific agent or talk to the room.

### Inbox (Workspace-level)

Actionable items only. Things with an Accept/Reject/Review button:

- File edit proposals
- Task completion approvals
- Suggested actions
- Questions that block agent progress

When the founder acts on an inbox item, it resolves. The global Inbox page aggregates items across all workspaces.

## User Journey

### Creating a Workspace

1. Founder browses the Agents catalog
2. Enrolls in an agent (e.g., "Content Agent")
3. Workspace auto-creates (founder names it, e.g., "Marketing")
4. Agent greets and asks about goals
5. Agent starts working — creating tasks, organizing sections

OR

1. Founder creates a blank workspace with a name and goal
2. Adds agents from the catalog
3. Adds humans from the marketplace
4. Work begins

### Working in a Workspace

1. Founder opens workspace from sidebar
2. Sees chat on the left, context panel on the right
3. Chats with agents, reviews their activity
4. Checks inbox for items needing approval
5. Reviews tasks to see progress
6. Browses dynamic sections for organized deliverables

## UI Layout

Two-panel design (Tenderulkar-style):

```
┌──────────────────────────────────────────────────────────────┐
│  [Workspace Name]  · ongoing/75% complete    [Settings ⚙]   │
├──────────────────────────────────┬───────────────────────────┤
│                                  │  📌 Brief                 │
│  Chat / Activity Stream          │  Goal: Launch product...  │
│                                  │  Status: Blog v3 ready... │
│  Content Agent · 2h ago          │                           │
│  ┌────────────────────────┐      │  📥 Inbox (3)             │
│  │ New file: blog-v3.md   │      │  ├─ Review blog draft     │
│  │ [View] [Accept]        │      │  ├─ Approve meta tags     │
│  └────────────────────────┘      │  └─ Confirm social copy   │
│                                  │                           │
│  You · 3h ago                    │  ✅ Tasks (5/8)           │
│  Make it more technical           │  ├─ ✓ SEO audit          │
│                                  │  ├─ ☐ Blog draft          │
│  SEO Agent · automated · 45m     │  └─ ☐ Social copy         │
│  Fixed 3 meta descriptions       │                           │
│                                  │  👥 Team                  │
│                                  │  ├─ 🤖 Content Agent      │
│                                  │  ├─ 🤖 SEO Agent          │
│                                  │  └─ 👤 Sarah (advisor)    │
│                                  │                           │
│                                  │  ── Dynamic Sections ──   │
│                                  │  📄 Content Drafts (3)    │
│                                  │  📊 SEO Reports (2)       │
│                                  │  📋 Publishing Checklist  │
├──────────────────────────────────┴───────────────────────────┤
│  Message...                                    [@] [📎] [→]  │
└──────────────────────────────────────────────────────────────┘
```

## Navigation Structure

```
Sidebar:
  [OnlyFounders logo]

  Chat (Manager)          ← always-available orchestrator
  Inbox                   ← cross-workspace attention items

  My Workspaces
  ├─ Marketing
  ├─ Legal & Registration
  └─ Fundraising

  Explore
  ├─ Agents               ← pre-built agent catalog
  └─ Marketplace          ← people, orgs, communities

  Calendar

  [User profile]
```

## Acceptance Criteria

- Founder can create a workspace with a name and optional goal
- Agents can be added to a workspace
- Humans from the marketplace can be added to a workspace
- Chat stream shows user messages, agent responses, and agent activity
- Inbox shows actionable items from agents
- Tasks show done/pending with assignee
- Team shows all agents and humans in the workspace
- Brief is auto-maintained with goal and current status
- Dynamic sections are created by agents
- Goal-based workspaces show completion progress
- Ongoing workspaces show no end state
- Global Inbox aggregates items across all workspaces

## Pending / Future

- Workspace templates (pre-configured workspace + agent combos)
- Workspace archival for completed goal-based workspaces
- Workspace permissions (who can see/edit what)
- Agent-to-agent communication within a workspace
- Workspace analytics (activity, task completion rate)
- Cron/scheduled agent runs within workspaces
