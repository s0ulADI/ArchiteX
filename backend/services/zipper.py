from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


def files_to_zip_bytes(files: dict[str, str]) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        for path, content in sorted(files.items()):
            normalized = path.replace("\\", "/").lstrip("/")
            archive.writestr(normalized, content)
    return buffer.getvalue()
