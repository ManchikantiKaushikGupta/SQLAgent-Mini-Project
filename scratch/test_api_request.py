import requests

url = "http://localhost:8000/api/v1/ask"
payload = {
    "query": "Show all products",
    "user_role": "admin",
    "username": "admin_user"
}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    print("Response Text:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
