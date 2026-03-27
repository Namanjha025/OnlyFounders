"""Seed agents, workspaces, messages, tasks, notifications, and feed events.

Uses the first founder account (marcus.chen@demo.com) from seed_profiles.py.
Requires the backend to be running and seed_profiles.py to have been run first.

Usage:
    python3 scripts/seed_workspaces.py
"""
import asyncio
import httpx

BASE = "http://localhost:8000/api/v1"
FOUNDER_EMAIL = "marcus.chen@demo.com"
FOUNDER_PASSWORD = "Demo1234!"

AGENTS = [
    {
        "name": "Manager",
        "slug": "manager",
        "description": "Your personal startup concierge. Understands what you need, finds the right specialist agent, creates cases, and tracks the big picture.",
        "agent_type": "platform",
        "category": "Management",
        "icon": "Sparkles",
        "color": "#818cf8",
        "capabilities": [
            "Find specialist agents",
            "Create cases",
            "Assign agents to cases",
            "Track progress",
            "Orchestrate workflows",
        ],
        "instructions": [
            "Tell the Manager what you need — it will find the right specialist",
            "The Manager creates cases and assigns agents automatically",
            "It tracks progress across all your cases",
            "It never does domain work itself — it delegates to specialists",
        ],
        "connections": [],
    },
    {
        "name": "Legal Agent",
        "slug": "legal",
        "description": "Drafts NDAs, privacy policies, terms of service, founder agreements, and other legal documents for startups.",
        "agent_type": "platform",
        "category": "Legal",
        "icon": "Scale",
        "color": "#60a5fa",
        "capabilities": [
            "NDA drafting",
            "Privacy policy",
            "Terms of service",
            "Founder agreements",
            "Consulting agreements",
            "Offer letters",
        ],
        "instructions": [
            "Asks clarifying questions before drafting any document",
            "Drafts in clean, readable format with proper legal structure",
            "Explains key clauses in plain language",
            "Creates tasks for next steps (review, sign, file)",
            "Always includes a disclaimer to consult a licensed attorney",
        ],
        "connections": [],
    },
    {
        "name": "Grant Finder",
        "slug": "grant-finder",
        "description": "Finds government grants, startup schemes, cloud credits, and funding programs matching your startup profile. Helps you apply.",
        "agent_type": "platform",
        "category": "Fundraising",
        "icon": "Landmark",
        "color": "#34d399",
        "capabilities": [
            "Startup India schemes",
            "DPIIT recognition",
            "State grants",
            "Cloud credits (AWS/GCP/Azure)",
            "Sector-specific grants",
            "Application planning",
        ],
        "instructions": [
            "Starts by understanding your startup: sector, stage, location, entity type",
            "Searches a curated database of 10+ grant programs",
            "Presents matching programs with eligibility details and amounts",
            "Creates step-by-step application plans with tasks",
            "Prioritizes by relevance, amount, and ease of application",
        ],
        "connections": [{"name": "Startup India Portal"}, {"name": "DPIIT"}],
    },
]


WORKSPACE_DEFS = [
    {
        "name": "NDA for Co-founder",
        "workspace_type": "goal",
        "case_status": "in_progress",
        "goal": "Draft a mutual NDA between co-founders before equity discussion",
        "icon": "Scale",
        "agent_slugs": ["legal"],
    },
    {
        "name": "Govt Grant Applications",
        "workspace_type": "goal",
        "case_status": "open",
        "goal": "Find and apply for government grants matching our startup profile",
        "icon": "Landmark",
        "agent_slugs": ["grant-finder"],
    },
]

TEAM_DEFS = [
    {"slug": "legal", "role": "Legal Specialist", "jd": "Drafts NDAs, privacy policies, terms of service, and other legal documents for the startup."},
    {"slug": "grant-finder", "role": "Grant Researcher", "jd": "Finds and helps apply for government grants, startup schemes, and cloud credits."},
]


