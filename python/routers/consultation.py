"""Consultation report REST endpoints."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from python.models.schemas import ConsultationReport, ExperienceMetadata
from python.vision.utils.assets import AssetOverlayError
from python.vision.reports.consultation import prepare_consultation
from python.vision.face.detection import FaceDetectionError
from python.vision.face.mesh import FaceMeshError
from python.vision.face.shape import FaceShapeError
from python.vision.hair.service import HairColorError
from python.vision.utils.image import decode_image_upload


router = APIRouter(prefix="/api/consultation", tags=["consultation"])


@router.post("/report", response_model=ConsultationReport)
async def report(
    image: UploadFile = File(...),
    product_name: str = Form(default="Full Consultation", alias="productName"),
) -> ConsultationReport:
    try:
        decoded = await decode_image_upload(image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    metadata = ExperienceMetadata(
        product="face-shape",
        productName=product_name,
    )

    try:
        response = await run_in_threadpool(prepare_consultation, metadata, decoded)
        return ConsultationReport.model_validate(response.report)
    except (AssetOverlayError, FaceDetectionError, FaceMeshError, FaceShapeError, HairColorError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
