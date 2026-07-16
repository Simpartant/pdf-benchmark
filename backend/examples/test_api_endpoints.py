"""
Example: Testing Health and Libraries Endpoints

This script demonstrates how to test the real backend API endpoints.
"""

import requests
import json
from typing import Dict, Any


def test_health_endpoint(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Test the health check endpoint.
    
    Args:
        base_url: Base URL of the API
        
    Returns:
        Health response data
    """
    url = f"{base_url}/api/v1/health"
    
    print(f"Testing health endpoint: {url}")
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nHealth Response:")
        print(json.dumps(data, indent=2))
        
        # Verify all required fields
        required_fields = ["status", "version", "pythonVersion", "uptime"]
        for field in required_fields:
            if field in data:
                print(f"✅ {field}: {data[field]}")
            else:
                print(f"❌ Missing field: {field}")
        
        return data
    else:
        print(f"❌ Error: {response.text}")
        return {}


def test_libraries_endpoint(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Test the libraries endpoint.
    
    Args:
        base_url: Base URL of the API
        
    Returns:
        Libraries response data
    """
    url = f"{base_url}/api/v1/libraries"
    
    print(f"\nTesting libraries endpoint: {url}")
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\nFound {data.get('total', 0)} libraries:")
        
        for lib in data.get("libraries", []):
            installed_status = "✅ Installed" if lib.get("installed") else "❌ Not installed"
            version = lib.get("version", "unknown")
            
            print(f"\n{lib.get('displayName', lib.get('name'))} ({lib.get('name')})")
            print(f"  {installed_status}")
            print(f"  Version: {version}")
            print(f"  Status: {lib.get('status')}")
            
            if lib.get("description"):
                print(f"  Description: {lib.get('description')}")
            
            if lib.get("capabilities"):
                print(f"  Capabilities: {', '.join(lib.get('capabilities', []))}")
        
        # Summary
        installed_count = sum(1 for lib in data.get("libraries", []) if lib.get("installed"))
        print(f"\n📊 Summary: {installed_count}/{data.get('total', 0)} libraries installed")
        
        return data
    else:
        print(f"❌ Error: {response.text}")
        return {}


def main():
    """Run all endpoint tests."""
    print("="*60)
    print("PDF Extraction Benchmark API - Endpoint Tests")
    print("="*60)
    
    # Test health endpoint
    health_data = test_health_endpoint()
    
    # Test libraries endpoint
    libraries_data = test_libraries_endpoint()
    
    print("\n" + "="*60)
    print("Tests Complete")
    print("="*60)
    
    # Return results
    return {
        "health": health_data,
        "libraries": libraries_data,
    }


if __name__ == "__main__":
    try:
        results = main()
        
        # Save results to file
        with open("api_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print("\n✅ Results saved to api_test_results.json")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the backend server is running on http://localhost:8000")
        print("\nTo start the server, run:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
