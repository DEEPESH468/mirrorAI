"""Transparent PNG asset alignment and compositing services.

Hairstyle and beard try-ons use transparent PNG assets. The assets are scaled,
rotated, and positioned from MediaPipe Face Mesh landmarks, then composited onto
the uploaded portrait with Pillow. No generated imagery or remote services are
used.
"""

from math import atan2, degrees, hypot
from pathlib import Path

import numpy as np
from PIL import Image

from python.models.schemas import AiModuleResult
from python.models.schemas import FaceMesh, SalonRenderResult
from python.utils.image import DecodedImage, encode_png_data_url


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSET_ROOT = PROJECT_ROOT / "public" / "assets" / "salon"


class AssetOverlayError(ValueError):
    """Raised when a hairstyle or beard asset cannot be aligned."""


def prepare_asset_overlay(kind: str) -> AiModuleResult:
    return AiModuleResult(
        module=kind,
        status="completed",
        message=f"{kind.title()} transparent PNG asset aligned with local face landmarks.",
    )


def render_hairstyle(
    image: DecodedImage,
    mesh: FaceMesh,
    style_id: str,
    option_name: str | None = None,
) -> SalonRenderResult:
    """Align and composite a transparent hairstyle PNG."""

    landmarks = _landmark_map(mesh)
    asset = _load_asset("hairstyles", style_id)
    left_temple = landmarks[127]
    right_temple = landmarks[356]
    left_eye = landmarks[33]
    right_eye = landmarks[263]
    forehead = landmarks[10]
    chin = landmarks[152]

    face_width = _distance(left_temple, right_temple)
    face_height = _distance(forehead, chin)
    angle = _angle(left_eye, right_eye)
    target_width = max(int(face_width * _hair_width_factor(style_id)), 96)
    overlay = _resize_keep_ratio(asset, target_width)
    overlay = overlay.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

    center_x = (left_temple.pixelX + right_temple.pixelX) / 2
    top_y = forehead.pixelY - face_height * _hair_top_factor(style_id)
    left = round(center_x - overlay.width / 2)
    top = round(top_y)

    result = _composite(image.rgb, overlay, left, top)

    return SalonRenderResult(
        kind="hairstyle",
        optionId=style_id,
        optionName=option_name,
        imageBase64=encode_png_data_url(result),
        width=image.width,
        height=image.height,
        transform={
            "asset": style_id,
            "x": left,
            "y": top,
            "width": overlay.width,
            "height": overlay.height,
            "rotationDegrees": round(angle, 3),
            "faceWidth": round(face_width, 3),
        },
    )


def render_beard(
    image: DecodedImage,
    mesh: FaceMesh,
    template_id: str,
    option_name: str | None = None,
) -> SalonRenderResult:
    """Align and composite a transparent beard PNG along jaw landmarks."""

    landmarks = _landmark_map(mesh)
    asset = _load_asset("beards", template_id)
    left_jaw = landmarks[172]
    right_jaw = landmarks[397]
    left_eye = landmarks[33]
    right_eye = landmarks[263]
    mouth_top = landmarks[13]
    chin = landmarks[152]

    jaw_width = _distance(left_jaw, right_jaw)
    angle = _angle(left_eye, right_eye)
    target_width = max(int(jaw_width * _beard_width_factor(template_id)), 72)
    overlay = _resize_keep_ratio(asset, target_width)
    overlay = overlay.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

    center_x = (left_jaw.pixelX + right_jaw.pixelX) / 2
    vertical_span = max(chin.pixelY - mouth_top.pixelY, overlay.height)
    left = round(center_x - overlay.width / 2)
    top = round(mouth_top.pixelY - overlay.height * 0.28 + vertical_span * 0.02)

    result = _composite(image.rgb, overlay, left, top)

    return SalonRenderResult(
        kind="beard",
        optionId=template_id,
        optionName=option_name,
        imageBase64=encode_png_data_url(result),
        width=image.width,
        height=image.height,
        transform={
            "asset": template_id,
            "x": left,
            "y": top,
            "width": overlay.width,
            "height": overlay.height,
            "rotationDegrees": round(angle, 3),
            "jawWidth": round(jaw_width, 3),
        },
    )


def _load_asset(group: str, asset_id: str) -> Image.Image:
    asset_path = ASSET_ROOT / group / f"{asset_id}.png"
    fallback_path = ASSET_ROOT / group / "default.png"
    path = asset_path if asset_path.exists() else fallback_path

    if not path.exists():
        raise AssetOverlayError(f"Missing transparent PNG asset for {group}/{asset_id}.")

    return Image.open(path).convert("RGBA")


def _resize_keep_ratio(asset: Image.Image, target_width: int) -> Image.Image:
    ratio = target_width / asset.width
    target_height = max(int(asset.height * ratio), 1)
    return asset.resize((target_width, target_height), Image.Resampling.LANCZOS)


def _composite(rgb_image: np.ndarray, overlay: Image.Image, left: int, top: int) -> np.ndarray:
    base = Image.fromarray(rgb_image).convert("RGBA")
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.alpha_composite(overlay, (left, top))
    merged = Image.alpha_composite(base, layer).convert("RGB")
    return np.asarray(merged)


def _landmark_map(mesh: FaceMesh):
    landmarks = {landmark.index: landmark for landmark in mesh.landmarks}
    required = (10, 13, 33, 127, 152, 172, 263, 356, 397)
    missing = [index for index in required if index not in landmarks]

    if missing:
        raise AssetOverlayError(f"Missing required face landmarks: {missing}.")

    return landmarks


def _distance(first, second) -> float:
    return hypot(first.pixelX - second.pixelX, first.pixelY - second.pixelY)


def _angle(first, second) -> float:
    return degrees(atan2(second.pixelY - first.pixelY, second.pixelX - first.pixelX))


def _hair_width_factor(style_id: str) -> float:
    return {
        "buzzcut": 1.35,
        "crewcut": 1.48,
        "curtain": 1.68,
    }.get(style_id, 1.55)


def _hair_top_factor(style_id: str) -> float:
    return {
        "buzzcut": 0.24,
        "crewcut": 0.31,
        "curtain": 0.38,
    }.get(style_id, 0.34)


def _beard_width_factor(template_id: str) -> float:
    return {
        "goatee": 0.72,
        "anchor": 0.92,
        "bandholz": 1.24,
    }.get(template_id, 1.0)
