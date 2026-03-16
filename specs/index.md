# OnlyFounders — Specs Index

## Modules

| Module | Description | Link |
|--------|-------------|------|
| Auth | User signup & signin | [View](auth/README.md) |
| Workspace | Startup workspace — team, tasks, docs, AI agents | [View](workspace/README.md) |
| Manager | AI Manager — workspace context, role awareness, actions | [View](manager/README.md) |
| Inbox | Human-in-the-loop agent communication channel | [View](inbox/README.md) |
| Marketplace | TwinVerse — AI Twin marketplace for discovery and connection | [View](marketplace/README.md) |
| Agents | AI employees — registry, workspace isolation, memory | [View](agents/README.md) |

## All Specs

| # | Spec | Module | Status | Description | Link |
|---|------|--------|--------|-------------|------|
| 1 | User Signup & Signin | Auth | Built | Simple registration and login with JWT | [View](auth/user-signup-signin.md) |
| 2 | Register Startup | Workspace | Backend built | Create workspace with just a name, AI onboarding pending | [View](workspace/register-startup.md) |
| 3 | Team Invitations | Workspace | In Progress | Invite platform users to join startup team | [View](workspace/team-invitations.md) |
| 4 | Task Management | Workspace | Backend built | Task board with assignment, priorities, deadlines, calendar | [View](workspace/task-management.md) |
| 5 | Document Management | Workspace | Backend built | S3-backed document upload/download for startup and member docs | [View](workspace/document-management.md) |
| 6 | Workspace Context & Ingestion | Manager | Not Started | Manager loads full startup context on every invocation | [View](manager/workspace-context.md) |
| 7 | User Auth & Role Awareness | Manager | Not Started | Manager adapts behavior based on who's talking to it | [View](manager/user-auth-awareness.md) |
| 8 | Workspace Actions | Manager | Not Started | Manager performs workspace CRUD via tool calling | [View](manager/workspace-actions.md) |
| 9 | Inbox System | Inbox | Not Started | Agents pause execution and send approvals, blockers, reports to user inbox | [View](inbox/inbox-system.md) |
| 10 | Twin Registration | Marketplace | Not Started | Create an AI Twin with role, bio, services, portfolio, Calendly | [View](marketplace/twin-registration.md) |
| 11 | Marketplace Discovery | Marketplace | Not Started | Browse, search, filter Twins by category and services | [View](marketplace/marketplace-discovery.md) |
| 12 | Twin Chat | Marketplace | Not Started | Chat with any Twin — sandboxed AI receptionist | [View](marketplace/twin-chat.md) |
| 13 | Agent Registry | Agents | Scaffolded | Catalog of AI agents with name, tools, system prompt | [View](agents/agent-registry.md) |
| 14 | Agent Workspace Isolation | Agents | Not Started | Scoped tasks, isolated memory/thread/calendar per agent | [View](agents/agent-workspace-isolation.md) |
