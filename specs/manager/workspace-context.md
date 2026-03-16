# Workspace Context & Ingestion

**Module:** Manager
**Status:** Not Started

## Overview

Before the Manager can help, it needs to know everything about the startup. This spec covers how the Manager loads and stays aware of the full workspace context — startup profile, team, tasks, documents, financials, funding, cap table, and conversation history.

Every time the Manager is invoked, it should have up-to-date context on the workspace it's operating in.

## What the Manager Knows

The Manager ingests context from all workspace tables tied to the startup:

| Context | Source Table | What it tells the Manager |
|---------|-------------|--------------------------|
| Startup profile | `startups` | Name, stage, industry, location, team size |
| Founder profile | `founder_profiles` | Who the founder is, their background, skills |
| Team members | `startup_members` | Who's on the team, their roles, responsibilities, access levels |
| Product details | `product_details` | What they're building, target market, competitive advantage |
| Traction metrics | `traction_metrics` | Users, revenue, growth, north star metric |
| Financial details | `financial_details` | Burn rate, runway, cash, fundraising status |
| Funding rounds | `funding_rounds` | Past/current rounds, amounts, investors |
| Cap table | `equity_shareholders` | Ownership breakdown, vesting |
| Documents | `documents` | What docs exist (pitch deck, incorporation, etc.) |
| Tasks | `tasks` | Open tasks, who's assigned, deadlines, blockers |
| Calendar events | `calendar_events` | Upcoming deadlines, meetings, milestones |
| Invitations | `invitations` | Pending invites, who's been invited |
| Conversation history | `messages` | Past interactions with the Manager |

## How Context is Loaded

On every `/chat/invoke` call:

1. Fetch the startup record and all related data
2. Build a structured context object (JSON or formatted text)
3. Inject it into the Manager's system prompt as workspace context
4. Include recent conversation history for continuity
5. The Manager now has full awareness and can respond intelligently

## Context Format

The context should be structured so the LLM can easily reference it:

```
## Startup: {name}
Stage: {stage} | Industry: {industry} | Team size: {team_size}
Description: {short_description}

## Founder
Name: {first_name} {last_name}
Bio: {bio} | Skills: {skills}

## Team ({count} members)
- {name} — {role} ({title}): {responsibilities}
- {name} — {role} ({title}): {responsibilities}

## Product
Problem: {problem_statement}
Solution: {solution_description}
Stage: {product_stage} | Target: {target_market}

## Traction
Users: {total_users} | Revenue: ${monthly_revenue}/mo
North Star: {north_star_metric}

## Financials
Burn: ${burn_rate}/mo | Runway: {runway_months} months
Total raised: ${total_raised}

## Open Tasks ({count})
- [{priority}] {title} — assigned to {assignee}, due {due_date}

## Pending Invitations ({count})
- {invited_user} as {role} — {status}

## Recent Documents
- {doc_name} ({category}) — uploaded {date}
```

## Acceptance Criteria

- Manager has access to all workspace data on every invocation
- Context is up-to-date (fetched fresh, not cached stale)
- Context is structured and readable by the LLM
- Conversation history is included for continuity
- Large workspaces don't break the context window (summarize if needed)

## Pending / Future

- Context summarization for large workspaces (token limit management)
- Incremental context (only send what changed since last message)
- Context caching for performance
- Document content ingestion (not just metadata — actually read pitch decks, etc.)
