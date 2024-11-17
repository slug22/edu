import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
URL = 'https://api.pinata.cloud'
BASE_UPLOAD_URL = f'{URL}/pinning/pinJSONToIPFS'
GROUP_ID = '192cbf02-f8f3-481f-aafa-884994c1f65d'

JWT = os.getenv("PINATA_JWT")

if not JWT:
    raise ValueError("Environment variable PINATA_JWT is not set. Please check your .env file.")

HEADERS = {
    "Authorization": f"Bearer {JWT}",
    "Content-Type": "application/json"
}

def upload_question(payload):
    """
    Uploads a JSON object to Pinata.

    Args:
        data (dict): The JSON object to upload.

    Returns:
        dict: Response data from Pinata.
    """

    try:
        response = requests.post(BASE_UPLOAD_URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to upload JSON: {e}")

def retrieve_question_set():
    """
    Retrieves a set of question JSON

    Args:
        none

    Returns:
        list: List of dictionaries that represent the questions in JSON format
    """

# Testing 
if __name__ == "__main__":
    # Define test JSON sample_data

    # Creating the group
    print(requests.post(f'{URL}/groups', json={"name": "questions"}, headers=HEADERS).json())

    sample_data = {
        "pinataMetadata" : {
            "name" : "bruhh.json"
        },
        "pinataOptions": {
            "groupId" : f'{GROUP_ID}'
        },
        "pinataContent": {
            "description": "This is an example JSON object uploaded to Pinata.",
            "data": {
                "key1": "value1",
                "key2": "value2",
                "nested": {
                    "key3": "value3"
                }
            }
        }
    }

    try:
        response = upload_question(sample_data)
        print("JSON uploaded successfully:")
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
