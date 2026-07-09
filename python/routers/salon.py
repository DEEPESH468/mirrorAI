"""REST endpoints for virtual salon rendering modules."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from python.models.schemas import MakeupRenderResult, SalonRenderResult
from python.services.assets import AssetOverlayError, render_beard, render_hairstyle
from python.services.face import analyze_face
from python.services.face_detection import FaceDetectionError
from python.services.face_mesh import FaceMeshError
from python.services.face_shape import FaceShapeError
from python.services.hair import HairColorError, simulate_hair_color
from python.services.makeup import render_makeup
from python.utils.image import DecodedImage, decode_image_upload


router = APIRouter(prefix="/api/salon", tags=["virtual-salon"])


@router.post("/hairstyle", response_model=SalonRenderResult)
async def hairstyle(
    image: UploadFile = File(...),
    style_id: str = Form(default="crewcut", alias="style_id"),
    option_name: str | None = Form(default=None, alias="optionName"),
) -> SalonRenderResult:
    decoded = await _decode_or_400(image)
    return await _render_or_422(
        decoded,
        lambda source, mesh: render_hairstyle(source, mesh, style_id, option_name),
    )


@router.post("/beard", response_model=SalonRenderResult)
async def beard(
    image: UploadFile = File(...),
    template_id: str = Form(default="anchor", alias="template_id"),
    option_name: str | None = Form(default=None, alias="optionName"),
) -> SalonRenderResult:
    decoded = await _decode_or_400(image)
    return await _render_or_422(
        decoded,
        lambda source, mesh: render_beard(source, mesh, template_id, option_name),
    )


@router.post("/hair-color", response_model=SalonRenderResult)
async def hair_color(
    image: UploadFile = File(...),
    color_id: str = Form(default="brown", alias="color_id"),
    option_name: str | None = Form(default=None, alias="optionName"),
) -> SalonRenderResult:
    decoded = await _decode_or_400(image)
    return await _render_or_422(
        decoded,
        lambda source, mesh: simulate_hair_color(source, mesh, color_id, option_name),
    )


@router.post("/makeup", response_model=MakeupRenderResult)
async def makeup(
    image: UploadFile = File(...),
    look_id: str = Form(default="soft-glam", alias="look_id"),
) -> MakeupRenderResult:
    decoded = await _decode_or_400(image)
    return await _render_or_422(
        decoded,
        lambda source, mesh: render_makeup(source, mesh, look_id),
    )


async def _decode_or_400(image: UploadFile) -> DecodedImage:
    try:
        return await decode_image_upload(image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def _render_or_422(decoded: DecodedImage, callback) -> SalonRenderResult | MakeupRenderResult:
    try:
        face_analysis = await run_in_threadpool(analyze_face, decoded)
        if face_analysis.mesh is None:
            raise FaceMeshError("A face mesh is required for virtual salon rendering.")
        return await run_in_threadpool(callback, decoded, face_analysis.mesh)
    except (AssetOverlayError, FaceDetectionError, FaceMeshError, FaceShapeError, HairColorError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
