from flask import Flask, request, jsonify
import openai
import requests
from PIL import Image
import io
import base64

# Flask 앱 초기화
app = Flask(__name__)

# OpenAI API 키 설정
api_key = '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'


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Path to your image
image_path = "ice.jpeg"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4o-mini",
    "messages": [
        # {
        #     "role": "system",
        #     "content": "You are an image risk analysis assistant."
        # },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    # "text": "What’s in this image?"
                    "text": "이 그림을 한글로 설명하고, 위험도 정도를 1~100으로 알려주고 그 이유를 설명해줘. 결과를 JSON 형식으로 제공해줘. JSON의 key 값은 'description', 'risk_level', 'reasons'로 해줘."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    # "max_tokens": 300
    "temperature": 0.2  # Set temperature to a lower value for more consistent results
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

response_data = response.json()
content = response_data["choices"][0]["message"]["content"]

print(content)

# def encode_image(image):
#     """이미지를 base64로 인코딩합니다."""
#     buffered = io.BytesIO()
#     image.save(buffered, format=image.format)
#     return base64.b64encode(buffered.getvalue()).decode("utf-8")
#
# def analyze_image(image_data):
#     """
#     OpenAI API를 호출하여 이미지의 위험도를 분석합니다.
#     Args:
#         image_data (str): Base64로 인코딩된 이미지 데이터.
#     Returns:
#         dict: 위험도 분석 결과.
#     """
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an image risk analysis assistant."},
#                 {"role": "user", "content": f"Analyze the following image for risks: {image_data}"}
#             ],
#             max_tokens = 300,
#         )
#
#         print(response.choices[0].message['content'])
#         return response['choices'][0]['message']['content']
#     except Exception as e:
#         return f"Error analyzing image: {str(e)}"
#
# @app.route('/analyze', methods=['POST'])
# def analyze():
#     """
#     클라이언트로부터 이미지를 받고 위험도를 분석하여 결과를 반환합니다.
#     """
#     if 'image' not in request.files:
#         return jsonify({"error": "No image file provided"}), 400
#
#     # 이미지 파일 가져오기
#     image_file = request.files['image']
#     try:
#         # 이미지 열기
#         image = Image.open(image_file)
#         # 이미지를 Base64로 인코딩
#         encoded_image = encode_image(image)
#         # OpenAI API로 분석 요청
#         analysis_result = analyze_image(encoded_image)
#         return jsonify({"analysis_result": analysis_result}), 200
#     except Exception as e:
#         return jsonify({"error": f"Failed to process image: {str(e)}"}), 500
#
# # 서버 실행
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
