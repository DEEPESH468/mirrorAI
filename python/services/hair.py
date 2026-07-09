from python.models.schemas import AiModuleResult


def analyze_hair() -> AiModuleResult:
    return AiModuleResult(
        module="hair",
        status="not_implemented",
        message="Hair segmentation, density, length, type, frizz, and color modules will be implemented here.",
    )
