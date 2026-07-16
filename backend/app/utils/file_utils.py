"""File utilities."""

from pathlib import Path
from typing import Optional
import mimetypes


def is_pdf_file(file_path: Path) -> bool:
    """
    Check if file is a PDF.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file is PDF
    """
    if not file_path.exists():
        return False
    
    # Check extension
    if file_path.suffix.lower() != ".pdf":
        return False
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type == "application/pdf":
        return True
    
    # Check magic bytes
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            return header == b"%PDF"
    except Exception:
        return False


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    if not file_path.exists():
        return 0.0
    
    size_bytes = file_path.stat().st_size
    return size_bytes / (1024 * 1024)


def ensure_directory(directory: Path) -> None:
    """
    Ensure directory exists, create if not.
    
    Args:
        directory: Path to directory
    """
    directory.mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    sanitized = filename
    for char in unsafe_chars:
        sanitized = sanitized.replace(char, '_')
    
    return sanitized
