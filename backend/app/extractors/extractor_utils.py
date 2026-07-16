"""Shared utilities for extractors to avoid code duplication."""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

from loguru import logger
from app.core.config import settings


def create_timestamped_output_directory(library_name: str, pdf_path: Path) -> Path:
    """
    Create timestamped output directory for extraction results.
    
    Args:
        library_name: Name of the extraction library
        pdf_path: Path to PDF file (not used currently, for future extensions)
        
    Returns:
        Path to output directory: results/{timestamp}/{library_name}/
    """
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    
    # Create directory structure: results/{timestamp}/{library_name}/
    output_dir = Path(settings.results_dir) / timestamp / library_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


def save_text_file(file_path: Path, content: str) -> None:
    """
    Save text content to file.
    
    Args:
        file_path: Path to save file
        content: Text content to save
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save text file {file_path}: {e}")


def save_json_file(file_path: Path, data: Any) -> None:
    """
    Save data as JSON file.
    
    Args:
        file_path: Path to save file
        data: Data to save as JSON
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save JSON file {file_path}: {e}")


def get_library_version(module_name: str) -> str:
    """
    Get version of an installed library.
    
    Args:
        module_name: Name of the module to check
        
    Returns:
        Version string or "unknown"
    """
    try:
        module = __import__(module_name)
        return getattr(module, "__version__", "unknown")
    except Exception:
        return "unknown"


def count_images_in_directory(images_dir: Path) -> int:
    """
    Count image files in a directory.
    
    Args:
        images_dir: Directory to scan for images
        
    Returns:
        Number of image files found
    """
    try:
        if not images_dir.exists():
            return 0
        
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
        image_count = sum(
            1 for f in images_dir.iterdir() 
            if f.is_file() and f.suffix.lower() in image_extensions
        )
        
        return image_count
        
    except Exception as e:
        logger.error(f"Error counting images: {e}")
        return 0


def create_extraction_summary(
    library_name: str,
    markdown_text: str,
    images_count: int,
    tables_count: int,
    pages_count: int = 0,
    additional_stats: Dict[str, Any] = None,
    output_files: Dict[str, str] = None,
) -> Dict[str, Any]:
    """
    Create standardized extraction summary.
    
    Args:
        library_name: Name of extraction library
        markdown_text: Extracted markdown text
        images_count: Number of images extracted
        tables_count: Number of tables extracted
        pages_count: Number of pages processed
        additional_stats: Additional statistics to include
        output_files: Dictionary of output file descriptions
        
    Returns:
        Summary dictionary
    """
    summary = {
        "extractor": library_name,
        "extraction_time": datetime.now().isoformat(),
        "statistics": {
            "text_length": len(markdown_text),
            "word_count": len(markdown_text.split()),
            "line_count": len(markdown_text.split('\n')),
            "images_extracted": images_count,
            "tables_extracted": tables_count,
        },
        "outputs": output_files or {},
    }
    
    # Add page count if provided
    if pages_count > 0:
        summary["statistics"]["pages"] = pages_count
    
    # Merge additional statistics
    if additional_stats:
        summary["statistics"].update(additional_stats)
    
    # Add status
    summary["status"] = "success"
    summary["errors"] = []
    
    return summary
