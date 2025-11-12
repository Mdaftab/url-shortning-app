"""
Test script for URL shortening service.
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    """Test root endpoint."""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✓ Root endpoint works")
        return True
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
        return False

def test_shorten_url():
    """Test URL shortening endpoint."""
    print("\nTesting POST /api/shorten...")
    try:
        # Test with valid URL
        test_url = "https://www.example.com/very/long/url/path"
        response = requests.post(
            f"{BASE_URL}/api/shorten",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "short_url" in data
        assert "original_url" in data
        assert "short_code" in data
        assert test_url in data["original_url"] or test_url.replace("https://", "") in data["original_url"]
        print(f"✓ URL shortened successfully")
        print(f"  Original: {data['original_url']}")
        print(f"  Short URL: {data['short_url']}")
        print(f"  Short Code: {data['short_code']}")
        return data["short_code"]
    except Exception as e:
        print(f"✗ URL shortening failed: {e}")
        return None

def test_redirect(short_code):
    """Test URL redirection."""
    print(f"\nTesting GET /{short_code} (redirect)...")
    try:
        response = requests.get(
            f"{BASE_URL}/{short_code}",
            allow_redirects=False
        )
        assert response.status_code == 302
        assert "Location" in response.headers
        print(f"✓ Redirect works")
        print(f"  Redirects to: {response.headers['Location']}")
        return True
    except Exception as e:
        print(f"✗ Redirect failed: {e}")
        return False

def test_invalid_url():
    """Test invalid URL handling."""
    print("\nTesting invalid URL...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/shorten",
            json={"url": "not-a-valid-url"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"✓ Invalid URL correctly rejected: {data['detail']}")
        return True
    except Exception as e:
        print(f"✗ Invalid URL test failed: {e}")
        return False

def test_nonexistent_code():
    """Test non-existent short code."""
    print("\nTesting non-existent short code...")
    try:
        response = requests.get(f"{BASE_URL}/nonexistent123")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print(f"✓ Non-existent code correctly handled: {data['detail']}")
        return True
    except Exception as e:
        print(f"✗ Non-existent code test failed: {e}")
        return False

def test_stats(short_code):
    """Test stats endpoint."""
    print(f"\nTesting GET /api/stats/{short_code}...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats/{short_code}")
        assert response.status_code == 200
        data = response.json()
        assert "short_url" in data
        assert "original_url" in data
        assert "short_code" in data
        print(f"✓ Stats endpoint works")
        print(f"  Created at: {data.get('created_at', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ Stats endpoint failed: {e}")
        return False

def test_duplicate_url():
    """Test that duplicate URLs return existing short code."""
    print("\nTesting duplicate URL handling...")
    try:
        test_url = "https://www.duplicate-test.com"
        # First request
        response1 = requests.post(
            f"{BASE_URL}/api/shorten",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        assert response1.status_code == 201
        data1 = response1.json()
        short_code1 = data1["short_code"]
        
        # Second request with same URL
        response2 = requests.post(
            f"{BASE_URL}/api/shorten",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        assert response2.status_code == 201
        data2 = response2.json()
        short_code2 = data2["short_code"]
        
        # Should return the same short code
        assert short_code1 == short_code2
        print(f"✓ Duplicate URL returns existing short code: {short_code1}")
        return True
    except Exception as e:
        print(f"✗ Duplicate URL test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("URL Shortening Service - Test Suite")
    print("=" * 60)
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                print("Server is ready!\n")
                break
        except:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                print("✗ Server is not responding. Please start the server first.")
                print("  Run: uvicorn main:app --host 0.0.0.0 --port 5000")
                sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Root Endpoint", test_root_endpoint()))
    short_code = test_shorten_url()
    results.append(("Shorten URL", short_code is not None))
    
    if short_code:
        results.append(("Redirect", test_redirect(short_code)))
        results.append(("Stats", test_stats(short_code)))
    
    results.append(("Invalid URL", test_invalid_url()))
    results.append(("Non-existent Code", test_nonexistent_code()))
    results.append(("Duplicate URL", test_duplicate_url()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

