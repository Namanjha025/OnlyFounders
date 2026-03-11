from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth,
    documents,
    equity,
    financial,
    founder_profile,
    funding_rounds,
    onboarding,
    product,
    startup_members,
    startups,
    traction,
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
app.include_router(onboarding.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
