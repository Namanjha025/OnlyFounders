"""Seed 15 marketplace profiles via the signup + onboarding flow.

Each user: register → start onboarding → complete 4 steps → publish.
Mirrors exactly what a real user does on the /login page.

Usage:
    python3 scripts/seed_profiles.py
"""
import asyncio
import httpx

BASE = "http://localhost:8000/api/v1"

USERS = [
    # ── PROFESSIONALS (5) ──────────────────────────────────────────

    {
        "register": {"email": "alex.rivera@demo.com", "password": "Demo1234!", "first_name": "Alex", "last_name": "Rivera"},
        "type": "professional",
        "steps": {
            1: {"headline": "Full-Stack Developer | React + Python", "bio": "10 years building SaaS products. Ex-Google, ex-Stripe. I specialize in taking MVPs from 0→1 with clean architecture and fast iteration.", "location": "San Francisco, CA"},
            2: {"skills": "react,python,fastapi,typescript,postgresql,aws,docker", "primary_role": "Full-Stack Developer", "years_experience": "10"},
            3: {"service_offerings": "MVP Development,Technical Architecture,Code Review,CTO-as-a-Service", "hourly_rate": "175", "availability_status": "open_to_offers"},
            4: {"linkedin_url": "https://linkedin.com/in/alexrivera", "website_url": "https://alexrivera.dev", "portfolio_url": "https://alexrivera.dev/portfolio", "cal_booking_link": "https://cal.com/alexrivera"},
        },
    },
    {
        "register": {"email": "sarah.kim@demo.com", "password": "Demo1234!", "first_name": "Sarah", "last_name": "Kim"},
        "type": "professional",
        "steps": {
            1: {"headline": "Product Designer | B2B SaaS & Fintech", "bio": "Led design at 3 YC startups. I turn complex workflows into clean interfaces. Obsessed with design systems and user research.", "location": "New York, NY"},
            2: {"skills": "figma,design-systems,user-research,prototyping,ux-writing,accessibility", "primary_role": "Product Designer", "years_experience": "7"},
            3: {"service_offerings": "UI/UX Design,Design System Setup,User Research,Prototype Testing", "hourly_rate": "140", "availability_status": "available"},
            4: {"linkedin_url": "https://linkedin.com/in/sarahkim-design", "website_url": "https://sarahkim.design", "portfolio_url": "https://dribbble.com/sarahkim", "cal_booking_link": "https://cal.com/sarahkim"},
        },
    },
    {
        "register": {"email": "raj.patel@demo.com", "password": "Demo1234!", "first_name": "Raj", "last_name": "Patel"},
        "type": "professional",
        "steps": {
            1: {"headline": "DevOps & Cloud Architect | AWS Certified", "bio": "Former AWS Solutions Architect. I help startups set up scalable infrastructure from day one — CI/CD, monitoring, Kubernetes, and cost optimization.", "location": "Bangalore, India"},
            2: {"skills": "aws,kubernetes,terraform,docker,github-actions,monitoring,postgresql", "primary_role": "DevOps Engineer", "years_experience": "8"},
            3: {"service_offerings": "Cloud Architecture,CI/CD Pipeline Setup,Cost Optimization,Security Audit", "hourly_rate": "95", "availability_status": "available"},
            4: {"linkedin_url": "https://linkedin.com/in/rajpatel-cloud", "website_url": "https://rajpatel.dev"},
        },
    },
    {
        "register": {"email": "emma.chen@demo.com", "password": "Demo1234!", "first_name": "Emma", "last_name": "Chen"},
        "type": "professional",
        "steps": {
            1: {"headline": "Growth Marketer | PLG & B2B SaaS", "bio": "Scaled 2 startups from 0→$5M ARR. I build growth engines: content, SEO, paid acquisition, and product-led funnels. Data-driven, not gut-driven.", "location": "Austin, TX"},
            2: {"skills": "growth-marketing,seo,content-strategy,google-ads,analytics,ab-testing,hubspot", "primary_role": "Growth Marketer", "years_experience": "6"},
            3: {"service_offerings": "Growth Strategy,SEO Audit,Paid Acquisition Setup,Content Playbook", "hourly_rate": "120", "availability_status": "open_to_offers"},
            4: {"linkedin_url": "https://linkedin.com/in/emmachen-growth", "website_url": "https://emmachen.co", "cal_booking_link": "https://cal.com/emmachen"},
        },
    },
    {
        "register": {"email": "david.okonkwo@demo.com", "password": "Demo1234!", "first_name": "David", "last_name": "Okonkwo"},
        "type": "professional",
        "steps": {
            1: {"headline": "Data Scientist | ML & NLP Specialist", "bio": "PhD in Machine Learning from MIT. Built recommendation engines at Spotify and fraud detection systems at Stripe. Available for contract ML projects.", "location": "London, UK"},
            2: {"skills": "python,pytorch,nlp,recommendation-systems,sql,spark,mlops", "primary_role": "Data Scientist", "years_experience": "9"},
            3: {"service_offerings": "ML Model Development,Data Pipeline Design,NLP Solutions,MLOps Setup", "hourly_rate": "200", "availability_status": "busy"},
            4: {"linkedin_url": "https://linkedin.com/in/davidokonkwo-ml", "website_url": "https://davidokonkwo.com", "portfolio_url": "https://github.com/dokonkwo"},
        },
    },

    # ── ADVISORS (5) ───────────────────────────────────────────────

    {
        "register": {"email": "priya.sharma@demo.com", "password": "Demo1234!", "first_name": "Priya", "last_name": "Sharma"},
        "type": "advisor",
        "steps": {
            1: {"headline": "Angel Investor & Fintech Advisor | 40+ Portfolio", "bio": "Former VP at Goldman Sachs turned angel investor. I back pre-seed and seed stage fintech startups. $25K-$100K checks with active GTM support.", "location": "New York, NY"},
            2: {"skills": "fundraising,fintech,go-to-market,strategy,banking,payments", "domain_expertise": "fintech,payments,embedded-finance,lending,neobanking", "investment_thesis": "Early-stage B2B fintech solving real pain points in payments infrastructure, lending automation, or compliance tooling. Must have technical founders."},
            3: {"investment_stages": "pre_seed,seed", "check_size_min": "25000", "check_size_max": "100000", "fee_structure": "equity"},
            4: {"availability": "5 hours/week", "cal_booking_link": "https://cal.com/priyasharma", "linkedin_url": "https://linkedin.com/in/priyasharma-investor"},
        },
    },
    {
        "register": {"email": "michael.torres@demo.com", "password": "Demo1234!", "first_name": "Michael", "last_name": "Torres"},
        "type": "advisor",
        "steps": {
            1: {"headline": "Startup Mentor | Ex-CTO, 3x Exits", "bio": "Built and sold 3 companies (2 acquihires, 1 acquisition by Salesforce). I help technical founders avoid the mistakes I made. Focus on engineering leadership and scaling teams.", "location": "Seattle, WA"},
            2: {"skills": "engineering-leadership,scaling,hiring,architecture,fundraising", "domain_expertise": "saas,enterprise,developer-tools,infrastructure", "investment_thesis": "I advise, don't invest. Looking for technical founders building developer tools or enterprise SaaS who need help with their first 10 engineering hires."},
            3: {"investment_stages": "seed,series_a", "fee_structure": "pro_bono"},
            4: {"availability": "3 hours/week", "cal_booking_link": "https://cal.com/michaeltorres", "linkedin_url": "https://linkedin.com/in/michaeltorres-cto", "website_url": "https://michaeltorres.io"},
        },
    },
    {
        "register": {"email": "aisha.johnson@demo.com", "password": "Demo1234!", "first_name": "Aisha", "last_name": "Johnson"},
        "type": "advisor",
        "steps": {
            1: {"headline": "VC Partner | Healthcare & Biotech | Series A-B", "bio": "Partner at Lux Capital. Led investments in 15+ healthcare/biotech companies including 3 unicorns. I help founders navigate FDA, clinical trials, and institutional fundraising.", "location": "Boston, MA"},
            2: {"skills": "healthcare,biotech,fundraising,fda-regulatory,clinical-trials,board-governance", "domain_expertise": "healthtech,biotech,medtech,digital-health,genomics", "investment_thesis": "Series A/B healthcare companies with strong clinical evidence and clear regulatory pathway. Prefer founders with domain expertise — ideally MD or PhD."},
            3: {"investment_stages": "series_a,series_b", "check_size_min": "500000", "check_size_max": "5000000", "fee_structure": "equity"},
            4: {"availability": "2 hours/week", "cal_booking_link": "https://cal.com/aishajohnson", "linkedin_url": "https://linkedin.com/in/aishajohnson-vc"},
        },
    },
    {
        "register": {"email": "hans.mueller@demo.com", "password": "Demo1234!", "first_name": "Hans", "last_name": "Mueller"},
        "type": "advisor",
        "steps": {
            1: {"headline": "Legal Advisor for Startups | Corporate & IP", "bio": "15 years in startup law. Helped 200+ companies incorporate, raise rounds, and protect IP. I offer fixed-fee packages for early-stage legal needs.", "location": "Berlin, Germany"},
            2: {"skills": "corporate-law,ip-protection,fundraising-legal,term-sheets,gdpr,contracts", "domain_expertise": "legal,corporate-formation,intellectual-property,compliance", "investment_thesis": "I provide legal advisory, not investment. Focused on helping EU and US startups with incorporation, IP strategy, and fundraising documentation."},
            3: {"fee_structure": "hourly"},
            4: {"availability": "10 hours/week", "cal_booking_link": "https://cal.com/hansmueller-law", "linkedin_url": "https://linkedin.com/in/hansmueller-legal", "website_url": "https://muellerlaw.eu"},
        },
    },
    {
        "register": {"email": "lisa.wong@demo.com", "password": "Demo1234!", "first_name": "Lisa", "last_name": "Wong"},
        "type": "advisor",
        "steps": {
            1: {"headline": "Go-to-Market Advisor | B2B SaaS | $0→$10M ARR", "bio": "VP Sales at 2 unicorns (Datadog, Notion). I help B2B SaaS founders build their first sales motion — ICP, outbound, pricing, and hiring the first 3 AEs.", "location": "San Francisco, CA"},
            2: {"skills": "b2b-sales,go-to-market,pricing,outbound,sales-hiring,crm-setup", "domain_expertise": "saas,b2b,enterprise-sales,plg,sales-operations", "investment_thesis": "Advisory only. I work with seed/Series A B2B SaaS companies that have product-market fit signals but need to build a repeatable sales process."},
            3: {"fee_structure": "retainer"},
            4: {"availability": "4 hours/week", "cal_booking_link": "https://cal.com/lisawong-gtm", "linkedin_url": "https://linkedin.com/in/lisawong-sales"},
        },
    },

    # ── FOUNDERS (5) ───────────────────────────────────────────────

    {
        "register": {"email": "marcus.chen@demo.com", "password": "Demo1234!", "first_name": "Marcus", "last_name": "Chen"},
        "type": "founder",
        "steps": {
            1: {"headline": "AI/ML Founder | Clinical Trial Matching Platform", "bio": "PhD in ML from Stanford, 5 years at OpenAI. Building an AI-powered clinical trial matching platform. Working prototype, $50K in grants, LOIs from 3 hospitals.", "location": "Austin, TX"},
            2: {"startup_stage": "pre_seed", "industry": "healthtech", "funding_stage": "pre-seed (grant funded)"},
            3: {"looking_for_roles": "CEO,COO,Head of BD", "cofounder_brief": "I've built the tech — a BERT-based model that matches patients to clinical trials with 94% accuracy. Need someone who can sell to pharma companies, build hospital partnerships, and lead our seed raise.", "equity_offered": "30-40%", "commitment_level": "full_time"},
            4: {"skills": "machine-learning,python,nlp,healthcare,product", "linkedin_url": "https://linkedin.com/in/marcuschen-ai", "website_url": "https://trialmatcha.ai"},
        },
    },
    {
        "register": {"email": "nina.rodriguez@demo.com", "password": "Demo1234!", "first_name": "Nina", "last_name": "Rodriguez"},
        "type": "founder",
        "steps": {
            1: {"headline": "Edtech Founder | AI Tutoring for K-12", "bio": "Former teacher turned founder. Building personalized AI tutoring that adapts to each student's learning style. 500 beta users, 85% retention rate.", "location": "Miami, FL"},
            2: {"startup_stage": "seed", "industry": "edtech", "funding_stage": "seed ($200K raised)"},
            3: {"looking_for_roles": "CTO,ML Engineer", "cofounder_brief": "I have the education expertise, GTM motion, and initial traction. Need a technical co-founder to rebuild our prototype into a scalable product with proper ML personalization.", "equity_offered": "25-35%", "commitment_level": "full_time"},
            4: {"skills": "education,product-management,sales,curriculum-design", "linkedin_url": "https://linkedin.com/in/ninarodriguez-ed", "website_url": "https://learnloop.ai"},
        },
    },
    {
        "register": {"email": "james.okafor@demo.com", "password": "Demo1234!", "first_name": "James", "last_name": "Okafor"},
        "type": "founder",
        "steps": {
            1: {"headline": "Fintech Founder | Cross-border Payments for Africa", "bio": "Ex-TransferWise engineer. Building instant, low-cost cross-border payments between Africa and the rest of the world. Licensed in Nigeria and Kenya.", "location": "Lagos, Nigeria"},
            2: {"startup_stage": "seed", "industry": "fintech", "funding_stage": "seed ($500K raised)"},
            3: {"looking_for_roles": "Head of Compliance,CFO", "cofounder_brief": "We have the tech and licenses. Processing $2M/month. Need a compliance expert who understands multi-jurisdiction money transmission regulations across Africa, EU, and US.", "equity_offered": "10-15%", "commitment_level": "full_time"},
            4: {"skills": "payments,engineering,regulatory,python,postgresql", "linkedin_url": "https://linkedin.com/in/jamesokafor-fintech", "website_url": "https://sendbridge.io"},
        },
    },
    {
        "register": {"email": "sophie.martin@demo.com", "password": "Demo1234!", "first_name": "Sophie", "last_name": "Martin"},
        "type": "founder",
        "steps": {
            1: {"headline": "Climate Tech Founder | Carbon Accounting SaaS", "bio": "Environmental scientist turned founder. Building automated carbon accounting for mid-market companies. Integrates with ERP systems. 12 paying customers.", "location": "Amsterdam, Netherlands"},
            2: {"startup_stage": "seed", "industry": "cleantech", "funding_stage": "seed ($350K raised)"},
            3: {"looking_for_roles": "CTO,Head of Engineering", "cofounder_brief": "I've validated the market and built the sales motion. We have 12 paying customers at $2K/mo. Need a technical co-founder to own the product — ERP integrations, data pipelines, and the calculation engine.", "equity_offered": "20-30%", "commitment_level": "full_time"},
            4: {"skills": "sustainability,carbon-accounting,sales,partnerships,erp", "linkedin_url": "https://linkedin.com/in/sophiemartin-climate", "website_url": "https://carbonsync.io"},
        },
    },
    {
        "register": {"email": "kevin.nakamura@demo.com", "password": "Demo1234!", "first_name": "Kevin", "last_name": "Nakamura"},
        "type": "founder",
        "steps": {
            1: {"headline": "Gaming Founder | AI NPCs for Open-World Games", "bio": "10 years in AAA game dev (Rockstar, Naughty Dog). Building AI-powered NPCs that have persistent memory and emergent behavior. Unreal Engine plugin.", "location": "Tokyo, Japan"},
            2: {"startup_stage": "idea", "industry": "gaming", "funding_stage": "bootstrapped"},
            3: {"looking_for_roles": "ML Engineer,3D Artist,Business Dev", "cofounder_brief": "I have the game dev expertise and a working prototype in UE5. Looking for an ML engineer to build the LLM-powered NPC brain, and a business person to talk to game studios. This is a $50B market.", "equity_offered": "20-25%", "commitment_level": "full_time"},
            4: {"skills": "unreal-engine,c++,game-design,ai,3d-graphics", "linkedin_url": "https://linkedin.com/in/kevinnakamura-games", "website_url": "https://sentientnpc.com"},
        },
    },
]


