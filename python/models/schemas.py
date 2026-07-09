"""Pydantic schemas for MirrorAI API contracts.

These models define the stable JSON shape shared by FastAPI routes, local AI
services, and the Next.js proxy. They intentionally expose structured face
results instead of provider-specific payloads.
"""

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

ModuleStatus = Literal["completed", "not_implemented", "skipped"]
FaceShapeLabel = Literal[
    "oval",
    "round",
    "square",
    "rectangle",
    "diamond",
    "heart",
    "triangle",
]


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


class ImageInfo(BaseModel):
    width: int
    height: int
    contentType: str | None = None


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int
    xMin: float
    yMin: float
    widthRatio: float
    heightRatio: float


class FaceDetection(BaseModel):
    confidence: float
    boundingBox: BoundingBox
    keypoints: dict[str, dict[str, float]]


class Landmark(BaseModel):
    index: int
    x: float
    y: float
    z: float
    pixelX: int
    pixelY: int


class FaceMesh(BaseModel):
    landmarkCount: int
    landmarks: list[Landmark]


class FaceShapeMeasurements(BaseModel):
    faceHeight: float
    cheekboneWidth: float
    jawWidth: float
    foreheadWidth: float
    heightToWidthRatio: float
    jawToCheekRatio: float
    foreheadToCheekRatio: float


class FaceShapeResult(BaseModel):
    shape: FaceShapeLabel
    confidence: float
    measurements: FaceShapeMeasurements
    explanation: str


class FaceCoreResponse(BaseModel):
    engine: str
    status: Literal["completed"]
    image: ImageInfo
    detection: FaceDetection
    mesh: FaceMesh | None = None
    faceShape: FaceShapeResult | None = None


class FaceDetectionResponse(BaseModel):
    engine: str
    status: Literal["completed"]
    image: ImageInfo
    detection: FaceDetection


class FaceMeshResponse(BaseModel):
    engine: str
    status: Literal["completed"]
    image: ImageInfo
    detection: FaceDetection
    mesh: FaceMesh


class FaceShapeResponse(BaseModel):
    engine: str
    status: Literal["completed"]
    image: ImageInfo
    detection: FaceDetection
    mesh: FaceMesh
    faceShape: FaceShapeResult
