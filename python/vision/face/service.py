"""Face AI orchestration service.

This module combines free local components:

- OpenCV-compatible RGB image arrays via NumPy/Pillow preprocessing.
- MediaPipe Face Detection for primary-face localization.
- MediaPipe Face Mesh for 468 landmarks.
- Deterministic face-shape classification from mesh geometry.

InsightFace, ONNX Runtime, and Segment Anything are declared project
dependencies for future local identity-safe embeddings, ONNX model execution,
and segmentation tasks. They are not invoked for hairstyle or beard overlays in
this AI-core pass.
"""

from python.models.schemas import (
    AiModuleResult,
    FaceCoreResponse,
    FaceDetectionResponse,
    FaceMeshResponse,
    FaceShapeResponse,
    ImageInfo,
)
from python.vision.face.detection import detect_primary_face
from python.vision.face.mesh import extract_face_mesh
from python.vision.face.shape import classify_face_shape
from python.vision.utils.image import DecodedImage


ENGINE_NAME = "MirrorAI local open-source face core"


def analyze_face(image: DecodedImage) -> FaceCoreResponse:
    """Run complete face-core analysis for the existing product endpoint."""

    detection = detect_primary_face(image.rgb)
    mesh = extract_face_mesh(image.rgb)
    face_shape = classify_face_shape(mesh)

    return FaceCoreResponse(
        engine=ENGINE_NAME,
        status="completed",
        image=_image_info(image),
        detection=detection,
        mesh=mesh,
        faceShape=face_shape,
    )


def detect_face(image: DecodedImage) -> FaceDetectionResponse:
    """Run face detection only."""

    return FaceDetectionResponse(
        engine=ENGINE_NAME,
        status="completed",
        image=_image_info(image),
        detection=detect_primary_face(image.rgb),
    )


def map_face_mesh(image: DecodedImage) -> FaceMeshResponse:
    """Run face detection and 468-landmark mesh extraction."""

    return FaceMeshResponse(
        engine=ENGINE_NAME,
        status="completed",
        image=_image_info(image),
        detection=detect_primary_face(image.rgb),
        mesh=extract_face_mesh(image.rgb),
    )


def detect_face_shape(image: DecodedImage) -> FaceShapeResponse:
    """Run face detection, mesh extraction, and face-shape classification."""

    detection = detect_primary_face(image.rgb)
    mesh = extract_face_mesh(image.rgb)

    return FaceShapeResponse(
        engine=ENGINE_NAME,
        status="completed",
        image=_image_info(image),
        detection=detection,
        mesh=mesh,
        faceShape=classify_face_shape(mesh),
    )


def face_module_result() -> AiModuleResult:
    """Return a module summary for consultation reports."""

    return AiModuleResult(
        module="face",
        status="completed",
        message="Face detection, 468-point face mesh, and face-shape analysis completed locally.",
    )


def _image_info(image: DecodedImage) -> ImageInfo:
    return ImageInfo(
        width=image.width,
        height=image.height,
        contentType=image.content_type,
    )
