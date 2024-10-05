import requests
from dotenv import load_dotenv
from os import getenv
import time

load_dotenv()

BRIGHT_DATA_API_TOKEN = getenv("BRIGHT_DATA_API_TOKEN")

def fetch_transcript(video_url):
    # Set the headers
    transcript_api_headers = {
        "Authorization": f"Bearer {BRIGHT_DATA_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Set the data (YouTube video URLs)
    data = [
        {"url": video_url},
    ]

    # API endpoint
    transcript_api_url = "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lk56epmy2i5g7lzu0k"

    # Send the POST request
    response = requests.post(transcript_api_url, headers=transcript_api_headers, json=data)

    # Print the response
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None
    else:
        print("First request was successful!")
        print(response.json(), '\n\n\n')

    # Extract the snapshot ID from the successful request
    snapshot_id =response.json()['snapshot_id']

    # Endpoint to get results for the snapshot ID
    snapshot_url = f" https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"

    for attempt in range(4):  # Try a maximum of 4 times
        response = requests.get(snapshot_url, headers=transcript_api_headers)

        if response.status_code == 200:
            return response.json()[0]['transcript']  # Return the successful response
        else:
            print(f"Attempt {attempt + 1} failed: {response.json()}")
            time.sleep(5)  # Wait for 5 seconds before retrying

    print("Max attempts reached. Failed to fetch snapshot.")
    return None

transcript = fetch_transcript("https://www.youtube.com/watch?v=HHtw4FwxESw&t=118s")
print(transcript)

# transcript_api_headers = {
#     "Authorization": f"Bearer {BRIGHT_DATA_API_TOKEN}",
#     "Content-Type": "application/json"
# }

# # Extract the snapshot ID from the successful request
# snapshot_id = "s_m1wmmnb6e29fgaebh"

# # Endpoint to get results for the snapshot ID
# snapshot_url = f"https://api.brightdata.com/datasets/snapshot/{snapshot_id}/download"

# # Make the GET request
# response = requests.get(snapshot_url, headers=transcript_api_headers)

# # Check if the request was successful
# if response.status_code == 200:
#     data = response.json()
#     print(data)
# else:
#     print(f"Request failed with status code {response.status_code}")
#     print(response.text)