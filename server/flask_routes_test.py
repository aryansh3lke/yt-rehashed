import requests

response = requests.get("http://127.0.0.1:8000/api/test-google-api")
print(response.json())