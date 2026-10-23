from pathlib import Path

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_file_extension(filename: str) -> bool:
    extension = Path(filename).suffix.lower()
    return extension in ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    return 0 <= file_size <= MAX_FILE_SIZE
