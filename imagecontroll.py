from flask import Blueprint, request, jsonify, send_file
import pymysql
import io
import os
from dotenv import load_dotenv

load_dotenv()

# Blueprint 생성
image_routes = Blueprint('image_routes', __name__)

# MySQL 연결 함수
def get_mysql_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

# 이미지 업로드 API
@image_routes.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files or 'road_number' not in request.form or 'risk' not in request.form:
        return jsonify({"error": "Missing required fields"}), 400

    file = request.files['image']
    road_number = request.form.get('road_number')
    risk = request.form.get('risk')

    if file.filename == '' or not road_number.isdigit() or not risk.isdigit():
        return jsonify({"error": "Invalid input"}), 400

    try:
        image_data = file.read()

        # MySQL에 데이터 삽입
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            query = "INSERT INTO image (image_data, road_number, risk) VALUES (%s, %s, %s)"
            cursor.execute(query, (image_data, int(road_number), int(risk)))
            connection.commit()

        return jsonify({"message": "Image uploaded successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 이미지 조회 API (ID 기반)
@image_routes.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            query = "SELECT image_data FROM image WHERE id = %s"
            cursor.execute(query, (image_id,))
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Image not found"}), 404

            # 이미지 데이터를 반환 (Base64 인코딩 또는 바이너리 스트림으로 전송)
            image_data = result['image_data']

            # 바이너리 데이터를 스트림으로 변환
            return send_file(
                io.BytesIO(image_data),
                mimetype='image/jpeg',  # JPEG 형식
                as_attachment=False,
                download_name=f'image_{image_id}.jpg'
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500