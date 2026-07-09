"""Image validation and decoding helpers for the local AI backend.

The functions in this module keep HTTP upload validation separate from AI
services. They accept only image uploads, cap payload size, and decode the file
into RGB arrays that OpenCV, MediaPipe, InsightFace, ONNX Runtime, and SAM-based
modules can share later.
"""

from dataclasses import dataclass
from io import BytesIO

import cv2
import numpy as np
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError


MAX_IMAGE_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class DecodedImage:
    data: bytes
    rgb: np.ndarray
    width: int
    height: int
    content_type: str | None


async def validate_image_upload(image: UploadFile) -> bytes:
    data = await image.read()

    if not data:
        raise ValueError("Upload a clear portrait image.")

    if image.content_type and not image.content_type.startswith("image/"):
        raise ValueError("The uploaded file must be an image.")

    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError("Upload an image smaller than 10 MB.")

    return data


async def decode_image_upload(image: UploadFile) -> DecodedImage:
    data = await validate_image_upload(image)

    try:
        with Image.open(BytesIO(data)) as pil_image:
            pil_image.verify()
    except UnidentifiedImageError as exc:
        raise ValueError("The uploaded file could not be decoded as an image.") from exc

    encoded = np.frombuffer(data, dtype=np.uint8)
    bgr = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

    if bgr is None:
        raise ValueError("The uploaded file could not be decoded as an image.")

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    height, width = rgb.shape[:2]

    if width < 128 or height < 128:
        raise ValueError("Upload a portrait image that is at least 128px by 128px.")

    return DecodedImage(
        data=data,
        rgb=rgb,
        width=width,
        height=height,
        content_type=image.content_type,
    )
