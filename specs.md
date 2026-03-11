# OnlyFounders — Product Spec

## Vision

OnlyFounders is an **AI-native startup accelerator platform**. Everything a traditional accelerator does — mentorship, team building, incorporation, investor connections, task management, feedback loops — is orchestrated by AI agents with humans in the loop.

Founders interact with a single **Manager agent**. The Manager coordinates a team of specialized agents, each backed by real people or companies. The result: founders get the speed and availability of AI with the judgment and trust of humans.

## Origin

Inspired by the university accelerator model where:

- Founders get resources, mentorship, and connections
- Advisors give tasks, deadlines, and feedback
- Students/professionals apply to join startup teams
- Service providers help with incorporation, legal, finance, etc.

All of this can be managed by AI with human-in-the-loop — and that's what OnlyFounders builds.

---

## Core Concepts

### 1. The Manager

The Manager is a **platform-provided** agent assigned to every startup. It is the founder's single point of contact.

**Responsibilities:**

- Orchestrate all other agents on the startup's team
- Break down founder requests into tasks and assign to the right agents
- Track deadlines, surface blockers, send reminders
- Collect results from agents and present to the founder
- Escalate to the founder only when their input is needed

**How it works:**

- Founder tells the Manager what they need (e.g., "We need to incorporate in Delaware")
- Manager identifies the right agent (e.g., the platform incorporation agent)
- Manager assigns the task with context and deadline
- Manager tracks progress and reports back to the founder
- If an agent is blocked or needs founder input, Manager surfaces it

**Key principle:** The founder never has to manage individual agents. The Manager handles all orchestration.

---

### 2. Agents — Two Categories

#### Platform Agents (Built by OnlyFounders) - Tools



Spears - Naman(tech EIR). Sarah(Marketing - PPT etc..). Spears pays them. So internal members. 

OnlyFounders - ProductManager AI(tools, skills, mcp) + Human-in-the-loop. (Sid)

AIAdvisor(HITL)  - Bhavna

Platform agents are built, maintained, and quality-controlled by OnlyFounders. They are backed by vetted human experts.

**Characteristics:**

- Can take real actions using MCP tool integrations
- Examples: incorporation agent, legal review agent, financial modeling agent, pitch deck reviewer
- The AI handles the work; the human expert reviews before delivery
- Fully autonomous within their defined scope
- Quality and reliability guaranteed by the platform

**How they work when added to a team:**

- Assigned tasks by the Manager
- Execute work using their tools (e.g., file paperwork, draft documents, run analysis)
- Human expert behind them reviews output before it's delivered
- Results flow back through the Manager to the founder

**Example flow — Incorporation Agent:**

1. Manager assigns: "Incorporate this startup as a Delaware C-Corp"
2. Agent gathers required info from the startup's profile data
3. Agent uses MCP tools to prepare incorporation documents
4. Human lawyer reviews the documents
5. Agent delivers reviewed documents back through the Manager
6. Founder gets notified: "Your incorporation documents are ready for review"

#### Marketplace Agents (Created by External People/Companies)

Marketplace agents are **AI-powered profiles** — a person or company wraps themselves in an agent interface. The agent represents them; the human does the actual work.



10,100,1000 - Profiles. Portfolio. 

Intern - PM. (25) SMU students. - Marketplace. 

Investor - Indian investor (30) - Marketplace. 

Topmate! 

**Characteristics:**

- Created by external individuals, companies, students, mentors, investors
- The agent is the communication and coordination layer
- The human behind the agent is the one doing the actual work
- The agent makes the human scalable — handle multiple startups simultaneously
- The agent knows the creator's skills, experience, portfolio, availability

**Who creates marketplace agents:**


| Creator Type                | What Their Agent Does                                                                                                                  |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Students/Applicants**     | AI portfolio showcasing skills, available to join startup teams. Agent handles initial conversations, the student does the work.       |
| **Freelancers/Consultants** | Agent represents their services, manages client communication, tracks deliverables. Human does the consulting work.                    |
| **Companies**               | Agent represents the company's services (e.g., accounting firm). Handles intake, coordination. Company delivers the service.           |
| **Mentors/Advisors**        | Agent embodies the mentor's expertise. Provides initial guidance, schedules calls, tracks follow-ups. Mentor provides the deep advice. |
| **Investors/VCs**           | Representative agent that startups can pitch to. Agent handles screening, Q&A. Human investor reviews promising deals.                 |


**How they work when added to a team:**

- Get assigned a role and responsibilities
- Agent handles: context gathering, task tracking, status updates, initial responses, scheduling
- Human creator gets notified of work that needs their attention
- Agent helps the human manage multiple startups they're working with
- Think of it like hiring a freelancer whose availability and project management is handled by their agent 24/7

**Comparison:**


|                  | Platform Agents     | Marketplace Agents                 |
| ---------------- | ------------------- | ---------------------------------- |
| Created by       | OnlyFounders        | External people/companies          |
| Can take actions | Yes (MCP tools)     | No — human does the work           |
| Human role       | Expert reviewer     | The actual worker                  |
| Agent role       | Does the work       | Coordination + communication layer |
| Quality control  | Platform-controlled | Reviews/ratings (future)           |


---

### 3. Agent Marketplace

A directory where founders discover and browse agents by use case.

**Features:**

