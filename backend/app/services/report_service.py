"""
Benchmark Report Generation Service

Automatically generates comprehensive markdown reports for benchmark executions.
Reports include overview, machine info, comparison, pros/cons, and recommendations.
"""

import platform
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json


class ReportService:
    """Service for generating benchmark reports."""

    def __init__(self):
        """Initialize report service."""
        self.machine_info = self._get_machine_info()

    def _get_machine_info(self) -> Dict[str, str]:
        """
        Gather machine information for the report.

        Returns:
            Dictionary containing system information
        """
        try:
            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            
            return {
                "os": platform.system(),
                "os_version": platform.version(),
                "os_release": platform.release(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "cpu_cores": psutil.cpu_count(logical=False),
                "cpu_threads": psutil.cpu_count(logical=True),
                "cpu_frequency": f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A",
                "total_memory": f"{memory.total / (1024**3):.2f} GB",
                "python_version": platform.python_version(),
            }
        except Exception as e:
            return {
                "os": "Unknown",
                "error": str(e)
            }

    def generate_report(
        self,
        benchmark_results: Dict,
        pdf_info: Dict,
        output_dir: Path,
    ) -> Path:
        """
        Generate comprehensive benchmark report.

        Args:
            benchmark_results: Dictionary with benchmark results for each library
            pdf_info: Information about the PDF being processed
            output_dir: Directory to save the report

        Returns:
            Path to the generated report file
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = output_dir / "report.md"
        
        # Build report content
        content = []
        
        # Title
        content.append("# PDF Extraction Benchmark Report")
        content.append("")
        content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        content.append("---")
        content.append("")
        
        # Overview Section
        content.extend(self._generate_overview_section(benchmark_results, pdf_info))
        content.append("")
        
        # Machine Information Section
        content.extend(self._generate_machine_info_section())
        content.append("")
        
        # Benchmark Results Section
        content.extend(self._generate_benchmark_section(benchmark_results))
        content.append("")
        
        # Comparison Section
        content.extend(self._generate_comparison_section(benchmark_results))
        content.append("")
        
        # Pros and Cons Section
        content.extend(self._generate_pros_cons_section(benchmark_results))
        content.append("")
        
        # Recommendations Section
        content.extend(self._generate_recommendations_section(benchmark_results, pdf_info))
        content.append("")
        
        # Footer
        content.append("---")
        content.append("")
        content.append("*Report generated automatically by PDF Extraction Benchmark System*")
        
        # Write report
        report_content = "\n".join(content)
        report_path.write_text(report_content, encoding="utf-8")
        
        return report_path

    def _generate_overview_section(
        self,
        benchmark_results: Dict,
        pdf_info: Dict
    ) -> List[str]:
        """Generate overview section."""
        lines = ["## 📊 Overview"]
        lines.append("")
        
        # PDF Information
        lines.append(f"**Document:** {pdf_info.get('name', 'Unknown')}")
        lines.append(f"**File Size:** {self._format_bytes(pdf_info.get('size', 0))}")
        lines.append(f"**Pages:** {pdf_info.get('pages', 'Unknown')}")
        lines.append("")
        
        # Benchmark Summary
        total_libraries = len(benchmark_results)
        successful = sum(1 for r in benchmark_results.values() if r.get('status') == 'success')
        failed = total_libraries - successful
        
        lines.append(f"**Libraries Tested:** {total_libraries}")
        lines.append(f"**Successful Extractions:** {successful} ✅")
        lines.append(f"**Failed Extractions:** {failed} ❌")
        lines.append("")
        
        if successful > 0:
            # Find fastest
            successful_results = {k: v for k, v in benchmark_results.items() 
                                 if v.get('status') == 'success'}
            fastest = min(successful_results.items(), 
                         key=lambda x: x[1].get('execution_time_ms', float('inf')))
            
            lines.append(f"**Fastest Library:** {fastest[0]} ({fastest[1].get('execution_time_ms', 0):.2f} ms)")
        
        lines.append("")
        return lines

    def _generate_machine_info_section(self) -> List[str]:
        """Generate machine information section."""
        lines = ["## 💻 Machine Information"]
        lines.append("")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        lines.append(f"| Operating System | {self.machine_info.get('os', 'Unknown')} {self.machine_info.get('os_release', '')} |")
        lines.append(f"| Architecture | {self.machine_info.get('architecture', 'Unknown')} |")
        lines.append(f"| Processor | {self.machine_info.get('processor', 'Unknown')} |")
        lines.append(f"| CPU Cores | {self.machine_info.get('cpu_cores', 'Unknown')} physical, {self.machine_info.get('cpu_threads', 'Unknown')} logical |")
        lines.append(f"| CPU Frequency | {self.machine_info.get('cpu_frequency', 'Unknown')} |")
        lines.append(f"| Total Memory | {self.machine_info.get('total_memory', 'Unknown')} |")
        lines.append(f"| Python Version | {self.machine_info.get('python_version', 'Unknown')} |")
        lines.append("")
        return lines

    def _generate_benchmark_section(self, benchmark_results: Dict) -> List[str]:
        """Generate detailed benchmark results section."""
        lines = ["## 🔬 Benchmark Results"]
        lines.append("")
        
        for library_name, result in sorted(benchmark_results.items()):
            status = result.get('status', 'unknown')
            
            lines.append(f"### {library_name}")
            lines.append("")
            
            if status == 'success':
                lines.append(f"**Status:** ✅ Success")
                lines.append("")
                
                # Performance Metrics
                lines.append("**Performance Metrics:**")
                lines.append("")
                lines.append(f"- **Execution Time:** {result.get('execution_time_ms', 0):.2f} ms")
                lines.append(f"- **Peak Memory:** {result.get('peak_memory_mb', 0):.2f} MB")
                lines.append(f"- **Average CPU:** {result.get('avg_cpu_percent', 0):.2f}%")
                lines.append("")
                
                # Output Information
                outputs = result.get('outputs', {})
                lines.append("**Output Information:**")
                lines.append("")
                lines.append(f"- **Markdown Size:** {self._format_bytes(outputs.get('markdown_size', 0))}")
                lines.append(f"- **JSON Size:** {self._format_bytes(outputs.get('json_size', 0))}")
                lines.append(f"- **Images Extracted:** {outputs.get('images_count', 0)}")
                lines.append(f"- **Tables Extracted:** {outputs.get('tables_count', 0)}")
                lines.append("")
                
            else:
                lines.append(f"**Status:** ❌ Failed")
                lines.append("")
                error_msg = result.get('error', 'Unknown error')
                lines.append(f"**Error:** {error_msg}")
                lines.append("")
        
        return lines

    def _generate_comparison_section(self, benchmark_results: Dict) -> List[str]:
        """Generate comparison table section."""
        lines = ["## ⚖️ Performance Comparison"]
        lines.append("")
        
        successful_results = {k: v for k, v in benchmark_results.items() 
                             if v.get('status') == 'success'}
        
        if not successful_results:
            lines.append("*No successful extractions to compare.*")
            lines.append("")
            return lines
        
        # Create comparison table
        lines.append("| Library | Time (ms) | Memory (MB) | CPU (%) | Output Size | Images | Tables |")
        lines.append("|---------|-----------|-------------|---------|-------------|--------|--------|")
        
        for library_name, result in sorted(successful_results.items(), 
                                          key=lambda x: x[1].get('execution_time_ms', 0)):
            outputs = result.get('outputs', {})
            total_size = outputs.get('markdown_size', 0) + outputs.get('json_size', 0)
            
            lines.append(
                f"| {library_name} | "
                f"{result.get('execution_time_ms', 0):.2f} | "
                f"{result.get('peak_memory_mb', 0):.2f} | "
                f"{result.get('avg_cpu_percent', 0):.2f} | "
                f"{self._format_bytes(total_size)} | "
                f"{outputs.get('images_count', 0)} | "
                f"{outputs.get('tables_count', 0)} |"
            )
        
        lines.append("")
        
        # Winners
        lines.append("### 🏆 Category Winners")
        lines.append("")
        
        # Fastest
        fastest = min(successful_results.items(), 
                     key=lambda x: x[1].get('execution_time_ms', float('inf')))
        lines.append(f"- **Fastest Execution:** {fastest[0]} ({fastest[1].get('execution_time_ms', 0):.2f} ms)")
        
        # Least Memory
        least_memory = min(successful_results.items(), 
                          key=lambda x: x[1].get('peak_memory_mb', float('inf')))
        lines.append(f"- **Least Memory:** {least_memory[0]} ({least_memory[1].get('peak_memory_mb', 0):.2f} MB)")
        
        # Least CPU
        least_cpu = min(successful_results.items(), 
                       key=lambda x: x[1].get('avg_cpu_percent', float('inf')))
        lines.append(f"- **Least CPU:** {least_cpu[0]} ({least_cpu[1].get('avg_cpu_percent', 0):.2f}%)")
        
        # Most Complete Output
        most_complete = max(successful_results.items(), 
                           key=lambda x: (x[1].get('outputs', {}).get('images_count', 0) + 
                                        x[1].get('outputs', {}).get('tables_count', 0)))
        lines.append(f"- **Most Complete Output:** {most_complete[0]} ({most_complete[1].get('outputs', {}).get('images_count', 0)} images, {most_complete[1].get('outputs', {}).get('tables_count', 0)} tables)")
        
        lines.append("")
        return lines

    def _generate_pros_cons_section(self, benchmark_results: Dict) -> List[str]:
        """Generate pros and cons analysis for each library."""
        lines = ["## ✅ ❌ Pros and Cons Analysis"]
        lines.append("")
        
        successful_results = {k: v for k, v in benchmark_results.items() 
                             if v.get('status') == 'success'}
        
        if not successful_results:
            lines.append("*No successful extractions to analyze.*")
            lines.append("")
            return lines
        
        for library_name, result in sorted(successful_results.items()):
            lines.append(f"### {library_name}")
            lines.append("")
            
            pros = []
            cons = []
            
            # Analyze performance
            exec_time = result.get('execution_time_ms', 0)
            memory = result.get('peak_memory_mb', 0)
            cpu = result.get('avg_cpu_percent', 0)
            outputs = result.get('outputs', {})
            images = outputs.get('images_count', 0)
            tables = outputs.get('tables_count', 0)
            
            # Speed analysis
            if exec_time < 1000:
                pros.append("⚡ Very fast execution (< 1 second)")
            elif exec_time < 2000:
                pros.append("🚀 Fast execution (< 2 seconds)")
            elif exec_time > 5000:
                cons.append("🐌 Slow execution (> 5 seconds)")
            
            # Memory analysis
            if memory < 100:
                pros.append("💾 Low memory usage (< 100 MB)")
            elif memory < 200:
                pros.append("💿 Moderate memory usage (< 200 MB)")
            elif memory > 300:
                cons.append("💣 High memory usage (> 300 MB)")
            
            # CPU analysis
            if cpu < 40:
                pros.append("🔋 Low CPU usage (< 40%)")
            elif cpu > 70:
                cons.append("🔥 High CPU usage (> 70%)")
            
            # Feature analysis
            if images > 0:
                pros.append(f"🖼️ Extracts images ({images} found)")
            else:
                cons.append("📷 No image extraction")
            
            if tables > 0:
                pros.append(f"📊 Extracts tables ({tables} found)")
            else:
                cons.append("📋 No table extraction")
            
            # Output size
            total_size = outputs.get('markdown_size', 0) + outputs.get('json_size', 0)
            if total_size > 30000:
                pros.append("📝 Comprehensive output")
            elif total_size < 10000:
                cons.append("📄 Limited output")
            
            # Library-specific notes
            if library_name.lower() == 'pypdf':
                pros.append("🔧 Simple and lightweight")
                cons.append("⚠️ Basic extraction capabilities")
            elif library_name.lower() == 'pdfplumber':
                pros.append("📐 Good table detection")
            elif library_name.lower() == 'pymupdf':
                pros.append("⚡ Fastest library")
                pros.append("🎨 Good image extraction")
            elif library_name.lower() == 'docling':
                pros.append("🧠 Advanced document understanding")
                pros.append("📊 Excellent structure preservation")
            elif library_name.lower() == 'mineru':
                pros.append("👁️ OCR support")
                pros.append("🎯 Layout analysis")
            elif library_name.lower() == 'unstructured':
                pros.append("🏗️ Element-based extraction")
                pros.append("🎯 Content classification")
            
            # Write pros
            lines.append("**Pros:**")
            lines.append("")
            if pros:
                for pro in pros:
                    lines.append(f"- {pro}")
            else:
                lines.append("- *None identified*")
            lines.append("")
            
            # Write cons
            lines.append("**Cons:**")
            lines.append("")
            if cons:
                for con in cons:
                    lines.append(f"- {con}")
            else:
                lines.append("- *None identified*")
            lines.append("")
        
        return lines

    def _generate_recommendations_section(
        self,
        benchmark_results: Dict,
        pdf_info: Dict
    ) -> List[str]:
        """Generate recommendations based on results."""
        lines = ["## 💡 Recommendations"]
        lines.append("")
        
        successful_results = {k: v for k, v in benchmark_results.items() 
                             if v.get('status') == 'success'}
        
        if not successful_results:
            lines.append("**No successful extractions. Consider:**")
            lines.append("")
            lines.append("- Verify PDF is not corrupted")
            lines.append("- Check library installations")
            lines.append("- Review error logs for details")
            lines.append("")
            return lines
        
        pages = pdf_info.get('pages', 0)
        
        # General recommendation
        lines.append("### Best Library for Your Use Case")
        lines.append("")
        
        # Speed priority
        fastest = min(successful_results.items(), 
                     key=lambda x: x[1].get('execution_time_ms', float('inf')))
        lines.append(f"**For Speed:** Use **{fastest[0]}** ({fastest[1].get('execution_time_ms', 0):.2f} ms)")
        lines.append("")
        
        # Memory efficiency
        least_memory = min(successful_results.items(), 
                          key=lambda x: x[1].get('peak_memory_mb', float('inf')))
        lines.append(f"**For Memory Efficiency:** Use **{least_memory[0]}** ({least_memory[1].get('peak_memory_mb', 0):.2f} MB)")
        lines.append("")
        
        # Feature completeness
        most_features = max(successful_results.items(), 
                           key=lambda x: (x[1].get('outputs', {}).get('images_count', 0) + 
                                        x[1].get('outputs', {}).get('tables_count', 0)))
        lines.append(f"**For Feature Completeness:** Use **{most_features[0]}** ({most_features[1].get('outputs', {}).get('images_count', 0)} images, {most_features[1].get('outputs', {}).get('tables_count', 0)} tables)")
        lines.append("")
        
        # Balanced recommendation
        lines.append("### Overall Recommendation")
        lines.append("")
        
        # Calculate balanced score (lower is better)
        scored_results = []
        for lib_name, result in successful_results.items():
            # Normalize scores (0-1 range)
            times = [r.get('execution_time_ms', 0) for r in successful_results.values()]
            memories = [r.get('peak_memory_mb', 0) for r in successful_results.values()]
            features = [r.get('outputs', {}).get('images_count', 0) + 
                       r.get('outputs', {}).get('tables_count', 0) 
                       for r in successful_results.values()]
            
            max_time = max(times) or 1
            max_memory = max(memories) or 1
            max_features = max(features) or 1
            
            time_score = result.get('execution_time_ms', 0) / max_time
            memory_score = result.get('peak_memory_mb', 0) / max_memory
            feature_score = 1 - ((result.get('outputs', {}).get('images_count', 0) + 
                                 result.get('outputs', {}).get('tables_count', 0)) / max_features)
            
            # Weighted score (40% speed, 30% memory, 30% features)
            balanced_score = (time_score * 0.4 + memory_score * 0.3 + feature_score * 0.3)
            
            scored_results.append((lib_name, balanced_score, result))
        
        scored_results.sort(key=lambda x: x[1])
        best_balanced = scored_results[0]
        
        lines.append(f"**Best Balanced Choice:** **{best_balanced[0]}**")
        lines.append("")
        lines.append("This library offers the best balance of:")
        lines.append("- Execution speed")
        lines.append("- Memory efficiency")
        lines.append("- Feature completeness")
        lines.append("")
        
        # Use case specific recommendations
        lines.append("### Use Case Specific Recommendations")
        lines.append("")
        
        if pages < 10:
            lines.append("**For Short Documents (< 10 pages):**")
            lines.append(f"- Any library will work well")
            lines.append(f"- Consider **{fastest[0]}** for maximum speed")
        elif pages < 50:
            lines.append("**For Medium Documents (10-50 pages):**")
            lines.append(f"- **{best_balanced[0]}** offers best balance")
            lines.append(f"- Consider **{least_memory[0]}** if memory is limited")
        else:
            lines.append("**For Large Documents (> 50 pages):**")
            lines.append(f"- **{least_memory[0]}** for memory efficiency")
            lines.append(f"- Consider batch processing with **{fastest[0]}**")
        
        lines.append("")
        
        # Special requirements
        lines.append("**Special Requirements:**")
        lines.append("")
        lines.append("- **Need OCR?** → MinerU (if available)")
        lines.append("- **Need tables?** → PDFPlumber or Docling")
        lines.append("- **Need images?** → PyMuPDF or Docling")
        lines.append("- **Need structure?** → Docling or Unstructured")
        lines.append("- **Simple text?** → PyPDF or PyMuPDF")
        lines.append("")
        
        return lines

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human-readable string."""
        if bytes_value < 1024:
            return f"{bytes_value} B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value / 1024:.2f} KB"
        else:
            return f"{bytes_value / (1024 * 1024):.2f} MB"


# Example usage
if __name__ == "__main__":
    # Example benchmark results
    example_results = {
        "PyPDF": {
            "status": "success",
            "execution_time_ms": 856.23,
            "peak_memory_mb": 89.4,
            "avg_cpu_percent": 28.5,
            "outputs": {
                "markdown_size": 12340,
                "json_size": 8500,
                "images_count": 0,
                "tables_count": 0,
            }
        },
        "Docling": {
            "status": "success",
            "execution_time_ms": 1234.56,
            "peak_memory_mb": 128.5,
            "avg_cpu_percent": 45.2,
            "outputs": {
                "markdown_size": 15420,
                "json_size": 23450,
                "images_count": 3,
                "tables_count": 2,
            }
        }
    }
    
    example_pdf_info = {
        "name": "sample-document.pdf",
        "size": 2457600,
        "pages": 45
    }
    
    service = ReportService()
    report_path = service.generate_report(
        benchmark_results=example_results,
        pdf_info=example_pdf_info,
        output_dir=Path("results/2026_07_15_143022")
    )
    
    print(f"Report generated: {report_path}")
