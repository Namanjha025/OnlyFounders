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
        "name": "Content Agent",
        "slug": "content",
        "description": "Creates blog posts, landing page copy, and product documentation for developer audiences.",
        "agent_type": "platform",
        "category": "Marketing",
        "icon": "PenTool",
        "color": "#a78bfa",
        "capabilities": ["Blog writing", "Landing page copy", "Product docs", "Email sequences"],
        "instructions": [
            "Writes content optimized for developer audiences with code examples",
            "Matches your brand voice and technical depth based on feedback",
            "Produces drafts with SEO-friendly structure and meta suggestions",
            "Iterates based on your review — typically 1-2 rounds to final",
        ],
        "connections": [{"name": "Google Docs"}, {"name": "Notion"}],
    },
    {
        "name": "SEO Agent",
        "slug": "seo",
        "description": "Audits your pages, fixes meta tags, researches keywords, and tracks search rankings.",
        "agent_type": "platform",
        "category": "Marketing",
        "icon": "Search",
        "color": "#34d399",
        "capabilities": ["Site audit", "Meta optimization", "Keyword research", "Rank tracking"],
        "instructions": [
            "Runs automated audits on all public pages for SEO issues",
            "Proposes meta description and title tag changes for approval",
            "Researches keywords by cluster and maps them to content opportunities",
            "Monitors ranking changes weekly and alerts on drops",
        ],
        "connections": [{"name": "Google Search Console"}, {"name": "Ahrefs"}],
    },
    {
        "name": "Social Agent",
        "slug": "social",
        "description": "Writes social copy, plans content calendars, schedules posts, and tracks engagement.",
        "agent_type": "platform",
        "category": "Marketing",
        "icon": "Share2",
        "color": "#f472b6",
        "capabilities": ["Social copy", "Content calendar", "Post scheduling", "Engagement tracking"],
        "instructions": [
            "Drafts platform-specific copy for Twitter/X, LinkedIn, and Instagram",
            "Plans weekly content calendars aligned with your launch milestones",
            "Suggests optimal posting times based on audience analytics",
            "Tracks engagement and recommends adjustments to strategy",
        ],
        "connections": [{"name": "Twitter/X"}, {"name": "LinkedIn"}, {"name": "Buffer"}],
    },
    {
        "name": "Registration Agent",
        "slug": "registration",
        "description": "Handles Pvt Ltd, LLP, OPC incorporation — SPICe+, MCA filings, and post-incorporation compliance.",
        "agent_type": "platform",
        "category": "Legal",
        "icon": "FileCheck",
        "color": "#60a5fa",
        "capabilities": ["Company registration", "MCA filings", "DSC/DIN", "Post-incorporation"],
        "instructions": [
            "Guides you through entity type selection (Pvt Ltd vs LLP vs OPC)",
            "Handles DSC, DIN, name reservation, and SPICe+ form prep",
            "Tracks MCA submission status and flags issues immediately",
            "Sets up post-incorporation tasks: bank account, PAN/TAN, first board meeting",
        ],
        "connections": [{"name": "MCA Portal"}],
    },
    {
        "name": "Compliance Agent",
        "slug": "compliance",
        "description": "Tracks statutory deadlines, ROC filings, AGM requirements, and regulatory compliance.",
        "agent_type": "platform",
        "category": "Legal",
        "icon": "Scale",
        "color": "#fbbf24",
        "capabilities": ["Deadline tracking", "ROC filings", "AGM prep", "Regulatory alerts"],
        "instructions": [
            "Maintains a compliance calendar with all statutory deadlines",
            "Sends reminders 7 days before each filing deadline",
            "Prepares filing checklists and document requirements",
            "Alerts on regulatory changes that affect your company type",
        ],
        "connections": [{"name": "Google Calendar"}],
    },
    {
        "name": "Funding Agent",
        "slug": "funding",
        "description": "Researches government schemes, grants, DPIIT benefits, and credit-linked programs.",
        "agent_type": "platform",
        "category": "Fundraising",
        "icon": "Landmark",
        "color": "#34d399",
        "capabilities": ["Scheme matching", "Eligibility check", "Application prep", "Grant tracking"],
        "instructions": [
            "Scans central and state schemes matching your sector, stage, and location",
            "Checks eligibility criteria against your startup profile automatically",
            "Prepares application documents and project notes for each scheme",
            "Tracks application status and follows up on pending decisions",
        ],
        "connections": [{"name": "Startup India Portal"}],
    },
    {
        "name": "Pitch Deck Agent",
        "slug": "pitch",
        "description": "Builds pitch decks, financial models, one-pagers, and prepares data rooms for investors.",
        "agent_type": "platform",
        "category": "Fundraising",
        "icon": "BarChart3",
        "color": "#f97316",
        "capabilities": ["Deck building", "Financial modeling", "Data room", "Investor prep"],
        "instructions": [
            "Creates pitch decks from your startup profile data — no blank slides",
            "Builds financial models with revenue, burn, and runway projections",
            "Runs investor-readiness checks for common objection points",
            "Organizes data room with cap table, incorporation, and financials",
        ],
        "connections": [{"name": "Google Slides"}, {"name": "Excel"}],
    },
    {
        "name": "Product Manager Agent",
        "slug": "pm",
        "description": "Helps with PRDs, roadmap planning, sprint management, and feature prioritization.",
        "agent_type": "platform",
        "category": "Product",
        "icon": "Bot",
        "color": "#818cf8",
        "capabilities": ["PRD writing", "Roadmap planning", "Sprint management", "Prioritization"],
        "instructions": [
            "Drafts PRDs from your feature ideas with user stories and acceptance criteria",
            "Maintains a prioritized roadmap based on impact and effort",
            "Breaks epics into sprint-sized tasks with clear ownership",
            "Runs weekly standups asynchronously — collects status from all agents",
        ],
        "connections": [{"name": "Linear"}, {"name": "Notion"}],
    },
]


