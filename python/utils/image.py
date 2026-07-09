from fastapi import UploadFile


async def validate_image_upload(image: UploadFile) -> bytes:
    data = await image.read()

    if not data:
        raise ValueError("Upload a clear portrait image.")

    if image.content_type and not image.content_type.startswith("image/"):
        raise ValueError("The uploaded file must be an image.")

    return data
