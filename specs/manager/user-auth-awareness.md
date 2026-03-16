# User Authentication & Role Awareness

**Module:** Manager
**Status:** Not Started

## Overview

The Manager needs to know WHO is talking to it. The founder has root access and can do anything. A team member (CTO, advisor, intern) should get a personalized experience based on their role and responsibilities in the workspace.

The Manager adapts its behavior, available actions, and information access based on the authenticated user's role.

## How It Works

Every `/chat/invoke` call already passes the authenticated user via JWT. The Manager uses this to:

1. **Identify the user** — who they are (name, email, user ID)
2. **Look up their role** — find their `startup_member` record for this workspace
3. **Load their permissions** — what they can see and do based on role + responsibilities
4. **Adapt behavior** — personalize responses, restrict/allow actions accordingly

## Role-Based Behavior

| User | What the Manager does for them |
|------|-------------------------------|
| **Founder (root)** | Full access. Can ask the Manager to do anything — update startup profile, send invites, create tasks, assign team members, view all financials, manage cap table. The Manager proactively helps with strategy, accountability, and next steps. |
| **CTO / Technical lead** | Sees product/technical context. Can manage tasks in their domain. Manager helps with technical decisions, hiring engineers, product roadmap. Cannot see sensitive financials unless granted access. |
| **Advisor** | Sees startup progress, traction, product. Manager gives them updates, surfaces areas where their advice is needed. Cannot take administrative actions. |
| **Employee / Intern** | Sees their assigned tasks and relevant context. Manager helps them understand what to do, provides guidance on their work. Limited visibility into financials, cap table. |

## System Prompt Injection

When the Manager is invoked, the system prompt includes:

```
You are the AI Manager for {startup_name}.

The person you're talking to is:
- Name: {user_name}
- Role: {role} ({title})
- Responsibilities: {responsibilities}
- Access level: {access_level}

As {role}, they can:
- {list of allowed actions}

They should NOT have access to:
- {list of restricted areas}

Adapt your responses accordingly. Be helpful within their scope.
If they ask for something outside their permissions, explain that the founder needs to grant access.
```

## Acceptance Criteria

- Manager knows who is talking to it on every invocation
- Manager adapts tone and available actions based on user's role
- Founder gets full access to all Manager capabilities
- Team members get role-appropriate responses and action access
- Restricted information is not leaked to unauthorized team members
- If a team member asks for something outside their scope, Manager explains the limitation

## Pending / Future

- Granular permission matrix (beyond role — custom permissions per member)
- Founder can configure what each role can see/do via the Manager
- Audit log of Manager actions per user
- Team member can request elevated access through the Manager
