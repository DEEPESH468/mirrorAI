"""Makeup try-on service placeholder.

Makeup rendering is intentionally out of scope for the face-core pass. The
module keeps the API contract stable while avoiding paid virtual try-on APIs.
"""

from python.models.schemas import AiModuleResult


def apply_makeup() -> AiModuleResult:
    return AiModuleResult(
        module="makeup",
        status="not_implemented",
        message="Virtual lipstick, foundation, blush, eyeliner, and eyeshadow modules will be implemented here.",
    )
