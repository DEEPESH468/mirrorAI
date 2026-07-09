"""Beard try-on rendering."""

from PIL import Image

from python.models.schemas import FaceMesh, SalonRenderResult
from python.vision.utils.assets import (
    angle,
    composite,
    distance,
    landmark_map,
    load_asset,
    prepare_asset_overlay,
    resize_keep_ratio,
)
from python.vision.utils.image import DecodedImage, encode_png_data_url


def prepare_beard_overlay():
    return prepare_asset_overlay("beard")


def render_beard(
    image: DecodedImage,
    mesh: FaceMesh,
    template_id: str,
    option_name: str | None = None,
) -> SalonRenderResult:
    """Align and composite a transparent beard PNG along jaw landmarks."""

    landmarks = landmark_map(mesh)
    asset = load_asset("beards", template_id)
    left_jaw = landmarks[172]
    right_jaw = landmarks[397]
    left_eye = landmarks[33]
    right_eye = landmarks[263]
    mouth_top = landmarks[13]
    chin = landmarks[152]

    jaw_width = distance(left_jaw, right_jaw)
    rotation = angle(left_eye, right_eye)
    target_width = max(int(jaw_width * _beard_width_factor(template_id)), 72)
    overlay = resize_keep_ratio(asset, target_width)
    overlay = overlay.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)

    center_x = (left_jaw.pixelX + right_jaw.pixelX) / 2
    vertical_span = max(chin.pixelY - mouth_top.pixelY, overlay.height)
    left = round(center_x - overlay.width / 2)
    top = round(mouth_top.pixelY - overlay.height * 0.28 + vertical_span * 0.02)

    result = composite(image.rgb, overlay, left, top)

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
            "rotationDegrees": round(rotation, 3),
            "jawWidth": round(jaw_width, 3),
        },
    )


def _beard_width_factor(template_id: str) -> float:
    return {
        "goatee": 0.72,
        "anchor": 0.92,
        "bandholz": 1.24,
    }.get(template_id, 1.0)
