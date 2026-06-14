import base64

from fastapi import UploadFile


SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


async def read_image_bytes(image: UploadFile) -> tuple[bytes, str]:
    mime_type = image.content_type or "application/octet-stream"
    data = await image.read()
    if mime_type not in SUPPORTED_IMAGE_TYPES:
        raise ValueError("Only jpg, png, and webp images are supported")
    if not data:
        raise ValueError("Uploaded image is empty")
    return data, mime_type


def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")
