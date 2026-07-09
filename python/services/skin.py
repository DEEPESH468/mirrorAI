from python.models.schemas import AiModuleResult


def analyze_skin() -> AiModuleResult:
    return AiModuleResult(
        module="skin",
        status="not_implemented",
        message="Skin analysis, tone, redness, acne, wrinkle, oiliness, and dark-circle modules will be implemented here.",
    )
