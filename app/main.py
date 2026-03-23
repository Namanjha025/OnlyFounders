from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    agents,
    auth,
    calendar,
    documents,
    equity,
    feed,
    financial,
    founder_profile,
    funding_rounds,
    invitations,
    manager,
    marketplace,
    member_documents,
    notifications,
    onboarding,
    product,
    startup_members,
    startups,
    tasks,
    traction,
    workspaces,
)

app = FastAPI(
    title="OnlyFounders API",
    description="AI-native accelerator platform — Startup Profile Intake API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(founder_profile.router)
app.include_router(startups.router)
app.include_router(startup_members.router)
app.include_router(product.router)
app.include_router(traction.router)
app.include_router(financial.router)
app.include_router(funding_rounds.router)
app.include_router(equity.router)
app.include_router(documents.router)
app.include_router(member_documents.router)
app.include_router(tasks.router)
app.include_router(calendar.router)
app.include_router(onboarding.router)
app.include_router(invitations.startup_router)
app.include_router(invitations.user_router)
app.include_router(agents.registry_router)
app.include_router(agents.team_router)
app.include_router(agents.chat_router)
app.include_router(manager.router)
app.include_router(marketplace.router)
app.include_router(workspaces.router)
app.include_router(notifications.router)
app.include_router(feed.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
