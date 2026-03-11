from __future__ import annotations

from typing import Dict

from pydantic import BaseModel


class SectionStatus(BaseModel):
    complete: bool
    completeness: int


class OnboardingStatus(BaseModel):
    overall_completeness: int
    sections: Dict[str, SectionStatus]
