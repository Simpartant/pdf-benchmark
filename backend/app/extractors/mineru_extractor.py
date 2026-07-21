"""MinerU extractor implementation (normalized interface).

Supports two distribution packages:
  - `magic-pdf` (legacy, Python 3.9+ but prebuilt binaries may fail)
  - `mineru` (current, Python 3.10+)

Detection resolves the actual CLI from installed console_scripts metadata
rather than guessing names.
"""

import json
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from importlib.metadata import entry_points as metadata_entry_points

from loguru import logger

from app.extractors.base_extractor import BaseExtractor
from app.models.extraction_result import ExtractionResult
from app.extractors.extractor_utils import (
    save_text_file,
    save_json_file,
    create_extraction_summary,
)


class MinerUExtractor(BaseExtractor):
    """
    MinerU PDF extraction implementation.

    Extracts PDF content to markdown, JSON, and images using the official
    MinerU CLI. Requires the `mineru` package (Python 3.10+) or
    `magic-pdf` package (Python 3.9+).
    """

    library_id = "mineru"
    display_name = "MinerU"
    description = "High-accuracy PDF parsing with layout analysis and OCR support"
    capabilities = [
        "text_extraction",
        "markdown_export",
        "json_export",
        "image_extraction",
        "table_extraction",
        "layout_analysis",
        "ocr_support",
        "metadata_extraction",
    ]
    performance_notes = "Requires Python 3.10+ for full support; package detected but CLI may be unavailable on Python 3.9"
    required_modules = ["magic_pdf", "mineru"]

    # Default timeout in seconds
    DEFAULT_TIMEOUT = 300

    def __init__(self):
        super().__init__()
        self._python_version_info = sys.version_info
        self._python_version_str = f"{self._python_version_info.major}.{self._python_version_info.minor}.{self._python_version_info.micro}"
        self._module_available = self._check_module_available()
        self._cli_info = self._resolve_cli()
        self._runtime_usable = self._check_runtime_usable()

    def _check_module_available(self) -> bool:
        """Check if any of the MinerU modules are available."""
        for module in self.required_modules:
            try:
                __import__(module)
                return True
            except ImportError:
                continue
        return False

    def _check_runtime_usable(self) -> bool:
        """
        Check if MinerU is actually usable from this Python environment.
        The magic-pdf CLI uses Python 3.10+ syntax (list[X | Y], etc.)
        and will crash on Python < 3.10.
        """
        if not self._module_available:
            return False

        # magic-pdf 1.3.0 uses Python 3.10+ union syntax in CLI code
        if self._python_version_info < (3, 10):
            # Check if we can at least import the module without crashing
            try:
                import magic_pdf
                return False  # Module exists but CLI/tools won't work
            except Exception:
                return False

        return True

    def _find_console_scripts(self) -> List[Tuple[str, str]]:
        """
        Find all console_scripts registered by mineru / magic-pdf packages.
        Returns list of (name, value) pairs.
        """
        scripts = []
        try:
            # Python 3.9 compatibility
            eps = metadata_entry_points()
            for ep in eps:
                if hasattr(ep, 'group') and ep.group == 'console_scripts':
                    if 'mineru' in ep.name.lower() or 'magic' in ep.name.lower():
                        scripts.append((ep.name, ep.value))
        except Exception:
            pass
        return scripts

    def _resolve_cli(self) -> Dict[str, Any]:
        """
        Resolve the mineru CLI path using multiple strategies.

        Returns:
            Dict with keys: path (str|None), name (str), scripts (list), diagnostics (list)
        """
        info: Dict[str, Any] = {
            "path": None,
            "name": None,
            "scripts": [],
            "diagnostics": [],
        }

        # 1) Check console_scripts from installed package metadata
        scripts = self._find_console_scripts()
        info["scripts"] = scripts
        for name, _ in scripts:
            cli_path = shutil.which(name)
            if cli_path:
                info["path"] = cli_path
                info["name"] = name
                return info

        # 2) Check PATH for expected names
        for name in ["mineru", "magic-pdf", "magic-pdf-dev"]:
            cli_path = shutil.which(name)
            if cli_path:
                info["path"] = cli_path
                info["name"] = name
                return info

        # 3) Check in the venv bin directory
        bin_dir = Path(sys.executable).parent
        for name in ["mineru", "magic-pdf", "magic-pdf-dev"]:
            candidate = bin_dir / name
            if candidate.exists():
                info["path"] = str(candidate)
                info["name"] = name
                return info

        # No CLI found – collect diagnostics
        info["diagnostics"].append(f"Python {self._python_version_str} (active: {sys.executable})")
        info["diagnostics"].append(f"Prefix: {sys.prefix}")
        if self._module_available:
            info["diagnostics"].append("Package detected but no usable console script in PATH or venv bin")
            if self._python_version_info < (3, 10):
                info["diagnostics"].append(
                    "magic-pdf 1.3.0 tools require Python 3.10+ "
                    "(uses `list[bytes | Dataset]` union syntax not supported on this Python)"
                )
        else:
            info["diagnostics"].append("MinerU package not installed")

        return info

    def is_available(self) -> bool:
        """MinerU is available only when module exists AND CLI is resolvable AND runtime is usable."""
        return self._module_available and self._cli_info["path"] is not None and self._runtime_usable

    def get_version(self) -> str:
        """Get the version from the available module or package metadata."""
        import importlib.metadata as metadata

        for module in self.required_modules:
            try:
                mod = __import__(module)
                version = getattr(mod, "__version__", None)
                if version:
                    return str(version)
            except ImportError:
                continue

        for package in ["magic-pdf", "mineru"]:
            try:
                return metadata.version(package)
            except Exception:
                continue
        return "unknown"

    def get_info(self) -> "ExtractorInfo":
        """Detailed status including Python version, module, and CLI diagnostics."""
        from app.extractors.base_extractor import ExtractorInfo, AvailabilityStatus, DependencyDiagnostic

        deps: List[DependencyDiagnostic] = []
        diags: List[str] = []

        # Dependency: module
        for module in self.required_modules:
            try:
                mod = __import__(module)
                version = getattr(mod, "__version__", "unknown")
                deps.append(DependencyDiagnostic(
                    name=module, module=module, installed=True, version=version,
                ))
            except ImportError:
                deps.append(DependencyDiagnostic(
                    name=module, module=module, installed=False, error="Module not found",
                ))

        # Diagnostics from CLI resolution
        if self._cli_info["diagnostics"]:
            diags.extend(self._cli_info["diagnostics"])

        # Determine status
        if self._module_available and self._cli_info["path"] and self._runtime_usable:
            status = AvailabilityStatus.AVAILABLE
        elif self._module_available and not self._runtime_usable:
            status = AvailabilityStatus.ERROR
            diags.insert(0, f"Python {self._python_version_str} does not meet the >=3.10 requirement")
        elif self._module_available and not self._cli_info["path"]:
            status = AvailabilityStatus.ERROR
            if not any("console script" in d for d in diags):
                diags.insert(0, "No usable CLI found")
        else:
            status = AvailabilityStatus.NOT_INSTALLED

        return ExtractorInfo(
            library_id=self.library_id,
            display_name=self.display_name,
            version=self.get_version(),
            status=status,
            description=self.description,
            capabilities=self.capabilities,
            performance_notes=self.performance_notes,
            dependencies=deps,
            diagnostics=diags,
        )

    def extract(
        self,
        pdf_path: Path,
        output_dir: Path,
        options: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """Extract PDF with MinerU into a normalized ExtractionResult."""
        self.validate_pdf(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not self._module_available:
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error="MinerU package not installed. Install with: pip install magic-pdf",
                output_files={},
            )

        if not self._runtime_usable:
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error=(
                    f"MinerU requires Python 3.10+ for its toolchain. "
                    f"Active Python is {self._python_version_str} ({sys.executable}). "
                    f"Install with a Python 3.10+ environment."
                ),
                output_files={},
            )

        cli_path = self._cli_info.get("path")
        if not cli_path:
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error="MinerU CLI not found. The installed package has no usable console script.",
                output_files={},
            )

        # Get options
        backend = (options or {}).get("backend", "pipeline")
        timeout = (options or {}).get("timeout", self.DEFAULT_TIMEOUT)

        try:
            method = "auto" if backend == "pipeline" else backend
            model_mode = (options or {}).get("model_mode", "lite")
            logger.info(f"Running MinerU CLI: {cli_path} pdf --pdf {pdf_path} --method {method} --inside_model true --model_mode {model_mode}")

            cmd = [
                cli_path,
                "pdf",
                "--pdf", str(pdf_path),
                "--method", method,
                "--inside_model", "true",
                "--model_mode", model_mode,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(output_dir),
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or f"Exit code: {result.returncode}"
                return ExtractionResult(
                    library=self.library_id,
                    library_version=self.get_version(),
                    original_filename=pdf_path.name,
                    status="failed",
                    error=f"MinerU CLI failed: {error_msg.strip()}",
                    output_files={},
                )

            # Load the generated outputs
            output_files = self._load_outputs(output_dir)
            markdown_text = self._read_markdown(output_dir)
            json_data = self._read_json(output_dir)
            page_count, table_count, image_count = self._extract_metrics(json_data)

            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="success",
                markdown=markdown_text,
                structured_json={"mineru": json_data} if json_data else None,
                metadata={"extractor": self.library_id, "backend": backend, "cli": cli_path},
                page_count=page_count,
                table_count=table_count,
                image_count=image_count,
                output_files=output_files,
            )

        except subprocess.TimeoutExpired:
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error=f"MinerU extraction timed out after {timeout} seconds",
                output_files={},
            )
        except Exception as e:
            logger.exception(f"MinerU extraction failed: {e}")
            return ExtractionResult(
                library=self.library_id,
                library_version=self.get_version(),
                original_filename=pdf_path.name,
                status="failed",
                error=str(e),
                output_files={},
            )

    def _load_outputs(self, output_dir: Path) -> Dict[str, Any]:
        """Load paths to generated output files."""
        output_files: Dict[str, Any] = {}
        for ext, key in [(".md", "markdown"), (".json", "json")]:
            for f in output_dir.glob(f"*{ext}"):
                if "metadata" not in f.name.lower() and "summary" not in f.name.lower():
                    output_files[key] = str(f)
        return output_files

    def _read_markdown(self, output_dir: Path) -> str:
        """Read the generated markdown file."""
        for f in output_dir.glob("*.md"):
            if "metadata" not in f.name.lower() and "summary" not in f.name.lower():
                with open(f, "r", encoding="utf-8") as mf:
                    return mf.read()
        return ""

    def _read_json(self, output_dir: Path) -> Dict[str, Any]:
        """Read the generated JSON file."""
        for f in output_dir.glob("*.json"):
            if "metadata" not in f.name.lower() and "summary" not in f.name.lower():
                with open(f, "r", encoding="utf-8") as jf:
                    return json.load(jf)
        return {}

    def _extract_metrics(self, json_data: Dict[str, Any]) -> Tuple[int, int, int]:
        """Extract page count, table count, and image count from MinerU JSON."""
        pages = set()
        table_count = 0
        image_count = 0

        for item in json_data if isinstance(json_data, list) else json_data.get("elements", []):
            if isinstance(item, dict):
                if "page" in item:
                    pages.add(item["page"])
                item_type = item.get("type", "").lower()
                if item_type == "table":
                    table_count += 1
                elif item_type == "image":
                    image_count += 1

        return len(pages), table_count, image_count

    def _save_outputs(
        self,
        output_dir: Path,
        documents: list,
        markdown_text: str,
        json_structure: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Save additional metadata and summary files."""
        output_files: Dict[str, Any] = {}
        try:
            metadata_file = output_dir / "metadata.json"
            save_json_file(
                metadata_file,
                {"extractor": self.library_id, "total_documents": len(documents)},
            )
            output_files["metadata"] = str(metadata_file)

            summary_file = output_dir / "summary.json"
            save_json_file(
                summary_file,
                create_extraction_summary(
                    library_name=self.library_id,
                    markdown_text=markdown_text,
                    images_count=0,
                    tables_count=0,
                    pages_count=0,
                    output_files=output_files,
                ),
            )
            output_files["summary"] = str(summary_file)
        except Exception as e:
            logger.error(f"Error saving MinerU outputs: {e}")
        return output_files