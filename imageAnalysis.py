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
                        "text": "이 그림을 한글로 설명하고, 미끄러움 정도를 기반으로 위험도 정도를 1~100으로 알려주고 그 이유를 설명해줘. 결과를 JSON 형식으로 제공해줘. JSON의 key 값은 'description', 'risk_level', 'reasons'로 해줘.",
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
