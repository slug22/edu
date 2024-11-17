import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
BASE_UPLOAD_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
JWT = os.getenv("PINATA_JWT")

if not JWT:
    raise ValueError("Environment variable PINATA_JWT is not set. Please check your .env file.")

HEADERS = {
    "Authorization": f"Bearer {JWT}",
    "Content-Type": "application/json"
}

def upload_json(data):
    """
    Uploads a JSON object to Pinata.

    Args:
        data (dict): The JSON object to upload.

    Returns:
        dict: Response data from Pinata.
    """
    try:
        response = requests.post(BASE_UPLOAD_URL, headers=HEADERS, json=data, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to upload JSON: {e}")

# Testing 
if __name__ == "__main__":
    # Define test JSON data
    sample_data = {
        "name": "Test JSON",
        "description": "This is an example JSON object uploaded to Pinata.",
        "data": {
            "key1": "value1",
            "key2": "value2",
            "nested": {
                "key3": "value3"
            }
        }
    }

    try:
        response = upload_json(sample_data)
        print("JSON uploaded successfully:")
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