WORKSPACE_DEFS = [
    {
        "name": "Marketing",
        "workspace_type": "ongoing",
        "case_status": "in_progress",
        "goal": "Launch product marketing for developer audience",
        "icon": "Megaphone",
        "agent_slugs": ["content", "seo", "social"],
    },
    {
        "name": "Legal & Registration",
        "workspace_type": "goal",
        "case_status": "in_progress",
        "goal": "Incorporate as Private Limited and complete initial compliance",
        "icon": "Scale",
        "agent_slugs": ["registration", "compliance"],
    },
    {
        "name": "Fundraising",
        "workspace_type": "goal",
        "case_status": "open",
        "goal": "Close pre-seed round — target $250K",
        "icon": "TrendingUp",
        "agent_slugs": ["funding", "pitch"],
    },
]

TEAM_DEFS = [
    {"slug": "content", "role": "Head of Content", "jd": "Creates all written content — blog posts, landing pages, docs, and email sequences. Focused on developer audiences with technical depth."},
    {"slug": "seo", "role": "SEO Specialist", "jd": "Audits pages, optimizes meta tags, researches keywords, and tracks search rankings to grow organic traffic."},
    {"slug": "social", "role": "Social Media Manager", "jd": "Plans content calendars, drafts social copy for Twitter/X and LinkedIn, schedules posts, and tracks engagement."},
    {"slug": "registration", "role": "Company Registration Lead", "jd": "Handles Pvt Ltd, LLP, OPC incorporation — SPICe+, MCA filings, DSC/DIN, and post-incorporation setup."},
    {"slug": "compliance", "role": "Compliance Officer", "jd": "Tracks all statutory deadlines, ROC filings, AGM requirements, and regulatory compliance for the company."},
    {"slug": "funding", "role": "Government Funding Researcher", "jd": "Researches and matches government schemes, grants, and credit-linked programs to the startup's profile."},
    {"slug": "pitch", "role": "Fundraising Strategist", "jd": "Builds pitch decks, financial models, one-pagers, and prepares data rooms for investor outreach."},
    {"slug": "pm", "role": "Product Manager", "jd": "Writes PRDs, plans roadmaps, runs sprint management, and handles feature prioritization across the product."},
]


