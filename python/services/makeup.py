"""Local virtual makeup rendering service.

The renderer uses MediaPipe landmark masks and OpenCV/Pillow-style alpha
blending. It supports lipstick, foundation, blush, contour, eyeshadow, and
eyeliner without any generated imagery or remote APIs.
"""

import cv2
import numpy as np

from python.models.schemas import AiModuleResult, FaceMesh, MakeupRenderResult
from python.services.landmarks import (
    LEFT_EYE,
    LIPS,
    RIGHT_EYE,
    face_mask,
    filled_mask,
    polygon_from_indices,
    softened,
)
from python.utils.image import DecodedImage, encode_png_data_url


LOOKS = {
    "soft-glam": {
        "lipstick": (150, 74, 72),
        "foundation": (204, 154, 125),
        "blush": (207, 104, 112),
        "contour": (116, 72, 55),
        "eyeshadow": (145, 96, 82),
        "eyeliner": (28, 22, 20),
        "intensity": 0.42,
    },
    "bridal-radiance": {
        "lipstick": (174, 92, 86),
        "foundation": (218, 170, 132),
        "blush": (225, 126, 128),
        "contour": (127, 79, 55),
        "eyeshadow": (168, 122, 91),
        "eyeliner": (24, 21, 20),
        "intensity": 0.5,
    },
    "editorial-evening": {
        "lipstick": (116, 48, 82),
        "foundation": (196, 145, 112),
        "blush": (173, 77, 110),
        "contour": (84, 58, 70),
        "eyeshadow": (84, 59, 92),
        "eyeliner": (14, 14, 18),
        "intensity": 0.62,
    },
}


def makeup_module_result() -> AiModuleResult:
    return AiModuleResult(
        module="makeup",
        status="completed",
        message="Foundation, lipstick, blush, contour, eyeshadow, and eyeliner rendered locally.",
    )


def render_makeup(
    image: DecodedImage,
    mesh: FaceMesh,
    look_id: str,
) -> MakeupRenderResult:
    """Render a complete virtual makeup look."""

    look = LOOKS.get(look_id, LOOKS["soft-glam"])
    result = image.rgb.copy()
    height, width = result.shape[:2]

    result = _foundation(result, mesh, look["foundation"], look["intensity"])
    result = _lipstick(result, mesh, look["lipstick"], look["intensity"])
    result = _blush(result, mesh, look["blush"], look["intensity"])
    result = _contour(result, mesh, look["contour"], look["intensity"])
    result = _eyeshadow(result, mesh, look["eyeshadow"], look["intensity"])
    result = _eyeliner(result, mesh, look["eyeliner"])

    return MakeupRenderResult(
        imageBase64=encode_png_data_url(result),
        lookId=look_id,
        applied=["foundation", "lipstick", "blush", "contour", "eyeshadow", "eyeliner"],
        intensity=float(look["intensity"]),
        width=width,
        height=height,
    )


def _foundation(rgb: np.ndarray, mesh: FaceMesh, color: tuple[int, int, int], intensity: float) -> np.ndarray:
    mask = softened(face_mask(rgb.shape[:2], mesh), 31)
    return _blend(rgb, color, mask, intensity * 0.26)


def _lipstick(rgb: np.ndarray, mesh: FaceMesh, color: tuple[int, int, int], intensity: float) -> np.ndarray:
    mask = softened(filled_mask(rgb.shape[:2], polygon_from_indices(mesh, LIPS)), 13)
    return _blend(rgb, color, mask, intensity * 0.82)


def _blush(rgb: np.ndarray, mesh: FaceMesh, color: tuple[int, int, int], intensity: float) -> np.ndarray:
    landmarks = {landmark.index: landmark for landmark in mesh.landmarks}
    mask = np.zeros(rgb.shape[:2], dtype=np.uint8)
    for cheek, nose in ((234, 2), (454, 2)):
        if cheek not in landmarks or nose not in landmarks:
            continue
        cx = int(landmarks[cheek].pixelX * 0.68 + landmarks[nose].pixelX * 0.32)
        cy = int(landmarks[cheek].pixelY * 0.62 + landmarks[nose].pixelY * 0.38)
        cv2.ellipse(mask, (cx, cy), (max(rgb.shape[1] // 16, 22), max(rgb.shape[0] // 28, 18)), 0, 0, 360, 255, -1)
    return _blend(rgb, color, softened(mask, 39), intensity * 0.42)


def _contour(rgb: np.ndarray, mesh: FaceMesh, color: tuple[int, int, int], intensity: float) -> np.ndarray:
    landmarks = {landmark.index: landmark for landmark in mesh.landmarks}
    mask = np.zeros(rgb.shape[:2], dtype=np.uint8)
    for indices in ((127, 234, 172, 136), (356, 454, 397, 365)):
        if all(index in landmarks for index in indices):
            points = np.array([[landmarks[index].pixelX, landmarks[index].pixelY] for index in indices], dtype=np.int32)
            cv2.fillPoly(mask, [points], 255)
    return _blend(rgb, color, softened(mask, 35), intensity * 0.28)


def _eyeshadow(rgb: np.ndarray, mesh: FaceMesh, color: tuple[int, int, int], intensity: float) -> np.ndarray:
    mask = np.zeros(rgb.shape[:2], dtype=np.uint8)
    for eye in (LEFT_EYE, RIGHT_EYE):
        points = polygon_from_indices(mesh, eye)
        if len(points) >= 3:
            x, y, w, h = cv2.boundingRect(points)
            cv2.ellipse(mask, (x + w // 2, y + h // 2), (max(w // 2, 12), max(h, 10)), 0, 180, 360, 255, -1)
    return _blend(rgb, color, softened(mask, 15), intensity * 0.48)


def _eyeliner(rgb: np.ndarray, mesh: FaceMesh, color: tuple[int, int, int]) -> np.ndarray:
    result = rgb.copy()
    for eye in (LEFT_EYE, RIGHT_EYE):
        points = polygon_from_indices(mesh, eye)
        if len(points) >= 3:
            upper = points[np.argsort(points[:, 1])[: max(4, len(points) // 3)]]
            upper = upper[np.argsort(upper[:, 0])]
            cv2.polylines(result, [upper], False, color, max(rgb.shape[1] // 240, 2), cv2.LINE_AA)
    return result


def _blend(rgb: np.ndarray, color: tuple[int, int, int], mask: np.ndarray, strength: float) -> np.ndarray:
    alpha = (mask.astype(np.float32) / 255.0)[:, :, None] * strength
    overlay = np.zeros_like(rgb, dtype=np.float32)
    overlay[:, :] = color
    blended = rgb.astype(np.float32) * (1 - alpha) + overlay * alpha
    return np.clip(blended, 0, 255).astype(np.uint8)