def build_messages(ws_name, agent_map):
    """Return list of (agent_slug_or_none, role, content) tuples."""
    if ws_name == "NDA for Co-founder":
        return [
            (None, "user", "I need to draft a mutual NDA between me and my potential co-founder before we discuss equity splits."),
            ("legal", "assistant", "I can help you draft a mutual NDA. Let me ask a few questions first:\n\n1. **Parties**: What are the full legal names of both parties?\n2. **Jurisdiction**: Which jurisdiction should govern this agreement? (e.g., India, US-Delaware)\n3. **Duration**: How long should the confidentiality obligations last? (Standard is 2-3 years)\n4. **Scope**: Any specific information you want explicitly covered or excluded?\n\nOnce I have these details, I'll draft a clean mutual NDA for your review."),
            (None, "user", "Both are Indian residents. Jurisdiction India. Duration 2 years. Standard scope — we'll be discussing equity, product roadmap, and financials."),
            ("legal", "assistant", "Got it. I'll draft a mutual NDA with:\n- Indian jurisdiction (governed by Indian Contract Act)\n- 2-year confidentiality period\n- Covers equity discussions, product roadmap, and financial information\n- Standard exceptions: publicly available info, independently developed info, required by law\n\nI'll have the draft ready shortly. I'll also create a task for you to review and sign it."),
        ]
    elif ws_name == "Govt Grant Applications":
        return [
            (None, "user", "We're a tech startup in Bangalore building an AI platform. We're pre-revenue, incorporated as Pvt Ltd. What grants can we apply for?"),
            ("grant-finder", "assistant", "Great, let me find the best matching programs for you. Based on what you've shared:\n\n- **Sector**: Tech / AI\n- **Stage**: Pre-revenue (early)\n- **Location**: Karnataka (Bangalore)\n- **Entity**: Pvt Ltd\n\nLet me search our database for matching programs. I'll also check if you have DPIIT recognition — that opens up several additional schemes.\n\nDo you have DPIIT Startup Recognition? And is your company less than 2 years old?"),
        ]
    return []


def build_tasks(ws_name, agent_map):
    """Return list of (title, agent_slug_or_none, assignee_name, is_done)."""
    if ws_name == "NDA for Co-founder":
        return [
            ("Draft mutual NDA", "legal", "Legal Agent", False),
            ("Review NDA with co-founder", None, "You", False),
            ("Both parties sign NDA", None, "You", False),
        ]
    elif ws_name == "Govt Grant Applications":
        return [
            ("Complete startup profile for grant matching", None, "You", False),
            ("Get DPIIT Startup Recognition", "grant-finder", "Grant Finder", False),
            ("Research matching grant programs", "grant-finder", "Grant Finder", False),
        ]
    return []


def build_notifications(ws_name, ws_id, agent_map):
    """Return list of notification dicts ready for the API."""
    notifs = []
    if ws_name == "NDA for Co-founder":
        notifs = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("legal"), "notification_type": "report", "priority": "medium", "title": "NDA drafting in progress", "description": "Gathering details for mutual NDA between co-founders.", "detail": "I'm drafting a mutual NDA for your co-founder discussion. Key parameters:\n\n• Jurisdiction: India\n• Duration: 2 years\n• Scope: Equity, product roadmap, financials\n\nI'll have a draft ready for review shortly."},
        ]
    elif ws_name == "Govt Grant Applications":
        notifs = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("grant-finder"), "notification_type": "report", "priority": "medium", "title": "Grant research started", "description": "Analyzing your startup profile to find matching programs.", "detail": "I'm searching our database of 10+ government grant programs and cloud credit schemes matching your profile:\n\n• Tech / AI sector\n• Pre-revenue stage\n• Karnataka (Bangalore)\n• Pvt Ltd\n\nI'll present the best matches with eligibility details shortly."},
        ]
    return notifs


def build_feed_events(ws_name, ws_id, agent_map):
    """Return list of feed event dicts."""
    events = []
    if ws_name == "NDA for Co-founder":
        events = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("legal"), "event_type": "task_started", "title": "NDA drafting started", "description": "Legal Agent is drafting a mutual NDA for co-founder discussions."},
        ]
    elif ws_name == "Govt Grant Applications":
        events = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("grant-finder"), "event_type": "task_started", "title": "Grant research initiated", "description": "Grant Finder is analyzing your startup profile to find matching government schemes and programs."},
        ]
    return events