def build_messages(ws_name, agent_map):
    """Return list of (agent_slug_or_none, role, content) tuples."""
    if ws_name == "Marketing":
        return [
            ("content", "assistant", "I've finished the blog draft for your product launch. Focused on the developer audience — included API code examples, integration walkthroughs, and a comparison table with alternatives.\n\nWord count: 1,840. Reading time: ~8 minutes."),
            (None, "user", "Can you make the intro more punchy? The first paragraph reads too generic."),
            ("content", "assistant", "Updated — the intro now opens with a developer pain point and a concrete stat. Here's v2:\n\n\"Every API integration starts the same way: reading docs for 2 hours, writing boilerplate for 3 more, and praying the auth flow works. We built something that cuts that to 15 minutes.\"\n\nRest of the draft is unchanged. Want me to push this version?"),
            ("seo", "activity", "SEO audit complete. Found 3 pages with missing or weak meta descriptions:\n\n• /pricing — was empty → \"Compare plans and start free\"\n• /docs — was generic → \"Developer docs: API reference, SDKs, and quickstart guides\"\n• /blog — outdated → \"Latest posts on API development and integrations\"\n\nAll 3 have been updated."),
            (None, "user", "Looks good — approve all the meta changes. @Social Agent can you start on the launch week social copy?"),
            ("social", "assistant", "On it. I'll draft a 5-post sequence for launch week:\n\n1. Teaser (Mon) — Problem statement hook\n2. Launch day (Wed) — Product reveal + link\n3. How it works (Thu) — 60-sec video script + caption\n4. Social proof (Fri) — Beta user quote thread\n5. Wrap-up (Sat) — Week 1 metrics + what's next\n\nI'll have drafts ready in ~2 hours. Which platforms — Twitter/X, LinkedIn, both?"),
        ]
    elif ws_name == "Legal & Registration":
        return [
            ("registration", "assistant", "I've started your Pvt Ltd incorporation. Here's where we stand:\n\nCompleted:\n✓ DSC obtained for both directors\n✓ Name reservation approved: \"OnlyFounders Technologies Pvt Ltd\"\n✓ DIN allocated\n\nIn progress:\n◐ SPICe+ form — 60% filled. I need the registered office address proof to continue.\n\nPending:\n☐ AGILE-PRO (GST/EPFO)\n☐ Bank account opening\n☐ First board meeting minutes"),
            (None, "user", "The registered office will be at our co-working space in HSR Layout, Bangalore. I have the NOC and utility bill."),
            ("registration", "assistant", "Perfect. Please upload the NOC and utility bill — I'll attach them to the SPICe+ form and proceed.\n\nFor a co-working space, the NOC needs to be on the space's letterhead with your company name mentioned. Does yours have that?"),
            ("compliance", "activity", "Compliance calendar created. I've set up statutory deadlines based on your expected incorporation date (April 2026):\n\n• INC-20A (Commencement) — within 180 days\n• First board meeting — within 30 days\n• Auditor appointment — within 30 days\n• ADT-1 filing — within 15 days of auditor appointment\n\nI'll send reminders as deadlines approach."),
        ]
    elif ws_name == "Fundraising":
        return [
            ("pitch", "assistant", "Your pitch deck v2 is ready. Key changes from v1:\n\n• Slide 3 — Added TAM/SAM/SOM breakdown with bottom-up calculation\n• Slide 7 — Updated traction slide with latest metrics\n• Slide 10 — Cleaner use-of-funds with milestone mapping\n\n12 slides, ~6 min presentation. Want me to run it through our investor-readiness check?"),
            ("funding", "activity", "Government funding scan complete. Based on your DPIIT status and sector, here are the top matches:\n\n1. Startup India Seed Fund — Up to ₹50L, equity/debt. You qualify.\n2. NIDHI PRAYAS — Up to ₹10L for prototyping. Relevant if hardware component.\n3. State startup policy (Karnataka) — Matching grant up to ₹50L.\n\nI've prepared application summaries for each. Which ones should I prioritize?"),
        ]
    return []


def build_tasks(ws_name, agent_map):
    """Return list of (title, agent_slug_or_none, assignee_name, is_done)."""
    if ws_name == "Marketing":
        return [
            ("Blog draft for product launch", "content", "Content Agent", False),
            ("SEO audit — fix meta descriptions", "seo", "SEO Agent", True),
            ("Launch week social copy (5 posts)", "social", "Social Agent", False),
            ("Landing page A/B test copy", "content", "Content Agent", False),
            ("Keyword research for docs pages", "seo", "SEO Agent", True),
            ("Set up social scheduling tool", "social", "Social Agent", False),
        ]
    elif ws_name == "Legal & Registration":
        return [
            ("Obtain DSC for directors", "registration", "Registration Agent", True),
            ("Name reservation (RUN)", "registration", "Registration Agent", True),
            ("Complete SPICe+ form", "registration", "Registration Agent", False),
            ("Upload registered office proof", None, "You", False),
            ("AGILE-PRO filing", "registration", "Registration Agent", False),
            ("Open bank account", None, "You", False),
            ("Set up compliance calendar", "compliance", "Compliance Agent", True),
            ("Draft first board meeting minutes", "compliance", "Compliance Agent", False),
        ]
    elif ws_name == "Fundraising":
        return [
            ("Pitch deck v2", "pitch", "Pitch Deck Agent", True),
            ("Financial model (18-month)", "pitch", "Pitch Deck Agent", True),
            ("Investor-readiness check", "pitch", "Pitch Deck Agent", False),
            ("Government scheme applications", "funding", "Funding Agent", False),
            ("Investor CRM setup", None, "You", False),
            ("Data room preparation", "pitch", "Pitch Deck Agent", False),
        ]
    return []


