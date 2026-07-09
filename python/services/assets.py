"""Placeholder asset-alignment services.

Hairstyle and beard overlays are intentionally not implemented in this AI-core
pass. Future local segmentation/alignment modules can be attached here without
changing the frontend contract.
"""

from python.models.schemas import AiModuleResult


def prepare_asset_overlay(kind: str) -> AiModuleResult:
    return AiModuleResult(
        module=kind,
        status="not_implemented",
        message=f"{kind.title()} asset alignment will be implemented in this service.",
    )
