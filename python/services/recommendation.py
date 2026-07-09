"""Recommendation service placeholder.

Future salon recommendation rules can consume face-shape, skin, hair, and
style-analysis outputs from local models. No remote recommendation API is used.
"""

from python.models.schemas import AiModuleResult


def build_recommendations() -> AiModuleResult:
    return AiModuleResult(
        module="recommendation",
        status="not_implemented",
        message="Personalized recommendation rules will be implemented in this service.",
    )
