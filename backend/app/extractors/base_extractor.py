"""Base extractor abstract class with a normalized interface.

Every PDF extraction library (docling, unstructured, mineru, ...)
implements this single interface so the rest of the
application can treat them uniformly through the extractor registry.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models.extraction_result import ExtractionResult


class AvailabilityStatus(str, Enum):
    """Availability state of an extraction library."""

    AVAILABLE = "available"
    NOT_INSTALLED = "not_installed"
    ERROR = "error"


@dataclass
class DependencyDiagnostic:
    """Diagnostic information about a single dependency."""

    name: str
    module: str
    installed: bool
    version: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ExtractorInfo:
    """Static metadata describing an extractor."""

    library_id: str
    display_name: str
    version: str = "unknown"
    status: AvailabilityStatus = AvailabilityStatus.NOT_INSTALLED
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    performance_notes: str = ""
    dependencies: List[DependencyDiagnostic] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "libraryId": self.library_id,
            "displayName": self.display_name,
            "version": self.version,
            "status": self.status.value,
            "description": self.description,
            "capabilities": self.capabilities,
            "performanceNotes": self.performance_notes,
            "dependencies": [
                {
                    "name": d.name,
                    "module": d.module,
                    "installed": d.installed,
                    "version": d.version,
                    "error": d.error,
                }
                for d in self.dependencies
            ],
            "diagnostics": self.diagnostics,
        }


class BaseExtractor(ABC):
    """
    Abstract base class for PDF extractors.

    All extraction implementations must inherit from this class and
    implement :meth:`extract`. The base class provides availability and
    dependency diagnostics so that a missing dependency makes the
    library *unavailable* without crashing the application.
    """

    #: Logical identifier used by the registry (e.g. "docling").
    library_id: str = "base"
    #: Human readable name.
    display_name: str = "Base"
    #: Short description of the library.
    description: str = ""
    #: Declared capabilities.
    capabilities: List[str] = []
    #: Free-form performance notes.
    performance_notes: str = ""
    #: Python modules that must be importable for this extractor to work.
    required_modules: List[str] = []

    def __init__(self) -> None:
        # Populated lazily / on demand.
        self._info: Optional[ExtractorInfo] = None

    # ------------------------------------------------------------------
    # Availability & diagnostics
    # ------------------------------------------------------------------
    def _check_module(self, module_name: str) -> DependencyDiagnostic:
        """Check whether a single module is importable and get its version."""
        import importlib.util
        import importlib.metadata as metadata

        try:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                return DependencyDiagnostic(
                    name=module_name,
                    module=module_name,
                    installed=False,
                    error="Module not found",
                )
            try:
                module = importlib.import_module(module_name)
                version = None
                # Try to get version from module's __version__ attribute
                module_version = getattr(module, "__version__", None)
                if module_version is not None and isinstance(module_version, str):
                    version = module_version
                if not version:
                    # Fall back to distribution metadata (e.g. docling
                    # does not expose __version__ on the package).
                    try:
                        version = metadata.version(module_name)
                    except Exception:
                        version = "unknown"
                return DependencyDiagnostic(
                    name=module_name,
                    module=module_name,
                    installed=True,
                    version=version,
                )
            except Exception as exc:
                return DependencyDiagnostic(
                    name=module_name,
                    module=module_name,
                    installed=True,
                    version="unknown",
                    error=f"Import error: {exc}",
                )
        except Exception as exc:
            return DependencyDiagnostic(
                name=module_name,
                module=module_name,
                installed=False,
                error=str(exc),
            )

    def get_dependency_diagnostics(self) -> List[DependencyDiagnostic]:
        """Return diagnostics for every declared dependency module."""
        return [self._check_module(m) for m in self.required_modules]

    def is_available(self) -> bool:
        """Return True when every required module is importable."""
        diags = self.get_dependency_diagnostics()
        return bool(diags) and all(d.installed for d in diags)

    def get_version(self) -> str:
        """Return the version of the primary dependency, if installed."""
        diags = self.get_dependency_diagnostics()
        for diag in diags:
            if diag.installed and diag.version and diag.version != "unknown":
                return diag.version
        return "unknown"

    def get_info(self) -> ExtractorInfo:
        """
        Build (and cache) the :class:`ExtractorInfo` for this extractor.

        Missing dependencies make the library ``not_installed`` (or
        ``error``) without raising, so the app keeps running.
        """
        if self._info is not None:
            return self._info

        diagnostics = self.get_dependency_diagnostics()
        missing = [d for d in diagnostics if not d.installed]
        errored = [d for d in diagnostics if d.installed and d.error]

        if errored:
            status = AvailabilityStatus.ERROR
        elif missing:
            status = AvailabilityStatus.NOT_INSTALLED
        else:
            status = AvailabilityStatus.AVAILABLE

        notes = []
        for d in missing:
            notes.append(f"Missing dependency '{d.module}': {d.error}")
        for d in errored:
            notes.append(f"Dependency '{d.module}' error: {d.error}")

        self._info = ExtractorInfo(
            library_id=self.library_id,
            display_name=self.display_name,
            version=self.get_version(),
            status=status,
            description=self.description,
            capabilities=self.capabilities,
            performance_notes=self.performance_notes,
            dependencies=diagnostics,
            diagnostics=notes,
        )
        return self._info

    # ------------------------------------------------------------------
    # Core extraction contract
    # ------------------------------------------------------------------
    @abstractmethod
    def extract(
        self,
        pdf_path: Path,
        output_dir: Path,
        options: Optional[Dict[str, Any]] = None,
    ) -> ExtractionResult:
        """
        Extract content from a PDF into a normalized ``ExtractionResult``.

        Implementations must:

        * validate the PDF (use :meth:`validate_pdf`),
        * create ``output_dir`` if it does not exist,
        * write all artifacts (markdown, json, images, tables, ...) into
          ``output_dir``,
        * return an :class:`~app.models.extraction_result.ExtractionResult`
          populated with ``library``, ``markdown``, ``structuredJson``,
          ``pageCount``, ``tableCount``, ``imageCount``, ``outputFiles``,
          ``status`` and, on failure, ``error``.

        The benchmark engine is responsible for filling the performance
        metrics and run identifiers afterwards.

        Args:
            pdf_path: Path to the source PDF file.
            output_dir: Directory where extraction artifacts are written.
            options: Optional extractor-specific options.

        Returns:
            ExtractionResult: Normalized extraction result.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def validate_pdf(self, pdf_path: Path) -> None:
        """
        Validate that the PDF file exists and is readable.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is not a PDF.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not pdf_path.is_file():
            raise ValueError(f"Path is not a file: {pdf_path}")

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"File is not a PDF: {pdf_path}")

    def get_library_name(self) -> str:
        """Backward-compatible alias for ``library_id``."""
        return self.library_id