async def seed():
    async with httpx.AsyncClient(base_url=BASE, timeout=30) as client:
        for user_data in USERS:
            email = user_data["register"]["email"]
            profile_type = user_data["type"]
            print(f"\n{'='*55}")
            print(f"  {user_data['register']['first_name']} {user_data['register']['last_name']} ({profile_type})")
            print(f"  {email}")

            # Step 1: Register
            res = await client.post("/auth/register", json=user_data["register"])
            if res.status_code == 400 and "already registered" in res.text.lower():
                res = await client.post("/auth/login", json={
                    "email": email,
                    "password": user_data["register"]["password"],
                })
                if res.status_code != 200:
                    print(f"  ERROR: Login failed: {res.text}")
                    continue
                token = res.json()["access_token"]
                print(f"  Logged in (already registered)")
            elif res.status_code == 201:
                token = res.json()["access_token"]
                print(f"  Registered")
            else:
                print(f"  ERROR: Register failed: {res.text}")
                continue

            headers = {"Authorization": f"Bearer {token}"}

            # Step 2: Start onboarding
            res = await client.post("/marketplace/onboarding/start", json={"profile_type": profile_type}, headers=headers)
            if res.status_code == 409:
                print(f"  Profile exists — ensuring public")
                await client.patch("/marketplace/profiles/me/visibility", json={"is_public": True}, headers=headers)
                continue
            elif res.status_code != 201:
                print(f"  ERROR: Onboarding start failed: {res.text}")
                continue
            print(f"  Onboarding started")

            # Step 3: Complete all 4 steps
            for step_num, step_data in user_data["steps"].items():
                # Convert comma-separated strings to arrays for array fields
                processed = {}
                array_fields = {"skills", "domain_expertise", "investment_stages", "looking_for_roles", "service_offerings"}
                number_fields = {"years_experience", "hourly_rate", "check_size_min", "check_size_max"}
                for k, v in step_data.items():
                    if k in array_fields:
                        processed[k] = [s.strip() for s in v.split(",")]
                    elif k in number_fields:
                        processed[k] = float(v)
                    else:
                        processed[k] = v

                res = await client.patch(
                    f"/marketplace/onboarding/step/{step_num}",
                    json={"data": processed},
                    headers=headers,
                )
                if res.status_code == 200:
                    status = res.json()
                    print(f"  Step {step_num}/4 ✓  score={status['profile_score']}")
                else:
                    print(f"  ERROR: Step {step_num} failed: {res.text}")

            # Step 4: Publish
            res = await client.patch("/marketplace/profiles/me/visibility", json={"is_public": True}, headers=headers)
            if res.status_code == 200:
                print(f"  Published!")
            else:
                print(f"  ERROR: Publish failed: {res.text}")

    # Print credentials table
    print(f"\n\n{'='*70}")
    print("  DEMO CREDENTIALS (all passwords: Demo1234!)")
    print(f"{'='*70}")
    print(f"  {'Type':<14} {'Name':<22} {'Email':<35}")
    print(f"  {'-'*14} {'-'*22} {'-'*35}")
    for u in USERS:
        r = u["register"]
        print(f"  {u['type']:<14} {r['first_name']+' '+r['last_name']:<22} {r['email']:<35}")
    print()


if __name__ == "__main__":
    asyncio.run(seed())
