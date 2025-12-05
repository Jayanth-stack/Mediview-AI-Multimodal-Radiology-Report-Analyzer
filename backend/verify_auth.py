import requests
import sys

BASE_URL = "http://localhost:8000/api"
EMAIL = "admin@mediview.ai"
PASSWORD = "admin123"

def test_auth():
    print("1. Testing Login...")
    login_data = {"username": EMAIL, "password": PASSWORD}
    try:
        r = requests.post(f"{BASE_URL}/login/access-token", data=login_data)
        if r.status_code != 200:
            print(f"FAILED: Login failed with status {r.status_code}: {r.text}")
            return
        token = r.json()["access_token"]
        print("SUCCESS: Got access token")
    except Exception as e:
        print(f"FAILED: Could not connect to backend: {e}")
        return

    print("\n2. Testing Protected Endpoint (Analyze Start) without token...")
    try:
        r = requests.post(f"{BASE_URL}/analyze/start", json={"s3_key": "test"})
        if r.status_code == 401 or r.status_code == 403:
            print("SUCCESS: Endpoint protected (401/403 received)")
        else:
            print(f"FAILED: Endpoint not protected, received {r.status_code}")
    except Exception as e:
        print(f"FAILED: {e}")

    print("\n3. Testing Protected Endpoint with token...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        # We expect this to execute (or fail with 500/validation error, but NOT 401)
        r = requests.post(f"{BASE_URL}/analyze/start", json={"s3_key": "test"}, headers=headers)
        if r.status_code != 401 and r.status_code != 403:
             print(f"SUCCESS: Token accepted (Status {r.status_code})")
        else:
            print(f"FAILED: Token rejected (Status {r.status_code})")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_auth()
