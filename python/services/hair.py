"""Hair analysis, color, and local simulation services.

Hair color simulation uses an OpenCV mask derived from face landmarks and
upper-head geometry. The output preserves luminance texture while blending a
target salon shade onto likely hair pixels.
"""

import cv2
import numpy as np

from python.models.schemas import AiModuleResult
from python.models.schemas import FaceMesh, HairColorId, SalonRenderResult
from python.utils.image import DecodedImage, encode_png_data_url


HAIR_COLORS: dict[str, tuple[int, int, int]] = {
    "black": (24, 20, 18),
    "brown": (92, 56, 36),
    "golden": (191, 142, 52),
    "blonde": (218, 190, 123),
    "silver": (190, 194, 198),
    "red": (156, 45, 38),
    "blue": (42, 82, 168),
}


class HairColorError(ValueError):
    """Raised when hair color simulation cannot be completed."""


def analyze_hair() -> AiModuleResult:
    return AiModuleResult(
        module="hair",
        status="completed",
        message="Hair color masking and salon simulation modules are available locally.",
    )


def simulate_hair_color(
    image: DecodedImage,
    mesh: FaceMesh,
    color_id: str,
    option_name: str | None = None,
) -> SalonRenderResult:
    """Apply a supported hair color using OpenCV masking."""

    if color_id not in HAIR_COLORS:
        raise HairColorError(
            "Unsupported hair color. Choose black, brown, golden, blonde, silver, red, or blue."
        )

    mask = _build_hair_region_mask(image.rgb, mesh)
    if int(np.count_nonzero(mask)) < 128:
        raise HairColorError("Hair region could not be estimated from this portrait.")

    result = _blend_color(image.rgb, mask, HAIR_COLORS[color_id])

    return SalonRenderResult(
        kind="hair-color",
        optionId=color_id,
        optionName=option_name,
        imageBase64=encode_png_data_url(result),
        width=image.width,
        height=image.height,
        transform={
            "color": color_id,
            "maskPixels": int(np.count_nonzero(mask)),
            "blendStrength": 0.62,
        },
    )


def _build_hair_region_mask(rgb_image: np.ndarray, mesh: FaceMesh) -> np.ndarray:
    height, width = rgb_image.shape[:2]
    landmarks = {landmark.index: landmark for landmark in mesh.landmarks}
    required = (10, 33, 127, 152, 234, 263, 356, 454)
    if any(index not in landmarks for index in required):
        raise HairColorError("Missing face landmarks for hair color simulation.")

    left = min(landmarks[127].pixelX, landmarks[234].pixelX)
    right = max(landmarks[356].pixelX, landmarks[454].pixelX)
    forehead_y = landmarks[10].pixelY
    chin_y = landmarks[152].pixelY
    face_height = max(chin_y - forehead_y, 1)
    face_width = max(right - left, 1)

    x_min = max(int(left - face_width * 0.32), 0)
    x_max = min(int(right + face_width * 0.32), width - 1)
    y_min = max(int(forehead_y - face_height * 0.55), 0)
    y_max = min(int(forehead_y + face_height * 0.28), height - 1)

    region_mask = np.zeros((height, width), dtype=np.uint8)
    polygon = np.array(
        [
            [x_min, y_max],
            [x_min + int(face_width * 0.08), y_min + int(face_height * 0.2)],
            [int((x_min + x_max) / 2), y_min],
            [x_max - int(face_width * 0.08), y_min + int(face_height * 0.2)],
            [x_max, y_max],
        ],
        dtype=np.int32,
    )
    cv2.fillConvexPoly(region_mask, polygon, 255)

    hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    candidate = np.where(((saturation > 22) | (value < 145)) & (value < 245), 255, 0).astype(np.uint8)
    mask = cv2.bitwise_and(region_mask, candidate)

    kernel = np.ones((9, 9), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.GaussianBlur(mask, (15, 15), 0)
    return mask


def _blend_color(rgb_image: np.ndarray, mask: np.ndarray, target_rgb: tuple[int, int, int]) -> np.ndarray:
    alpha = (mask.astype(np.float32) / 255.0)[:, :, None] * 0.62
    target = np.zeros_like(rgb_image, dtype=np.float32)
    target[:, :] = target_rgb

    hsv_original = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv_target = cv2.cvtColor(np.uint8([[target_rgb]]), cv2.COLOR_RGB2HSV).astype(np.float32)[0, 0]
    recolored_hsv = hsv_original.copy()
    recolored_hsv[:, :, 0] = hsv_target[0]
    recolored_hsv[:, :, 1] = np.clip(hsv_original[:, :, 1] * 0.45 + hsv_target[1] * 0.75, 0, 255)
    recolored = cv2.cvtColor(recolored_hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    blended = rgb_image.astype(np.float32) * (1 - alpha) + recolored * alpha
    return np.clip(blended, 0, 255).astype(np.uint8)
