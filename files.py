import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
URL = 'https://api.pinata.cloud'
BASE_UPLOAD_URL = f'{URL}/pinning/pinJSONToIPFS'
GROUP_ID = '2016a6be-fcb5-435d-a799-326313c7daf5'


JWT = os.getenv("PINATA_JWT")

if not JWT:
    raise ValueError("Environment variable PINATA_JWT is not set. Please check your .env file.")

HEADERS = {
    "Authorization": f"Bearer {JWT}",
    "Content-Type": "application/json"
}

def upload_question(question_data):
    payload = {
        "pinataMetadata" : {
            "name" : "question.json"
        },
        "pinataOptions": {
            "groupId" : f'{GROUP_ID}'
        },
        "pinataContent": question_data
    }

    try:
        response = requests.post(BASE_UPLOAD_URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to upload JSON: {e}")

def retrieve_question_set():
    pass

# Testing 
if __name__ == "__main__":
    # Define test JSON sample_data

    sample_data = {
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
        response = upload_question(sample_data)
        print("JSON uploaded successfully:")
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
