from pprint import pprint
import requests

url = "http://localhost:8000/transcribe"

file_path = "/Users/tt/Downloads/sample.mp3" 

try:
    with open(file_path, "rb") as f:
        files = {"audio_file": (file_path.split("/")[-1], f, "audio/mpeg")}
        response = requests.post(url, files=files)

    response.raise_for_status()
    print("Status Code:", response.status_code)
    print("Response Text (raw):", response.text)
    print("Response JSON (pretty-printed):")
    pprint(response.json()) 

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print("Response content:", e.response.text)