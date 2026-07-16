"""Test comprehensive benchmark metrics."""

import requests
import json
from pathlib import Path
from datetime import datetime


def test_comprehensive_metrics():
    """Test the comprehensive benchmark metrics with POST /extract."""
    
    print("=" * 70)
    print("Testing Comprehensive Benchmark Metrics")
    print("=" * 70)
    
    # API endpoint
    url = "http://localhost:8000/api/v1/extract"
    
    # Test PDF file
    test_pdf = Path("test_files/sample.pdf")
    
    if not test_pdf.exists():
        print(f"\n❌ Test PDF not found: {test_pdf}")
        print("Create a 'test_files' directory and add 'sample.pdf'")
        return False
    
    print(f"\n✓ Test PDF: {test_pdf}")
    print(f"  Size: {test_pdf.stat().st_size:,} bytes")
    
    # Test with Docling to get comprehensive outputs
    libraries = "docling"
    
    print(f"\n✓ Testing with: {libraries}")
    print("  (Docling produces the most comprehensive outputs)")
    
    try:
        # Upload and extract
        with open(test_pdf, 'rb') as pdf_file:
            files = {'file': (test_pdf.name, pdf_file, 'application/pdf')}
            data = {'libraries': libraries}
            
            print(f"\n📤 Uploading and extracting...")
            response = requests.post(url, files=files, data=data, timeout=120)
            
            print(f"\n📥 Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"\n❌ Request failed!")
                print(f"Response: {response.text}")
                return False
            
            result = response.json()
            
            print("\n" + "=" * 70)
            print("✅ BENCHMARK RESULTS WITH COMPREHENSIVE METRICS")
            print("=" * 70)
            
            # Overall benchmark info
            print(f"\n📊 Benchmark Overview:")
            print(f"  Benchmark ID: {result['id']}")
            print(f"  PDF: {result['pdf_filename']}")
            print(f"  Total Duration: {result['total_duration_ms']:.2f}ms")
            print(f"  Created: {result['created_at']}")
            
            # Extraction results
            for extraction in result['extraction_results']:
                lib_name = extraction['library_name'].upper()
                
                print(f"\n{'=' * 70}")
                print(f"📚 {lib_name} EXTRACTION RESULTS")
                print(f"{'=' * 70}")
                
                if extraction['success']:
                    print(f"\n✅ Status: SUCCESS\n")
                    
                    # Performance metrics
                    print("⏱️  PERFORMANCE METRICS:")
                    print(f"  • Processing Time: {extraction['execution_time_ms']:.2f}ms")
                    print(f"  • Peak Memory: {extraction['memory_usage_mb']:.2f}MB")
                    print(f"  • Average CPU: {extraction['cpu_usage_percent']:.1f}%")
                    
                    # Text extraction metrics
                    print(f"\n📝 TEXT EXTRACTION:")
                    print(f"  • Characters: {extraction['char_count']:,}")
                    print(f"  • Words: {extraction['word_count']:,}")
                    print(f"  • Pages: {extraction['pages_extracted']}")
                    
                    # Comprehensive output metrics
                    print(f"\n📦 OUTPUT METRICS:")
                    print(f"  • Total Output Size: {extraction['output_size_bytes']:,} bytes")
                    print(f"  • Images Extracted: {extraction['images_count']}")
                    print(f"  • Tables Extracted: {extraction['tables_count']}")
                    print(f"  • Markdown Length: {extraction['markdown_length']:,} characters")
                    print(f"  • JSON Size: {extraction['json_size_bytes']:,} bytes")
                    
                    if extraction['output_directory']:
                        print(f"\n📁 Output Directory:")
                        print(f"  {extraction['output_directory']}")
                    
                    # Text preview
                    text = extraction['text_content']
                    if text:
                        preview = text[:300].replace('\n', ' ')
                        print(f"\n📄 Text Preview:")
                        print(f"  {preview}...")
                    
                else:
                    print(f"\n❌ Status: FAILED")
                    print(f"  Error: {extraction['error_message']}")
            
            # Save results
            output_file = Path("benchmark_metrics_test.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n{'=' * 70}")
            print("💾 Results saved to:", output_file)
            
            # Check benchmark.json file
            print(f"\n📁 Checking results directory...")
            results_dir = Path("../results")
            if results_dir.exists():
                # Find latest result
                timestamp_dirs = sorted(
                    [d for d in results_dir.iterdir() if d.is_dir()],
                    key=lambda d: d.stat().st_mtime,
                    reverse=True
                )
                
                if timestamp_dirs:
                    latest = timestamp_dirs[0]
                    benchmark_file = latest / "benchmark.json"
                    
                    if benchmark_file.exists():
                        print(f"\n✅ benchmark.json found:")
                        print(f"  Location: {benchmark_file}")
                        print(f"  Size: {benchmark_file.stat().st_size:,} bytes")
                        
                        # Load and show summary
                        with open(benchmark_file, 'r') as f:
                            benchmark_data = json.load(f)
                        
                        print(f"\n📊 benchmark.json Summary:")
                        print(f"  • Benchmark ID: {benchmark_data['benchmark_id']}")
                        print(f"  • PDF: {benchmark_data['pdf_filename']}")
                        print(f"  • Libraries Tested: {len(benchmark_data['extraction_results'])}")
                        
                        if 'summary' in benchmark_data:
                            summary = benchmark_data['summary']
                            print(f"  • Fastest: {summary.get('fastest_library', 'N/A')}")
                            print(f"  • Most Efficient: {summary.get('most_efficient_memory', 'N/A')}")
                        
                        # Show performance comparison
                        if 'metadata' in benchmark_data and 'performance_comparison' in benchmark_data['metadata']:
                            perf = benchmark_data['metadata']['performance_comparison']
                            print(f"\n📈 Performance Comparison in benchmark.json:")
                            
                            if 'output_sizes' in perf:
                                print(f"  Output Sizes:")
                                for lib, size in perf['output_sizes'].items():
                                    print(f"    • {lib}: {size:,} bytes")
                            
                            if 'images_extracted' in perf:
                                print(f"  Images Extracted:")
                                for lib, count in perf['images_extracted'].items():
                                    print(f"    • {lib}: {count}")
                            
                            if 'tables_extracted' in perf:
                                print(f"  Tables Extracted:")
                                for lib, count in perf['tables_extracted'].items():
                                    print(f"    • {lib}: {count}")
                    else:
                        print(f"\n⚠️  benchmark.json not found in {latest}")
                else:
                    print(f"\n⚠️  No timestamp directories found in {results_dir}")
            else:
                print(f"\n⚠️  Results directory not found: {results_dir}")
            
            print(f"\n{'=' * 70}")
            print("✅ TEST COMPLETED SUCCESSFULLY")
            print(f"{'=' * 70}")
            
            return True
                
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure the backend server is running:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_metrics_in_benchmark_json():
    """Verify that benchmark.json contains all the new metrics."""
    
    print("\n" + "=" * 70)
    print("Verifying Metrics in benchmark.json")
    print("=" * 70)
    
    results_dir = Path("../results")
    if not results_dir.exists():
        print("\n⚠️  Results directory not found")
        return False
    
    # Find latest result
    timestamp_dirs = sorted(
        [d for d in results_dir.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True
    )
    
    if not timestamp_dirs:
        print("\n⚠️  No results found")
        return False
    
    latest = timestamp_dirs[0]
    benchmark_file = latest / "benchmark.json"
    
    if not benchmark_file.exists():
        print(f"\n❌ benchmark.json not found in {latest}")
        return False
    
    print(f"\n✅ Found: {benchmark_file}")
    
    with open(benchmark_file, 'r') as f:
        data = json.load(f)
    
    # Check required fields
    required_fields = [
        'benchmark_id',
        'pdf_filename',
        'created_at',
        'total_duration_ms',
        'extraction_results',
    ]
    
    print(f"\n✓ Checking required fields...")
    for field in required_fields:
        if field in data:
            print(f"  ✅ {field}")
        else:
            print(f"  ❌ {field} MISSING")
            return False
    
    # Check extraction result metrics
    if data['extraction_results']:
        result = data['extraction_results'][0]
        
        print(f"\n✓ Checking comprehensive metrics in extraction results...")
        
        comprehensive_fields = [
            'output_size_bytes',
            'images_count',
            'tables_count',
            'markdown_length',
            'json_size_bytes',
            'output_directory',
        ]
        
        for field in comprehensive_fields:
            if field in result:
                value = result[field]
                print(f"  ✅ {field}: {value}")
            else:
                print(f"  ❌ {field} MISSING")
                return False
    
    print(f"\n{'=' * 70}")
    print("✅ ALL METRICS VERIFIED IN benchmark.json")
    print(f"{'=' * 70}")
    
    return True


if __name__ == "__main__":
    import sys
    
    # Test 1: Comprehensive metrics
    success1 = test_comprehensive_metrics()
    
    # Test 2: Verify benchmark.json
    success2 = verify_metrics_in_benchmark_json()
    
    if success1 and success2:
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Comprehensive metrics implemented:")
        print("  • Processing Time")
        print("  • Peak Memory")
        print("  • Average CPU")
        print("  • Output Size")
        print("  • Pages")
        print("  • Images")
        print("  • Tables")
        print("  • Markdown Length")
        print("  • JSON Size")
        print("\n✅ benchmark.json generated and saved in results folder")
        print("✅ Integrated with POST /extract endpoint")
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        sys.exit(1)
