"""Hairstyle try-on rendering."""

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


def prepare_hairstyle_overlay():
    return prepare_asset_overlay("hairstyle")


def render_hairstyle(
    image: DecodedImage,
    mesh: FaceMesh,
    style_id: str,
    option_name: str | None = None,
) -> SalonRenderResult:
    """Align and composite a transparent hairstyle PNG."""

    landmarks = landmark_map(mesh)
    asset = load_asset("hairstyles", style_id)
    left_temple = landmarks[127]
    right_temple = landmarks[356]
    left_eye = landmarks[33]
    right_eye = landmarks[263]
    forehead = landmarks[10]
    chin = landmarks[152]

    face_width = distance(left_temple, right_temple)
    face_height = distance(forehead, chin)
    rotation = angle(left_eye, right_eye)
    target_width = max(int(face_width * _hair_width_factor(style_id)), 96)
    overlay = resize_keep_ratio(asset, target_width)
    overlay = overlay.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)

    center_x = (left_temple.pixelX + right_temple.pixelX) / 2
    top_y = forehead.pixelY - face_height * _hair_top_factor(style_id)
    left = round(center_x - overlay.width / 2)
    top = round(top_y)

    result = composite(image.rgb, overlay, left, top)

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
            "rotationDegrees": round(rotation, 3),
            "faceWidth": round(face_width, 3),
        },
    )


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
