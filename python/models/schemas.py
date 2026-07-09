from typing import Literal, TypeGuard

from pydantic import BaseModel


ProductId = Literal[
    "skin-analysis",
    "makeup",
    "hair-color",
    "hairstyle",
    "beard",
    "face-shape",
    "hair-analysis",
]

PRODUCT_IDS: tuple[ProductId, ...] = (
    "skin-analysis",
    "makeup",
    "hair-color",
    "hairstyle",
    "beard",
    "face-shape",
    "hair-analysis",
)

ModuleStatus = Literal["not_implemented"]


def is_product_id(value: str) -> TypeGuard[ProductId]:
    return value in PRODUCT_IDS


class AiModuleResult(BaseModel):
    module: str
    status: ModuleStatus
    message: str


class ExperienceMetadata(BaseModel):
    product: ProductId
    productName: str
    optionId: str | None = None
    optionName: str | None = None


class ExperienceResponse(BaseModel):
    imageBase64: str | None = None
    aiResponse: dict[str, object]
    report: dict[str, object]