def build_notifications(ws_name, ws_id, agent_map):
    """Return list of notification dicts ready for the API."""
    notifs = []
    if ws_name == "Marketing":
        notifs = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("content"), "notification_type": "approval", "priority": "high", "title": "Review blog draft v2", "description": "Updated intro with developer pain point hook. 1,840 words.", "detail": "The blog draft has been rewritten with a developer-first intro. Opens with a pain point and includes 2 code examples, a comparison table, and a CTA to the docs.\n\nWord count: 1,840 · Reading time: ~8 min\n\nKey changes from v1:\n• New intro paragraph with concrete stat\n• Added code examples for auth flow\n• Comparison table: us vs. alternatives\n\nReady for your review before publishing.", "action_buttons": [{"label": "Approve", "variant": "primary"}, {"label": "Request Changes", "variant": "secondary"}]},
            {"workspace_id": ws_id, "agent_id": agent_map.get("seo"), "notification_type": "approval", "priority": "medium", "title": "Approve meta description updates", "description": "3 pages updated: /pricing, /docs, /blog", "detail": "SEO audit found 3 pages with missing or weak meta descriptions.\n\n/pricing — was empty → \"Compare plans and start building for free.\"\n/docs — was generic → \"Developer docs: API reference, SDKs, and quickstart guides.\"\n/blog — outdated → \"Latest posts on API development and developer tooling.\"\n\nAll changes follow best practices: 150-160 chars, include primary keyword.", "action_buttons": [{"label": "Approve All", "variant": "primary"}, {"label": "Review Individually", "variant": "secondary"}]},
            {"workspace_id": ws_id, "agent_id": agent_map.get("seo"), "notification_type": "report", "priority": "low", "title": "Keyword research completed", "description": "Identified 45 keywords across 3 clusters for docs pages.", "detail": "45 keywords identified across 3 clusters:\n• \"API integration\" cluster — 18 keywords, avg. volume 2.4K/mo\n• \"Developer tools\" cluster — 15 keywords, avg. volume 1.8K/mo\n• \"SDK setup\" cluster — 12 keywords, avg. volume 900/mo\n\nTop opportunities:\n1. \"api integration tutorial\" — 3.2K vol, low competition\n2. \"rest api authentication\" — 2.8K vol, medium competition\n3. \"sdk quickstart guide\" — 1.5K vol, low competition"},
        ]
    elif ws_name == "Legal & Registration":
        notifs = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("registration"), "notification_type": "approval", "priority": "high", "title": "Upload registered office proof", "description": "Need NOC + utility bill to proceed with SPICe+ filing.", "detail": "The SPICe+ form is 60% complete but I'm blocked on the registered office address proof. I need:\n\n1. NOC from the co-working space — on their letterhead with your company name mentioned.\n2. Utility bill — recent (within 2 months) for the co-working space address.\n\nOnce uploaded, I can complete the SPICe+ form and submit to MCA.", "action_buttons": [{"label": "Upload Files", "variant": "primary"}, {"label": "Ask Question", "variant": "secondary"}]},
            {"workspace_id": ws_id, "agent_id": agent_map.get("compliance"), "notification_type": "report", "priority": "low", "title": "Compliance calendar set up", "description": "All statutory deadlines configured based on expected incorporation date.", "detail": "Post-incorporation compliance calendar created:\n\n• INC-20A (Commencement of business) — within 180 days\n• First board meeting — within 30 days\n• Auditor appointment (ADT-1) — within 30 days\n• DIR-12 (Director appointment) — within 30 days\n• First annual filing (AOC-4 + MGT-7) — due by end of FY\n\nReminders set for 7 days before each deadline."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("registration"), "notification_type": "report", "priority": "low", "title": "DSC and DIN obtained successfully", "description": "Digital signatures and Director IDs are ready for both directors.", "detail": "Both director credentials are now ready:\n\nDirector 1 — DSC Class 3, valid until March 2028, DIN allocated.\nDirector 2 — DSC Class 3, valid until March 2028, DIN allocated.\n\nLinked to MCA account and ready for SPICe+ submission."},
        ]
    elif ws_name == "Fundraising":
        notifs = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("pitch"), "notification_type": "approval", "priority": "medium", "title": "Run investor-readiness check on deck v2", "description": "Deck is ready — run automated check for common investor objections.", "detail": "Pitch deck v2 is complete (12 slides). I can run an automated readiness check that evaluates:\n\n• Story arc and narrative clarity\n• TAM/SAM/SOM methodology\n• Traction slide credibility\n• Financial ask vs. milestones alignment\n\nThis takes about 2 minutes and produces a scorecard.", "action_buttons": [{"label": "Run Check", "variant": "primary"}, {"label": "Skip", "variant": "secondary"}]},
            {"workspace_id": ws_id, "agent_id": agent_map.get("funding"), "notification_type": "approval", "priority": "high", "title": "Select government schemes to apply for", "description": "3 schemes matched your profile — pick which ones to prioritize.", "detail": "Based on your DPIIT registration, sector, and stage:\n\n1. Startup India Seed Fund — Up to ₹50L. Strong match.\n2. NIDHI PRAYAS — Up to ₹10L for prototyping.\n3. Karnataka Startup Policy — Matching grant up to ₹50L.\n\nRecommendation: Prioritize #1 and #3.", "action_buttons": [{"label": "Prioritize Top 2", "variant": "primary"}, {"label": "View All Details", "variant": "secondary"}]},
            {"workspace_id": ws_id, "agent_id": agent_map.get("pitch"), "notification_type": "report", "priority": "low", "title": "Pitch deck v2 completed", "description": "12 slides ready with updated TAM, traction, and use-of-funds.", "detail": "Pitch deck v2 changes from v1:\n\n• Slide 3 — TAM/SAM/SOM bottom-up calculation\n• Slide 7 — Updated traction with latest MRR\n• Slide 10 — Use of funds mapped to milestones\n• Slide 12 — Cleaner ask slide\n\n12 slides, ~6 min presentation."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("pitch"), "notification_type": "report", "priority": "low", "title": "Financial model updated", "description": "18-month projections with burn rate and runway analysis.", "detail": "Financial model updated:\n\n• Monthly burn: ₹4.5L → ₹8L (post-hire)\n• Runway at current burn: 14 months\n• Revenue projections: ₹0 → ₹12L MRR by month 18\n• Break-even target: Month 22"},
        ]
    return notifs


