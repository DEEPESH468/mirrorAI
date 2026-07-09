"""Local cosmetic skin analysis service.

The service uses OpenCV measurements inside the MediaPipe face mask. It is a
best-effort salon consultation aid and does not provide medical diagnosis.
"""

import cv2
import numpy as np

from python.models.schemas import AiModuleResult, FaceMesh, SkinAnalysisResult, SkinConcern
from python.vision.utils.landmarks import LEFT_EYE, RIGHT_EYE, bbox, face_mask, level, polygon_from_indices
from python.vision.utils.image import DecodedImage


DISCLAIMER = (
    "Cosmetic best-effort analysis only. Results are affected by lighting, camera quality, "
    "makeup, and pose, and are not medical advice."
)


def skin_module_result() -> AiModuleResult:
    return AiModuleResult(
        module="skin",
        status="completed",
        message="Cosmetic skin tone, redness, texture, oiliness, dark-circle, and spot analysis completed locally.",
    )


def analyze_skin(image: DecodedImage, mesh: FaceMesh) -> SkinAnalysisResult:
    """Estimate visible cosmetic skin attributes from the face region."""

    rgb = image.rgb
    height, width = rgb.shape[:2]
    mask = face_mask((height, width), mesh)
    skin_pixels = rgb[mask > 0]
    if skin_pixels.size == 0:
        raise ValueError("Skin region could not be estimated from this portrait.")

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    tone_rgb = np.median(skin_pixels, axis=0).astype(int)
    tone_luma = float(0.2126 * tone_rgb[0] + 0.7152 * tone_rgb[1] + 0.0722 * tone_rgb[2])
    tone_label = _tone_label(tone_luma)

    red_excess = np.maximum(rgb[:, :, 0].astype(np.int16) - ((rgb[:, :, 1].astype(np.int16) + rgb[:, :, 2].astype(np.int16)) // 2), 0)
    redness_score = _masked_mean(red_excess, mask) / 72.0

    spot_mask = np.where((red_excess > 28) & (hsv[:, :, 1] > 45) & (mask > 0), 255, 0).astype(np.uint8)
    spot_mask = cv2.morphologyEx(spot_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(spot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    spot_count = sum(1 for contour in contours if 6 <= cv2.contourArea(contour) <= 260)
    acne_score = min(1.0, spot_count / 18.0)

    wrinkle_score = _wrinkle_score(gray, mask, mesh)
    dark_circle_score = _dark_circle_score(lab, mesh, width, height)

    value = hsv[:, :, 2]
    saturation = hsv[:, :, 1]
    t_zone = _t_zone_mask(mask, mesh, width, height)
    shine = np.where((value > 188) & (saturation < 72) & (t_zone > 0), 255, 0).astype(np.uint8)
    oiliness_score = min(1.0, np.count_nonzero(shine) / max(np.count_nonzero(t_zone) * 0.18, 1))

    confidence = float(np.clip(0.58 + np.count_nonzero(mask) / max(width * height, 1), 0.58, 0.9))

    return SkinAnalysisResult(
        acne=_concern(acne_score, 0.68),
        wrinkles=_concern(wrinkle_score, 0.62),
        darkCircles=_concern(dark_circle_score, 0.64),
        redness=_concern(redness_score, 0.66),
        oiliness=_concern(oiliness_score, 0.6),
        skinTone=tone_label,
        toneRgb={"r": int(tone_rgb[0]), "g": int(tone_rgb[1]), "b": int(tone_rgb[2])},
        confidence=round(confidence, 4),
        disclaimer=DISCLAIMER,
    )


def _concern(score: float, confidence: float) -> SkinConcern:
    bounded = float(np.clip(score, 0, 1))
    return SkinConcern(
        level=level(bounded),
        score=round(bounded, 4),
        confidence=round(confidence, 4),
    )


def _masked_mean(channel: np.ndarray, mask: np.ndarray) -> float:
    values = channel[mask > 0]
    return float(values.mean()) if values.size else 0.0


def _tone_label(luma: float) -> str:
    if luma >= 205:
        return "fair"
    if luma >= 170:
        return "light"
    if luma >= 130:
        return "medium"
    if luma >= 92:
        return "tan"
    return "deep"


def _wrinkle_score(gray: np.ndarray, mask: np.ndarray, mesh: FaceMesh) -> float:
    points = polygon_from_indices(mesh, (67, 109, 10, 338, 297, 332, 333, 299, 69, 104))
    if len(points) < 3:
        region = mask
    else:
        region = np.zeros_like(mask)
        cv2.fillPoly(region, [points], 255)
        region = cv2.bitwise_and(region, mask)

    edges = cv2.Canny(cv2.bitwise_and(gray, gray, mask=region), 38, 105)
    line_density = np.count_nonzero(edges) / max(np.count_nonzero(region), 1)
    texture = cv2.Laplacian(cv2.bitwise_and(gray, gray, mask=region), cv2.CV_64F).var() / 900.0
    return float(np.clip(line_density * 12.0 + texture * 0.12, 0, 1))


def _dark_circle_score(lab: np.ndarray, mesh: FaceMesh, width: int, height: int) -> float:
    left = polygon_from_indices(mesh, LEFT_EYE)
    right = polygon_from_indices(mesh, RIGHT_EYE)
    if len(left) < 3 or len(right) < 3:
        return 0.0

    scores = []
    for eye in (left, right):
        x0, y0, x1, y1 = bbox(eye, 10, width, height)
        eye_height = max(y1 - y0, 1)
        under_y0 = min(y1, height - 1)
        under_y1 = min(y1 + eye_height, height)
        cheek_y0 = min(under_y1 + eye_height, height - 1)
        cheek_y1 = min(cheek_y0 + eye_height, height)
        if under_y1 <= under_y0 or cheek_y1 <= cheek_y0:
            continue
        under_l = lab[under_y0:under_y1, x0:x1, 0].mean()
        cheek_l = lab[cheek_y0:cheek_y1, x0:x1, 0].mean()
        scores.append(max(0.0, (cheek_l - under_l) / 42.0))
    return float(np.clip(np.mean(scores) if scores else 0.0, 0, 1))


def _t_zone_mask(face: np.ndarray, mesh: FaceMesh, width: int, height: int) -> np.ndarray:
    landmarks = {landmark.index: landmark for landmark in mesh.landmarks}
    if not all(index in landmarks for index in (9, 168, 2, 10, 152)):
        return face
    center_x = landmarks[168].pixelX
    top_y = landmarks[10].pixelY
    bottom_y = landmarks[2].pixelY
    half_width = max(int(width * 0.055), 16)
    mask = np.zeros_like(face)
    cv2.rectangle(
        mask,
        (max(center_x - half_width, 0), max(top_y, 0)),
        (min(center_x + half_width, width - 1), min(bottom_y + int(height * 0.08), height - 1)),
        255,
        -1,
    )
    return cv2.bitwise_and(mask, face)
