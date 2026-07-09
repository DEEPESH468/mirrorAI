"""Shared transparent PNG asset helpers.

Domain renderers in hair and beard use these helpers to scale, rotate, and
composite transparent PNG assets onto uploaded portraits.
"""

from math import atan2, degrees, hypot
from pathlib import Path

import numpy as np
from PIL import Image

from python.models.schemas import AiModuleResult, FaceMesh


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = PROJECT_ROOT / "public" / "assets" / "salon"


class AssetOverlayError(ValueError):
    """Raised when a hairstyle or beard asset cannot be aligned."""


def prepare_asset_overlay(kind: str) -> AiModuleResult:
    return AiModuleResult(
        module=kind,
        status="completed",
        message=f"{kind.title()} transparent PNG asset aligned with local face landmarks.",
    )


def load_asset(group: str, asset_id: str) -> Image.Image:
    asset_path = ASSET_ROOT / group / f"{asset_id}.png"
    fallback_path = ASSET_ROOT / group / "default.png"
    path = asset_path if asset_path.exists() else fallback_path

    if not path.exists():
        raise AssetOverlayError(f"Missing transparent PNG asset for {group}/{asset_id}.")

    return Image.open(path).convert("RGBA")


def resize_keep_ratio(asset: Image.Image, target_width: int) -> Image.Image:
    ratio = target_width / asset.width
    target_height = max(int(asset.height * ratio), 1)
    return asset.resize((target_width, target_height), Image.Resampling.LANCZOS)


def composite(rgb_image: np.ndarray, overlay: Image.Image, left: int, top: int) -> np.ndarray:
    base = Image.fromarray(rgb_image).convert("RGBA")
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.alpha_composite(overlay, (left, top))
    merged = Image.alpha_composite(base, layer).convert("RGB")
    return np.asarray(merged)


def landmark_map(mesh: FaceMesh):
    landmarks = {landmark.index: landmark for landmark in mesh.landmarks}
    required = (10, 13, 33, 127, 152, 172, 263, 356, 397)
    missing = [index for index in required if index not in landmarks]

    if missing:
        raise AssetOverlayError(f"Missing required face landmarks: {missing}.")

    return landmarks


def distance(first, second) -> float:
    return hypot(first.pixelX - second.pixelX, first.pixelY - second.pixelY)


def angle(first, second) -> float:
    return degrees(atan2(second.pixelY - first.pixelY, second.pixelX - first.pixelX))
