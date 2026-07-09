from python.models.schemas import AiModuleResult


def apply_makeup() -> AiModuleResult:
    return AiModuleResult(
        module="makeup",
        status="not_implemented",
        message="Virtual lipstick, foundation, blush, eyeliner, and eyeshadow modules will be implemented here.",
    )
