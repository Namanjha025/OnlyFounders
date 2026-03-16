# OnlyFounders — Product Features

7 product features, 59 API endpoints. Features 1–5 are fully functional. Features 6–7 are scaffolded (endpoints exist, no AI logic yet).

---

## 1. Authentication

*Sign up, log in, know who I am.*

| Method | Endpoint | What it does |
|--------|----------|--------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Log in, get token |
| GET | `/api/v1/auth/me` | Get my profile |

**Status:** Fully built. JWT-based stateless auth.

---

## 2. Startup Onboarding

*Set up my startup profile — company info, founder profile, product, traction, financials, funding history, cap table, and track completeness.*

| Method | Endpoint | What it does |
|--------|----------|--------------|
| POST | `/api/v1/startups` | Create a startup |
| GET | `/api/v1/startups/mine` | List my startups |
| GET | `/api/v1/startups/{id}` | View startup details |
| PUT | `/api/v1/startups/{id}` | Update startup info |
| GET | `/api/v1/founder-profile/me` | Get my founder profile |
| PUT | `/api/v1/founder-profile/me` | Update my founder profile |
| GET | `/api/v1/founder-profile/{user_id}` | View someone's founder profile |
| GET | `/api/v1/startups/{id}/product` | Get product details |
| PUT | `/api/v1/startups/{id}/product` | Create/update product details |
| GET | `/api/v1/startups/{id}/traction` | Get traction metrics |
| PUT | `/api/v1/startups/{id}/traction` | Create/update traction metrics |
| GET | `/api/v1/startups/{id}/financial` | Get financial details |
| PUT | `/api/v1/startups/{id}/financial` | Create/update financial details |
| GET | `/api/v1/startups/{id}/funding-rounds` | List funding rounds |
| POST | `/api/v1/startups/{id}/funding-rounds` | Create funding round |
| GET | `/api/v1/startups/{id}/funding-rounds/{rid}` | View funding round |
| PUT | `/api/v1/startups/{id}/funding-rounds/{rid}` | Update funding round |
| DELETE | `/api/v1/startups/{id}/funding-rounds/{rid}` | Delete funding round |
| GET | `/api/v1/startups/{id}/equity` | List cap table |
| POST | `/api/v1/startups/{id}/equity` | Add shareholder |
| GET | `/api/v1/startups/{id}/equity/{sid}` | View shareholder |
| PUT | `/api/v1/startups/{id}/equity/{sid}` | Update shareholder |
| DELETE | `/api/v1/startups/{id}/equity/{sid}` | Delete shareholder |
| GET | `/api/v1/startups/{id}/onboarding` | Onboarding completeness % per section |

**Status:** Fully built. This is the core intake flow — 24 endpoints spanning company info, founder profile, product, traction, financials, funding rounds, cap table, and onboarding progress.

---

## 3. Team Management

*Build my startup team — add people, assign roles, manage contracts and documents per member.*

| Method | Endpoint | What it does |
|--------|----------|--------------|
| GET | `/api/v1/startups/{id}/members` | List team members |
| POST | `/api/v1/startups/{id}/members` | Add a team member |
| GET | `/api/v1/startups/{id}/members/{mid}` | View member details |
| PUT | `/api/v1/startups/{id}/members/{mid}` | Update role/title/equity |
| DELETE | `/api/v1/startups/{id}/members/{mid}` | Remove member |
| GET | `/api/v1/startups/{id}/member-documents` | List member documents |
| POST | `/api/v1/startups/{id}/member-documents/upload-url` | Get S3 upload link for member doc |
| POST | `/api/v1/startups/{id}/member-documents/confirm-upload` | Confirm member doc upload |
| POST | `/api/v1/startups/{id}/member-documents/download-url` | Get download link for member doc |
| DELETE | `/api/v1/startups/{id}/member-documents/{mdid}` | Delete member document |

**Status:** Fully built. Supports human and agent team members. Member docs include offer letters, contracts, NDAs, tax forms.

---

## 4. Document Management

*Upload and manage startup-level documents — pitch decks, incorporation docs, financials.*

| Method | Endpoint | What it does |
|--------|----------|--------------|
| GET | `/api/v1/startups/{id}/documents` | List documents |
| POST | `/api/v1/startups/{id}/documents/upload-url` | Get S3 presigned upload link |
| POST | `/api/v1/startups/{id}/documents/confirm-upload` | Confirm upload completed |
| POST | `/api/v1/startups/{id}/documents/download-url` | Get S3 presigned download link |
| DELETE | `/api/v1/startups/{id}/documents/{doc_id}` | Delete document |

**Status:** Fully built. S3-backed with presigned URLs. Categorized by type (pitch deck, incorporation, financial, etc.).

---

## 5. Task Management

*Create tasks, assign to team members, set deadlines, track progress. Calendar events for due dates, meetings, and milestones.*

| Method | Endpoint | What it does |
|--------|----------|--------------|
| GET | `/api/v1/startups/{id}/tasks` | List tasks (filterable by status, assignee) |
| POST | `/api/v1/startups/{id}/tasks` | Create task |
| GET | `/api/v1/startups/{id}/tasks/{tid}` | View task |
| PUT | `/api/v1/startups/{id}/tasks/{tid}` | Update status/assignee/priority |
| DELETE | `/api/v1/startups/{id}/tasks/{tid}` | Delete task |
| GET | `/api/v1/startups/{id}/calendar` | List calendar events |
| POST | `/api/v1/startups/{id}/calendar` | Create calendar event |
| DELETE | `/api/v1/startups/{id}/calendar/{eid}` | Delete calendar event |

**Status:** Fully built. Tasks have status flow (pending → in_progress → blocked → review → completed), priority levels, and deadlines.

---

## 6. Agent Marketplace

*Browse and discover AI agents. Add them to my startup team.*

| Method | Endpoint | What it does |
|--------|----------|--------------|
| GET | `/api/v1/agents` | Browse all agents |
| GET | `/api/v1/agents/{id}` | View agent profile |
| POST | `/api/v1/agents` | Create agent (admin only) |
| PUT | `/api/v1/agents/{id}` | Update agent |
| GET | `/api/v1/startups/{id}/agents` | List agents on my team |
| POST | `/api/v1/startups/{id}/agents` | Add agent to my team |
| DELETE | `/api/v1/startups/{id}/agents/{aid}` | Remove agent from team |

**Status:** Scaffolded. Endpoints work for CRUD and team assignment. No marketplace UI, search/filter, agent creator onboarding, or discovery features yet.

---

## 7. AI Chat (Manager + Agents)

*Talk to the Manager agent or any agent on my team.*

| Method | Endpoint | What it does |
|--------|----------|--------------|
| POST | `/api/v1/startups/{id}/chat/invoke` | Send message to Manager |
| GET | `/api/v1/startups/{id}/chat/messages` | Get Manager chat history |
| POST | `/api/v1/startups/{id}/agents/{aid}/chat/invoke` | Send message to an agent |
| GET | `/api/v1/startups/{id}/agents/{aid}/chat/messages` | Get agent chat history |

**Status:** Scaffolded. Endpoints exist and store messages, but responses are placeholder — no LangGraph orchestration or real AI logic behind them yet.
