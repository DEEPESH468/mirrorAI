"""Skin analysis service placeholder.

Skin analysis remains scaffolded while the current implementation focuses on
local face detection, face mesh, and face-shape classification.
"""

from python.models.schemas import AiModuleResult


def analyze_skin() -> AiModuleResult:
    return AiModuleResult(
        module="skin",
        status="not_implemented",
        message="Skin analysis, tone, redness, acne, wrinkle, oiliness, and dark-circle modules will be implemented here.",
    )
