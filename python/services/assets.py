from python.models.schemas import AiModuleResult


def prepare_asset_overlay(kind: str) -> AiModuleResult:
    return AiModuleResult(
        module=kind,
        status="not_implemented",
        message=f"{kind.title()} asset alignment will be implemented in this service.",
    )
