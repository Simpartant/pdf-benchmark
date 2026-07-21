// PDF extraction library constants

export interface LibraryConfig {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  features: string[];
  selected?: boolean;
}

export const AVAILABLE_LIBRARIES: LibraryConfig[] = [
  {
    id: "pypdf",
    name: "PyPDF",
    description: "Pure Python, basic extraction",
    icon: "📄",
    color: "blue",
    features: ["Fast", "Simple", "Text only"],
    selected: false,
  },
  {
    id: "pdfplumber",
    name: "PDFPlumber",
    description: "Powerful table extraction",
    icon: "📊",
    color: "green",
    features: ["Tables", "Layout", "Text"],
    selected: false,
  },
  {
    id: "pymupdf",
    name: "PyMuPDF",
    description: "Fast C-based library",
    icon: "⚡",
    color: "yellow",
    features: ["Very Fast", "Images", "Text"],
    selected: false,
  },
  {
    id: "docling",
    name: "Docling",
    description: "Advanced document understanding",
    icon: "🧠",
    color: "purple",
    features: ["Structure", "Images", "Tables", "Metadata"],
    selected: true,
  },
  {
    id: "mineru",
    name: "MinerU",
    description: "Layout analysis with OCR",
    icon: "👁️",
    color: "orange",
    features: ["OCR", "Layout", "Images", "Tables"],
    selected: true,
  },
  {
    id: "unstructured",
    name: "Unstructured",
    description: "Element-based extraction",
    icon: "🏗️",
    color: "teal",
    features: ["Classification", "Elements", "Images", "Tables"],
    selected: false,
  },
];

export const DEFAULT_SELECTED_LIBRARIES = AVAILABLE_LIBRARIES.filter(
  (lib) => lib.selected,
).map((lib) => lib.id);
