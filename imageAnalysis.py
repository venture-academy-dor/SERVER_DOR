import base64
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Function to encode image as base64
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

# Function to call OpenAI API
def analyze_image(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze the slipperiness of this image and assess the risk level on a scale from 1 to 100 based on its slipperiness. Provide the results in JSON format with the following keys: 'description' (a detailed explanation of the image), 'risk_score' (the slipperiness-based risk score), and 'reasons' (an explanation of why the risk score was assigned).",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        "temperature": 0.2,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
    )
    response.raise_for_status()  # Raise exception for HTTP errors
    return response.json()

# Function to parse OpenAI API response
def parse_response(api_response):
    content = api_response["choices"][0]["message"]["content"]

    # Locate the JSON content
    json_start = content.find("{")
    json_end = content.rfind("}")
    if json_start != -1 and json_end != -1:
        cleaned_json = content[json_start:json_end + 1]
        return json.loads(cleaned_json)  # Safely parse JSON string
    else:
        raise ValueError("Invalid response format from OpenAI API")

# Function to get risk level from risk score
def get_level_from_risk_score(risk_score):
    if risk_score >= 75:
        level = 3
    elif risk_score >= 55:
        level = 2
    elif risk_score >= 35:
        level = 1
    else:
        level = 0
    return level

# Function to analyze image
def analyze(file):
    try:
        # Get the image file from the request
        image_file = file

        # Encode the image as base64
        base64_image = encode_image(image_file)

        # Call OpenAI API for analysis
        api_response = analyze_image(base64_image)

        # Parse the API response
        parsed_response = parse_response(api_response)

        print(parsed_response)

        risk_level = get_level_from_risk_score(parsed_response["risk_score"])

        return risk_level

    except Exception as e:
        raise Exception(f"An error occurred during image analysis: {str(e)}")
