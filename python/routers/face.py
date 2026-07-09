"""REST endpoints for the MirrorAI local face core."""

from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from python.models.schemas import (
    FaceCoreResponse,
    FaceDetectionResponse,
    FaceMeshResponse,
    FaceShapeResponse,
)
from python.services.face import analyze_face, detect_face, detect_face_shape, map_face_mesh
from python.services.face_detection import FaceDetectionError
from python.services.face_mesh import FaceMeshError
from python.services.face_shape import FaceShapeError
from python.utils.image import decode_image_upload


router = APIRouter(prefix="/api/face", tags=["face-core"])


@router.post("/detect", response_model=FaceDetectionResponse)
async def detect(image: UploadFile = File(...)) -> FaceDetectionResponse:
    decoded = await _decode_or_400(image)
    return await _run_or_422(lambda: detect_face(decoded))


@router.post("/mesh", response_model=FaceMeshResponse)
async def mesh(image: UploadFile = File(...)) -> FaceMeshResponse:
    decoded = await _decode_or_400(image)
    return await _run_or_422(lambda: map_face_mesh(decoded))


@router.post("/shape", response_model=FaceShapeResponse)
async def shape(image: UploadFile = File(...)) -> FaceShapeResponse:
    decoded = await _decode_or_400(image)
    return await _run_or_422(lambda: detect_face_shape(decoded))


@router.post("/analyze", response_model=FaceCoreResponse)
async def analyze(image: UploadFile = File(...)) -> FaceCoreResponse:
    decoded = await _decode_or_400(image)
    return await _run_or_422(lambda: analyze_face(decoded))


async def _decode_or_400(image: UploadFile):
    try:
        return await decode_image_upload(image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def _run_or_422(callback):
    try:
        return await run_in_threadpool(callback)
    except (FaceDetectionError, FaceMeshError, FaceShapeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
