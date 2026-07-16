"""Test script for POST /extract endpoint with file upload."""

import requests
import json
from pathlib import Path


def test_extract_endpoint():
    """Test the POST /extract endpoint with file upload."""
    
    print("=" * 60)
    print("Testing POST /extract endpoint")
    print("=" * 60)
    
    # API endpoint
    url = "http://localhost:8000/api/v1/extract"
    
    # Test PDF file
    test_pdf = Path("test_files/sample.pdf")
    
    if not test_pdf.exists():
        print(f"\n❌ Test PDF not found: {test_pdf}")
        print("Create a 'test_files' directory and add 'sample.pdf'")
        return False
    
    print(f"\n✓ Test PDF found: {test_pdf}")
    print(f"  Size: {test_pdf.stat().st_size} bytes")
    
    # Libraries to test
    libraries = "docling,pypdf,pdfplumber"
    
    print(f"\n✓ Libraries: {libraries}")
    
    try:
        # Prepare multipart form data
        with open(test_pdf, 'rb') as pdf_file:
            files = {
                'file': (test_pdf.name, pdf_file, 'application/pdf')
            }
            data = {
                'libraries': libraries
            }
            
            print(f"\n📤 Uploading PDF and running extraction...")
            print(f"   POST {url}")
            
            # Make request
            response = requests.post(url, files=files, data=data)
            
            print(f"\n📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ Extraction Successful!")
                print("\n" + "=" * 60)
                print("Benchmark Results")
                print("=" * 60)
                
                print(f"\nPDF: {result['pdf_filename']}")
                print(f"Total Duration: {result['total_duration_ms']:.2f}ms")
                print(f"Fastest Library: {result.get('fastest_library', 'N/A')}")
                print(f"Most Efficient (Memory): {result.get('most_efficient_memory', 'N/A')}")
                print(f"Most Text Extracted: {result.get('most_text_extracted', 'N/A')}")
                
                print(f"\n📊 Extraction Results ({len(result['extraction_results'])} libraries):")
                print("-" * 60)
                
                for extraction in result['extraction_results']:
                    print(f"\n{extraction['library_name'].upper()}:")
                    if extraction['success']:
                        print(f"  ✅ Success")
                        print(f"  Execution Time: {extraction['execution_time_ms']:.2f}ms")
                        print(f"  Memory Usage: {extraction['memory_usage_mb']:.2f}MB")
                        print(f"  CPU Usage: {extraction['cpu_usage_percent']:.1f}%")
                        print(f"  Characters: {extraction['char_count']:,}")
                        print(f"  Words: {extraction['word_count']:,}")
                        print(f"  Pages: {extraction['pages_extracted']}")
                        
                        # Show text preview
                        text = extraction['text_content']
                        if text:
                            preview = text[:200].replace('\n', ' ')
                            print(f"  Text Preview: {preview}...")
                    else:
                        print(f"  ❌ Failed")
                        print(f"  Error: {extraction['error_message']}")
                
                print("\n" + "=" * 60)
                print("Test Completed Successfully!")
                print("=" * 60)
                
                # Save full results to file
                output_file = Path("test_extract_results.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                
                print(f"\n💾 Full results saved to: {output_file}")
                
                return True
                
            else:
                print(f"\n❌ Request failed!")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
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


def test_with_docling_only():
    """Test extraction with Docling only."""
    
    print("\n" + "=" * 60)
    print("Testing Docling Extraction Only")
    print("=" * 60)
    
    url = "http://localhost:8000/api/v1/extract"
    test_pdf = Path("test_files/sample.pdf")
    
    if not test_pdf.exists():
        print(f"\n❌ Test PDF not found: {test_pdf}")
        return False
    
    try:
        with open(test_pdf, 'rb') as pdf_file:
            files = {'file': (test_pdf.name, pdf_file, 'application/pdf')}
            data = {'libraries': 'docling'}
            
            print(f"\n📤 Uploading PDF for Docling extraction...")
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n✅ Docling Extraction Successful!")
                
                docling_result = result['extraction_results'][0]
                if docling_result['success']:
                    print(f"\nExecution Time: {docling_result['execution_time_ms']:.2f}ms")
                    print(f"Memory Usage: {docling_result['memory_usage_mb']:.2f}MB")
                    print(f"Characters Extracted: {docling_result['char_count']:,}")
                    print(f"Words Extracted: {docling_result['word_count']:,}")
                    
                    # Check for outputs in results directory
                    print("\n📁 Docling outputs should be saved in:")
                    print("   results/{timestamp}/docling/")
                    print("   - markdown.md")
                    print("   - document.json")
                    print("   - metadata.json")
                    print("   - images/ (if any)")
                    print("   - tables/ (if any)")
                    
                return True
            else:
                print(f"\n❌ Failed: {response.status_code}")
                print(response.text)
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    # Test 1: Multiple libraries
    success1 = test_extract_endpoint()
    
    # Test 2: Docling only
    success2 = test_with_docling_only()
    
    # Overall result
    if success1 and success2:
        print("\n" + "=" * 60)
        print("🎉 All Tests Passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Some Tests Failed")
        print("=" * 60)
        sys.exit(1)
