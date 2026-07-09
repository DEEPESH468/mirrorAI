from python.models.schemas import AiModuleResult


def build_recommendations() -> AiModuleResult:
    return AiModuleResult(
        module="recommendation",
        status="not_implemented",
        message="Personalized recommendation rules will be implemented in this service.",
    )
