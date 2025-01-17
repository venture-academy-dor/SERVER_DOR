from flask import Flask, request, jsonify
from imageAnalysis import encode_image, analyze_image, parse_response, get_level_from_risk_score
from imagecontroll import image_routes  # imagecontroll에서 Blueprint 가져오기

app = Flask(__name__)

# Blueprint 등록
app.register_blueprint(image_routes)

@app.route('/')
def home():
    return "Welcome to the Image Analysis API!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
