"""Search backend for marketplace discovery.

PostgreSQL-native implementation using tsvector full-text search,
pg_trgm fuzzy matching, and JSONB containment queries.
Abstracts behind SearchBackend for future Elasticsearch swap.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import json

from sqlalchemy import Integer, case, cast, func, or_, select, text, type_coerce
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.marketplace_profile import (
    AdvisorProfile,
    FounderMarketplaceProfile,
    MarketplaceProfile,
    ProfessionalProfile,
)


@dataclass
class SearchQuery:
    text: str | None = None
    profile_type: str | None = None
    skills: list[str] = field(default_factory=list)
    location: str | None = None
    sort_by: str = "score"
    page: int = 1
    page_size: int = 20
    # Type-specific
    min_rate: float | None = None
    max_rate: float | None = None
    availability: str | None = None
    min_experience: int | None = None
    domain_expertise: list[str] = field(default_factory=list)
    investment_stages: list[str] = field(default_factory=list)
    fee_structure: str | None = None
    has_booking: bool | None = None
    looking_for: str | None = None
    startup_stage: str | None = None
    industry: str | None = None
    commitment: str | None = None
    remote_ok: bool | None = None
    include_facets: bool = False


@dataclass
class SearchResult:
    items: list[MarketplaceProfile]
    total: int
    facets: dict[str, Any] | None = None


class SearchBackend:
    async def search(self, session: AsyncSession, query: SearchQuery) -> SearchResult:
        raise NotImplementedError


class PostgresSearchBackend(SearchBackend):

    async def search(self, session: AsyncSession, query: SearchQuery) -> SearchResult:
        MP = MarketplaceProfile

        # Base query with eager loads
        stmt = (
            select(MP)
            .options(
                selectinload(MP.professional_data),
                selectinload(MP.advisor_data),
                selectinload(MP.founder_data),
                selectinload(MP.user),
            )
        )
        count_stmt = select(func.count()).select_from(MP)

        # ── Base filters (always applied) ─────────────────────────
        base_filters = [
            MP.is_public == True,
            MP.profile_score >= 40,
        ]
        for f in base_filters:
            stmt = stmt.where(f)
            count_stmt = count_stmt.where(f)

        # ── Profile type ──────────────────────────────────────────
        if query.profile_type:
            stmt = stmt.where(MP.profile_type == query.profile_type)
            count_stmt = count_stmt.where(MP.profile_type == query.profile_type)

        # ── Location ──────────────────────────────────────────────
        if query.location:
            loc = MP.location.ilike(f"%{query.location}%")
            stmt = stmt.where(loc)
            count_stmt = count_stmt.where(loc)

        # ── Skills (JSONB containment) ────────────────────────────
        for skill in query.skills:
            sf = MP.skills.op("@>")(cast(json.dumps([skill]), JSONB))
            stmt = stmt.where(sf)
            count_stmt = count_stmt.where(sf)

        # ── Full-text search ──────────────────────────────────────
        ts_query = None
        if query.text:
            ts_query = func.websearch_to_tsquery("english", query.text)
            fts_filter = MP.search_vector.op("@@")(ts_query)
            stmt = stmt.where(fts_filter)
            count_stmt = count_stmt.where(fts_filter)

        # ── Professional-specific filters ─────────────────────────
        needs_pro_join = any([
            query.min_rate is not None,
            query.max_rate is not None,
            query.availability is not None,
            query.min_experience is not None,
        ])
        if needs_pro_join:
            stmt = stmt.join(ProfessionalProfile, ProfessionalProfile.profile_id == MP.id, isouter=True)
            count_stmt = count_stmt.join(ProfessionalProfile, ProfessionalProfile.profile_id == MP.id, isouter=True)
            if query.min_rate is not None:
                stmt = stmt.where(ProfessionalProfile.hourly_rate >= query.min_rate)
                count_stmt = count_stmt.where(ProfessionalProfile.hourly_rate >= query.min_rate)
            if query.max_rate is not None:
                stmt = stmt.where(ProfessionalProfile.hourly_rate <= query.max_rate)
                count_stmt = count_stmt.where(ProfessionalProfile.hourly_rate <= query.max_rate)
            if query.availability:
                stmt = stmt.where(ProfessionalProfile.availability_status == query.availability)
                count_stmt = count_stmt.where(ProfessionalProfile.availability_status == query.availability)
            if query.min_experience is not None:
                stmt = stmt.where(ProfessionalProfile.years_experience >= query.min_experience)
                count_stmt = count_stmt.where(ProfessionalProfile.years_experience >= query.min_experience)

        # ── Advisor-specific filters ──────────────────────────────
        needs_adv_join = any([
            query.domain_expertise,
            query.investment_stages,
            query.fee_structure is not None,
            query.has_booking is not None,
        ])
        if needs_adv_join:
            stmt = stmt.join(AdvisorProfile, AdvisorProfile.profile_id == MP.id, isouter=True)
            count_stmt = count_stmt.join(AdvisorProfile, AdvisorProfile.profile_id == MP.id, isouter=True)
            for exp in query.domain_expertise:
                stmt = stmt.where(AdvisorProfile.domain_expertise.op("@>")(cast(json.dumps([exp]), JSONB)))
                count_stmt = count_stmt.where(AdvisorProfile.domain_expertise.op("@>")(cast(json.dumps([exp]), JSONB)))
            for stg in query.investment_stages:
                stmt = stmt.where(AdvisorProfile.investment_stages.op("@>")(cast(json.dumps([stg]), JSONB)))
                count_stmt = count_stmt.where(AdvisorProfile.investment_stages.op("@>")(cast(json.dumps([stg]), JSONB)))
            if query.fee_structure:
                stmt = stmt.where(AdvisorProfile.fee_structure == query.fee_structure)
                count_stmt = count_stmt.where(AdvisorProfile.fee_structure == query.fee_structure)
            if query.has_booking is True:
                stmt = stmt.where(AdvisorProfile.cal_booking_link.isnot(None))
                count_stmt = count_stmt.where(AdvisorProfile.cal_booking_link.isnot(None))

        # ── Founder-specific filters ──────────────────────────────
        needs_fnd_join = any([
            query.looking_for is not None,
            query.startup_stage is not None,
            query.industry is not None,
            query.commitment is not None,
            query.remote_ok is not None,
        ])
        if needs_fnd_join:
            stmt = stmt.join(FounderMarketplaceProfile, FounderMarketplaceProfile.profile_id == MP.id, isouter=True)
            count_stmt = count_stmt.join(FounderMarketplaceProfile, FounderMarketplaceProfile.profile_id == MP.id, isouter=True)
            if query.looking_for:
                stmt = stmt.where(FounderMarketplaceProfile.looking_for_roles.op("@>")(cast(json.dumps([query.looking_for]), JSONB)))
                count_stmt = count_stmt.where(FounderMarketplaceProfile.looking_for_roles.op("@>")(cast(json.dumps([query.looking_for]), JSONB)))
            if query.startup_stage:
                stmt = stmt.where(FounderMarketplaceProfile.startup_stage == query.startup_stage)
                count_stmt = count_stmt.where(FounderMarketplaceProfile.startup_stage == query.startup_stage)
            if query.industry:
                stmt = stmt.where(FounderMarketplaceProfile.industry == query.industry)
                count_stmt = count_stmt.where(FounderMarketplaceProfile.industry == query.industry)
            if query.commitment:
                stmt = stmt.where(FounderMarketplaceProfile.commitment_level == query.commitment)
                count_stmt = count_stmt.where(FounderMarketplaceProfile.commitment_level == query.commitment)
            if query.remote_ok is not None:
                stmt = stmt.where(FounderMarketplaceProfile.remote_ok == query.remote_ok)
                count_stmt = count_stmt.where(FounderMarketplaceProfile.remote_ok == query.remote_ok)

        # ── Sorting ───────────────────────────────────────────────
        if query.sort_by == "relevance" and ts_query is not None:
            stmt = stmt.order_by(func.ts_rank_cd(MP.search_vector, ts_query).desc())
        elif query.sort_by == "newest":
            stmt = stmt.order_by(MP.created_at.desc())
        elif query.sort_by == "rate_low":
            if not needs_pro_join:
                stmt = stmt.join(ProfessionalProfile, ProfessionalProfile.profile_id == MP.id, isouter=True)
            stmt = stmt.order_by(ProfessionalProfile.hourly_rate.asc().nullslast())
        elif query.sort_by == "rate_high":
            if not needs_pro_join:
                stmt = stmt.join(ProfessionalProfile, ProfessionalProfile.profile_id == MP.id, isouter=True)
            stmt = stmt.order_by(ProfessionalProfile.hourly_rate.desc().nullslast())
        else:  # "score" default
            stmt = stmt.order_by(MP.profile_score.desc())

        # ── Pagination ────────────────────────────────────────────
        offset = (query.page - 1) * query.page_size
        stmt = stmt.limit(query.page_size).offset(offset)

        # ── Execute ───────────────────────────────────────────────
        result = await session.execute(stmt)
        items = list(result.scalars().all())
        total = (await session.execute(count_stmt)).scalar() or 0

        # ── Facets ────────────────────────────────────────────────
        facets = None
        if query.include_facets:
            facets = await self._compute_facets(session, query)

        return SearchResult(items=items, total=total, facets=facets)

    async def _compute_facets(
        self, session: AsyncSession, query: SearchQuery
    ) -> dict[str, Any]:
        MP = MarketplaceProfile
        base = [MP.is_public == True, MP.profile_score >= 40]

        # Profile type counts
        type_stmt = (
            select(MP.profile_type, func.count())
            .where(*base)
            .group_by(MP.profile_type)
        )
        type_rows = (await session.execute(type_stmt)).all()
        profile_types = [{"value": r[0], "count": r[1]} for r in type_rows]

        # Skills counts (unnest JSONB array, top 20)
        skills_stmt = (
            select(
                func.jsonb_array_elements_text(MP.skills).label("skill"),
                func.count().label("cnt"),
            )
            .where(*base, MP.skills.isnot(None))
            .group_by(text("skill"))
            .order_by(text("cnt DESC"))
            .limit(20)
        )
        skill_rows = (await session.execute(skills_stmt)).all()
        skills = [{"value": r[0], "count": r[1]} for r in skill_rows]

        # Availability counts (professionals only)
        avail_stmt = (
            select(ProfessionalProfile.availability_status, func.count())
            .join(MP, MP.id == ProfessionalProfile.profile_id)
            .where(*base, ProfessionalProfile.availability_status.isnot(None))
            .group_by(ProfessionalProfile.availability_status)
        )
        avail_rows = (await session.execute(avail_stmt)).all()
        availability = [{"value": str(r[0].value) if hasattr(r[0], 'value') else str(r[0]), "count": r[1]} for r in avail_rows]

        # Hourly rate ranges
        rate_stmt = (
            select(
                case(
                    (ProfessionalProfile.hourly_rate < 50, "0-50"),
                    (ProfessionalProfile.hourly_rate < 100, "50-100"),
                    (ProfessionalProfile.hourly_rate < 200, "100-200"),
                    else_="200+",
                ).label("bucket"),
                func.count().label("cnt"),
            )
            .join(MP, MP.id == ProfessionalProfile.profile_id)
            .where(*base, ProfessionalProfile.hourly_rate.isnot(None))
            .group_by(text("bucket"))
            .order_by(text("bucket"))
        )
        rate_rows = (await session.execute(rate_stmt)).all()
        hourly_rate_ranges = [{"value": r[0], "count": r[1]} for r in rate_rows]

        # Location counts (top 15)
        loc_stmt = (
            select(MP.location, func.count())
            .where(*base, MP.location.isnot(None), MP.location != "")
            .group_by(MP.location)
            .order_by(func.count().desc())
            .limit(15)
        )
        loc_rows = (await session.execute(loc_stmt)).all()
        locations = [{"value": r[0], "count": r[1]} for r in loc_rows]

        return {
            "profile_types": profile_types,
            "skills": skills,
            "availability": availability,
            "hourly_rate_ranges": hourly_rate_ranges,
            "locations": locations,
        }


# Singleton
_search_backend: SearchBackend | None = None


def get_search_backend() -> SearchBackend:
    global _search_backend
    if _search_backend is None:
        _search_backend = PostgresSearchBackend()
    return _search_backend