async def seed():
    async with httpx.AsyncClient(base_url=BASE, timeout=30) as client:
        # Login
        print("Logging in as founder...")
        res = await client.post("/auth/login", json={"email": FOUNDER_EMAIL, "password": FOUNDER_PASSWORD})
        if res.status_code != 200:
            print(f"Login failed: {res.text}")
            print("Make sure seed_profiles.py has been run first!")
            return
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"  Logged in as {FOUNDER_EMAIL}")

        # Create agents
        print("\nCreating agents...")
        agent_id_map = {}  # slug -> uuid
        for agent_data in AGENTS:
            slug = agent_data["slug"]
            res = await client.post("/agents/", json=agent_data, headers=headers)
            if res.status_code == 201:
                agent_id_map[slug] = res.json()["id"]
                print(f"  Created: {agent_data['name']}")
            elif res.status_code == 400 and "slug already exists" in res.text.lower():
                # fetch existing
                res2 = await client.get("/agents/", headers=headers)
                for a in res2.json():
                    if a["slug"] == slug:
                        agent_id_map[slug] = a["id"]
                        # update with new fields
                        await client.put(f"/agents/{a['id']}", json={
                            "category": agent_data.get("category"),
                            "icon": agent_data.get("icon"),
                            "color": agent_data.get("color"),
                            "capabilities": agent_data.get("capabilities"),
                            "instructions": agent_data.get("instructions"),
                            "connections": agent_data.get("connections"),
                        }, headers=headers)
                        print(f"  Updated: {agent_data['name']} (already existed)")
                        break
            else:
                print(f"  ERROR creating {slug}: {res.text}")

        # Hire agents to team
        print("\nHiring agents to team...")
        for td in TEAM_DEFS:
            agent_id = agent_id_map.get(td["slug"])
            if not agent_id:
                print(f"  SKIP: {td['slug']} (agent not found)")
                continue
            res = await client.post("/team/", json={
                "agent_id": agent_id,
                "role": td["role"],
                "job_description": td["jd"],
            }, headers=headers)
            if res.status_code == 201:
                print(f"  Hired: {td['slug']} as {td['role']}")
            elif res.status_code == 409:
                print(f"  Already hired: {td['slug']}")
            else:
                print(f"  ERROR hiring {td['slug']}: {res.text}")

        # Create workspaces (cases)
        print("\nCreating cases...")
        for ws_def in WORKSPACE_DEFS:
            ws_name = ws_def["name"]
            res = await client.post("/workspaces/", json={
                "name": ws_name,
                "workspace_type": ws_def["workspace_type"],
                "case_status": ws_def.get("case_status", "open"),
                "goal": ws_def["goal"],
                "icon": ws_def["icon"],
            }, headers=headers)
            if res.status_code != 201:
                print(f"  ERROR creating workspace {ws_name}: {res.text}")
                continue

            ws = res.json()
            ws_id = ws["id"]
            print(f"  Created workspace: {ws_name} ({ws_id})")

            # Add agents to workspace
            for slug in ws_def["agent_slugs"]:
                agent_id = agent_id_map.get(slug)
                if agent_id:
                    r = await client.post(f"/workspaces/{ws_id}/agents/{agent_id}", headers=headers)
                    if r.status_code == 201:
                        print(f"    Added agent: {slug}")
                    else:
                        print(f"    ERROR adding {slug}: {r.text}")

            # Update workspace brief/status after creation
            brief_map = {
                "Marketing": "Blog draft v3 is ready for review. SEO audit completed — 3 meta descriptions fixed. Social copy for launch week is pending.",
                "Legal & Registration": "DSC obtained. Name reservation approved. SPICe+ form 60% complete — waiting on registered office proof.",
                "Fundraising": "Pitch deck v2 ready. Financial model updated with 18-month projections. Government scheme applications shortlisted.",
            }
            status_map = {
                "Marketing": "Blog draft ready for review",
                "Legal & Registration": "SPICe+ filing in progress",
                "Fundraising": "Investor outreach starting",
            }
            progress_map = {
                "Legal & Registration": 62,
                "Fundraising": 40,
            }
            update_data = {
                "brief": brief_map.get(ws_name),
                "status_text": status_map.get(ws_name),
            }
            if ws_name in progress_map:
                update_data["progress"] = progress_map[ws_name]
            await client.put(f"/workspaces/{ws_id}", json=update_data, headers=headers)

            # Create messages
            msgs = build_messages(ws_name, agent_id_map)
            for agent_slug, role, content in msgs:
                agent_id = agent_id_map.get(agent_slug) if agent_slug else None
                msg_data = {"content": content, "role": role}
                if agent_id:
                    msg_data["agent_id"] = agent_id
                await client.post(f"/workspaces/{ws_id}/messages", json=msg_data, headers=headers)
            print(f"    Messages: {len(msgs)} created")

            # Create tasks
            tasks = build_tasks(ws_name, agent_id_map)
            for title, agent_slug, assignee_name, is_done in tasks:
                agent_id = agent_id_map.get(agent_slug) if agent_slug else None
                task_data = {"title": title, "assignee_name": assignee_name}
                if agent_id:
                    task_data["agent_id"] = agent_id
                r = await client.post(f"/workspaces/{ws_id}/tasks", json=task_data, headers=headers)
                if r.status_code == 201 and is_done:
                    task_id = r.json()["id"]
                    await client.put(f"/workspaces/{ws_id}/tasks/{task_id}", json={"is_done": True}, headers=headers)
            print(f"    Tasks: {len(tasks)} created")

            # Create notifications
            notifs = build_notifications(ws_name, ws_id, agent_id_map)
            for notif_data in notifs:
                r = await client.post("/notifications/", json=notif_data, headers=headers)
                if r.status_code != 201:
                    print(f"    ERROR notification: {r.text}")
            print(f"    Notifications: {len(notifs)} created")

            # Create feed events
            events = build_feed_events(ws_name, ws_id, agent_id_map)
            for event_data in events:
                r = await client.post("/feed/", json=event_data, headers=headers)
                if r.status_code != 201:
                    print(f"    ERROR feed event: {r.text}")
            print(f"    Feed events: {len(events)} created")

        print("\n✅ Seeding complete!")
        print(f"Login with: {FOUNDER_EMAIL} / {FOUNDER_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
