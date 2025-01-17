from flask import Flask, request, jsonify
from imageAnalysis import encode_image, analyze_image, parse_response
from imagecontroll import image_routes  # imagecontroll에서 Blueprint 가져오기

app = Flask(__name__)

# Blueprint 등록
app.register_blueprint(image_routes)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    try:
        # Get the image file from the request
        image_file = request.files['image']

        # Encode the image as base64
        base64_image = encode_image(image_file)

        # Call OpenAI API for analysis
        api_response = analyze_image(base64_image)

        # Parse the API response
        parsed_response = parse_response(api_response)

        return jsonify(parsed_response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid response: {str(ve)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 500

@app.route('/')
def home():
    return "Welcome to the Image Analysis API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
