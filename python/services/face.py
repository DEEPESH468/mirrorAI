from python.models.schemas import AiModuleResult


def analyze_face() -> AiModuleResult:
    return AiModuleResult(
        module="face",
        status="not_implemented",
        message="Face detection and landmark analysis will be implemented in this module.",
    )
