"""Hair analysis service placeholder.

The current implementation does not run hairstyle, hair-color, or hair-health
AI. This module exists so future local OpenCV/SAM segmentation and analysis can
be added behind a stable service boundary.
"""

from python.models.schemas import AiModuleResult


def analyze_hair() -> AiModuleResult:
    return AiModuleResult(
        module="hair",
        status="not_implemented",
        message="Hair segmentation, density, length, type, frizz, and color modules will be implemented here.",
    )
