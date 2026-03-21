"""Seed 3 dummy marketplace profiles (professional, advisor, founder).

Usage:
    DATABASE_URL=postgresql+asyncpg://sidda:postgres@localhost:5432/onlyfounders python3 scripts/seed_profiles.py
"""
import asyncio
import httpx

BASE = "http://localhost:8000/api/v1"

USERS = [
    {
        "register": {
            "email": "alex.professional@demo.com",
            "password": "Demo1234!",
            "first_name": "Alex",
            "last_name": "Rivera",
        },
        "profile": {
            "profile_type": "professional",
            "headline": "Full-Stack Developer | React + Python",
            "bio": "10 years building SaaS products. Ex-Google, ex-Stripe. I specialize in taking MVPs from 0 to 1 with clean architecture and fast iteration. Available for contract or full-time roles with equity.",
            "location": "San Francisco, CA",
            "skills": ["react", "python", "fastapi", "typescript", "postgresql", "aws", "docker"],
            "linkedin_url": "https://linkedin.com/in/alexrivera",
            "website_url": "https://alexrivera.dev",
            "professional_data": {
                "primary_role": "Full-Stack Developer",
                "years_experience": 10,
                "hourly_rate": 175.00,
                "availability_status": "open_to_offers",
                "service_offerings": ["MVP Development", "Technical Architecture", "Code Review", "CTO-as-a-Service"],
                "portfolio_url": "https://alexrivera.dev/portfolio",
                "cal_booking_link": "https://cal.com/alexrivera",
            },
        },
    },
    {
        "register": {
            "email": "priya.advisor@demo.com",
            "password": "Demo1234!",
            "first_name": "Priya",
            "last_name": "Sharma",
        },
        "profile": {
            "profile_type": "advisor",
            "headline": "Angel Investor & Fintech Advisor | 40+ Portfolio Companies",
            "bio": "Former VP at Goldman Sachs turned angel investor. I back pre-seed and seed stage fintech, payments, and embedded finance startups. I write $25K-$100K checks and actively help with GTM strategy, banking partnerships, and fundraising.",
            "location": "New York, NY",
            "skills": ["fundraising", "fintech", "go-to-market", "strategy", "banking", "payments", "board-advisory"],
            "linkedin_url": "https://linkedin.com/in/priyasharma-investor",
            "advisor_data": {
                "domain_expertise": ["fintech", "payments", "embedded-finance", "lending", "neobanking"],
                "investment_thesis": "Early-stage B2B fintech solving real pain points in payments infrastructure, lending automation, or compliance tooling. Must have technical founders.",
                "investment_stages": ["pre_seed", "seed"],
                "portfolio_companies": [
                    {"name": "PayStack", "role": "Advisor"},
                    {"name": "LendFlow", "role": "Board Observer"},
                    {"name": "ComplianceAI", "role": "Angel Investor"},
                ],
                "check_size_min": 25000,
                "check_size_max": 100000,
                "fee_structure": "equity",
                "availability": "5 hours/week",
                "cal_booking_link": "https://cal.com/priyasharma",
            },
        },
    },
    {
        "register": {
            "email": "marcus.founder@demo.com",
            "password": "Demo1234!",
            "first_name": "Marcus",
            "last_name": "Chen",
        },
        "profile": {
            "profile_type": "founder",
            "headline": "AI/ML Founder Seeking Business Co-founder",
            "bio": "PhD in ML from Stanford, 5 years at OpenAI. Building an AI-powered clinical trial matching platform. Have a working prototype, $50K in grants, and LOIs from 3 hospitals. Looking for a business co-founder who knows healthcare GTM and fundraising.",
            "location": "Austin, TX",
            "skills": ["machine-learning", "python", "nlp", "healthcare", "product", "research"],
            "linkedin_url": "https://linkedin.com/in/marcuschen-ai",
            "website_url": "https://trialmatcha.ai",
            "founder_data": {
                "looking_for_roles": ["CEO", "COO", "Head of BD"],
                "cofounder_brief": "I've built the tech — a BERT-based model that matches patients to clinical trials with 94% accuracy. We have a prototype, hospital LOIs, and grant funding. I need someone who can sell to pharma companies, build partnerships with hospital networks, and lead our seed raise. Offering 30-40% equity for the right co-founder.",
                "commitment_level": "full_time",
                "equity_offered": "30-40%",
                "startup_stage": "pre_seed",
                "industry": "healthtech",
                "remote_ok": True,
                "funding_stage": "pre-seed (grant funded)",
            },
        },
    },
]


async def seed():
    async with httpx.AsyncClient(base_url=BASE, timeout=30) as client:
        for user_data in USERS:
            email = user_data["register"]["email"]
            print(f"\n{'='*50}")
            print(f"Creating: {email}")

            # Register
            res = await client.post("/auth/register", json=user_data["register"])
            if res.status_code == 400 and "already registered" in res.text.lower():
                # Login instead
                res = await client.post("/auth/login", json={
                    "email": user_data["register"]["email"],
                    "password": user_data["register"]["password"],
                })
                if res.status_code != 200:
                    print(f"  Login failed: {res.text}")
                    continue
                token = res.json()["access_token"]
            elif res.status_code == 201:
                token = res.json()["access_token"]
            else:
                print(f"  Register failed: {res.text}")
                continue

            headers = {"Authorization": f"Bearer {token}"}
            print(f"  Authenticated")

            # Create profile
            res = await client.post("/marketplace/profiles", json=user_data["profile"], headers=headers)
            if res.status_code == 409:
                print(f"  Profile already exists — skipping creation")
                # Make sure it's public
                await client.patch("/marketplace/profiles/me/visibility", json={"is_public": True}, headers=headers)
                print(f"  Ensured profile is public")
                continue
            elif res.status_code == 201:
                profile = res.json()
                print(f"  Profile created: {profile['profile_type']} | Score: {profile['profile_score']}")
            else:
                print(f"  Profile creation failed: {res.text}")
                continue

            # Publish profile
            res = await client.patch("/marketplace/profiles/me/visibility", json={"is_public": True}, headers=headers)
            if res.status_code == 200:
                print(f"  Published!")
            else:
                print(f"  Publish failed: {res.text}")

    print(f"\n{'='*50}")
    print("DEMO CREDENTIALS")
    print("="*50)
    print()
    for user_data in USERS:
        r = user_data["register"]
        p = user_data["profile"]
        print(f"  {p['profile_type'].upper()}")
        print(f"    Email:    {r['email']}")
        print(f"    Password: {r['password']}")
        print(f"    Name:     {r['first_name']} {r['last_name']}")
        print()


if __name__ == "__main__":
    asyncio.run(seed())