- Agent profiles with skills, description, type (platform vs marketplace), creator info
- Browse, search, and filter by category/skill/use case
- Talk to an agent directly before adding to team ("Can you help us with X?")
- Add agents to your startup team from the marketplace

**For agent creators:**

- Onboarding flow to create their agent profile
- Define skills, experience, portfolio, availability
- Set up how their agent communicates and what it knows
- Manage multiple startup clients through their agent's dashboard
- Pricing set by the creator (billing is future scope)

---

### 4. Startup Team

A startup's team is composed of agents (and the founder), coordinated by the Manager.

**How it works:**

- Founder creates a startup (via the intake flow)
- Manager is auto-assigned
- Founder browses marketplace or platform agents and adds them to the team
- Each agent gets assigned roles and responsibilities — what they should do, what they shouldn't
- Tasks are assigned with deadlines
- All agents share context through the startup's shared data

**Shared context:**

- Everything an agent does is connected to the startup's record
- All agents on a team can see relevant work done by other agents
- Stored in shared startup tables — profiles, documents, tasks, deliverables, conversations
- No siloed information; the whole team operates on the same context

**Roles and responsibilities:**

- When an agent joins, they're given a scope (e.g., "You handle all financial modeling tasks")
- Clear boundaries on what they can and can't do
- The Manager enforces these boundaries when delegating

---

### 5. Task & Communication Flow

```
Founder ←→ Manager ←→ Agents ←→ Humans (behind agents)
```

**The loop:**

1. Founder tells the Manager what they need
2. Manager breaks it down into tasks
3. Manager assigns tasks to the right agents with deadlines
4. Agents do the work (platform agents take action; marketplace agents coordinate with their humans)
5. Humans review/do the work as needed
6. Results flow back through the Manager
7. Manager presents results to the founder
8. If blockers arise that need the founder, Manager surfaces them with clear asks

**Task properties:**

- Assigned to a specific agent
- Has a deadline
- Has a status (pending, in progress, blocked, review, complete)
- Has context (linked to startup data, previous tasks, relevant documents)
- Can have blockers that get escalated

**Communication:**

- Founder ↔ Manager: Primary channel. The founder's only interface.
- Manager ↔ Agents: Task delegation, status checks, blocker resolution
- Agent ↔ Human (behind agent): Internal to the agent. How the human gets notified and delivers work.

---

## Design Principles

1. **Founder simplicity** — The founder only talks to the Manager. Everything else is abstracted.
2. **Human-backed trust** — Every agent has a human behind it. AI handles speed and availability; humans handle judgment.
3. **Shared context** — All work lives in shared startup tables. No information silos.
4. **Agents make humans scalable** — A mentor can advise 20 startups because their agent handles coordination. A consultant can manage 10 clients because their agent handles project management.
5. **Progressive automation** — Platform agents do work with human review. Marketplace agents coordinate while humans work. Over time, more autonomy as trust is established.
6. **Two-sided marketplace** — Founders find help; creators monetize expertise. The agent layer benefits both sides.

---

## Platform Components

### A. Startup Profile Intake — BUILT

Structured onboarding flow collecting founder profile, company details, team composition, product & market details, traction metrics, financials, funding history, and documents.

**Tech stack:** FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Alembic, JWT auth, S3 presigned URLs, Pydantic v2

**What's implemented:**

- 10 database tables (users, founder_profiles, startups, startup_members, product_details, traction_metrics, financial_details, funding_rounds, equity_shareholders, documents)
- 33 API endpoints across 11 routers
- Auth (register/login/JWT), CRUD for all entities
- Presigned S3 upload/download for documents
- Computed onboarding completeness per section
- Role-based access (owner vs member)

**Endpoints overview:**

- Auth: register, login, me
- Founder profile: get/update own, view others
- Startups: create (auto-slug), list mine, get, update
- Team members: full CRUD
- Product, Traction, Financials: get + upsert each
- Funding rounds, Equity/Cap table: full CRUD each
- Documents: list, presigned upload, confirm upload, presigned download, delete
- Onboarding: computed completeness score per section

### B. Agent Marketplace — NOT BUILT

- Agent profiles (skills, description, type, creator info, portfolio)
- Browse/search/filter
- Agent creator onboarding and management
- Direct conversation with agents before hiring

### C. Team Management — NOT BUILT

- Add/remove agents from a startup team
- Role and responsibility assignment
- Task creation and assignment with deadlines
- Shared context across team agents
- Status tracking and updates

### D. The Manager — NOT BUILT

- Platform-provided orchestrator agent per startup
- Task delegation and tracking
- Founder-facing communication interface
- Blocker detection and escalation
- Reminders and progress summaries

### E. Communication Layer — NOT BUILT

- Founder ↔ Manager messaging
- Manager ↔ Agent task delegation protocol
- Agent ↔ Human notification system
- Task status updates and notifications
- Conversation history tied to startup context

### F. Agent Creator Tools — NOT BUILT

- Agent builder for companies and individuals
- Skill/portfolio/availability configuration
- MCP tool integration (for platform agents)
- Human review interface
- Multi-client management dashboard for creators

---

## Prototype Scope (v1)

To be scoped. Likely order after startup intake:

1. Agent profiles and marketplace (browsing/discovery)
2. Basic team management (add agents to startup)
3. Task assignment and tracking
4. Manager agent (orchestration)
5. Communication layer
6. Agent creator tools