def build_feed_events(ws_name, ws_id, agent_map):
    """Return list of feed event dicts."""
    events = []
    if ws_name == "Marketing":
        events = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("seo"), "event_type": "task_complete", "title": "SEO audit completed", "description": "Found and fixed 3 pages with missing meta descriptions."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("social"), "event_type": "task_started", "title": "Social Agent started launch week copy", "description": "Drafting 5-post sequence for Twitter/X and LinkedIn. ETA: 2 hours."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("content"), "event_type": "file_created", "title": "Blog draft v2 ready", "description": "Updated intro with developer pain point hook. 1,840 words, ~8 min read."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("seo"), "event_type": "task_complete", "title": "Keyword research completed", "description": "45 keywords across 3 clusters identified for documentation pages."},
        ]
    elif ws_name == "Legal & Registration":
        events = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("compliance"), "event_type": "task_complete", "title": "Compliance calendar configured", "description": "All statutory deadlines set up based on expected April 2026 incorporation."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("registration"), "event_type": "status_update", "title": "SPICe+ form 60% complete", "description": "DSC and DIN obtained. Name approved. Blocked on registered office proof."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("registration"), "event_type": "task_complete", "title": "DSC and DIN obtained", "description": "Digital signatures and Director IDs ready for both directors."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("registration"), "event_type": "task_complete", "title": "Name reservation approved", "description": "\"OnlyFounders Technologies Pvt Ltd\" approved by MCA."},
        ]
    elif ws_name == "Fundraising":
        events = [
            {"workspace_id": ws_id, "agent_id": agent_map.get("funding"), "event_type": "approval_request", "title": "Select government schemes to apply for", "description": "3 schemes matched your profile — pick which ones to prioritize."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("pitch"), "event_type": "approval_request", "title": "Investor-readiness check ready to run", "description": "Pitch deck v2 is done. Run automated check before sending to investors?"},
            {"workspace_id": ws_id, "agent_id": agent_map.get("pitch"), "event_type": "task_complete", "title": "Pitch deck v2 completed", "description": "12 slides with updated TAM, traction, and use-of-funds."},
            {"workspace_id": ws_id, "agent_id": agent_map.get("pitch"), "event_type": "file_created", "title": "Financial model updated", "description": "18-month projections with burn rate, runway, and revenue forecasts."},
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
