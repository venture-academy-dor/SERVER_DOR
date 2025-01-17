from flask import Blueprint, request, jsonify, send_file
import pymysql
import io
import os
from dotenv import load_dotenv
from imageAnalysis import analyze

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
    if 'image' not in request.files:
        return jsonify({"error": "Missing image file"}), 400

    # 파일 가져오기
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # 이미지 위험도를 OPENAI API로 분석
        risk = analyze(file)

        # 파일을 읽기 위해 포인터를 처음으로 이동
        file.seek(0)

        # 이미지 데이터를 읽기
        image_data = file.read()

        if image_data is None:
            return jsonify({"error": "Invalid image file"}), 400

        # JSON 데이터 가져오기
        report_text = request.form.get('report_text')  # report_text 값은 선택

        # MySQL에 데이터 삽입
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # risk와 report_text 처리
            query = """
                INSERT INTO image (image_data, risk, report_text)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (
                image_data,
                risk if risk else 0,  # risk 값이 없으면 NULL
                report_text if report_text else None  # report_text 값이 없으면 NULL
            ))
            connection.commit()

        return jsonify({"message": "Image uploaded successfully"}), 201

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@image_routes.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            query = "SELECT image_data, report_text FROM image WHERE id = %s"
            cursor.execute(query, (image_id,))
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Image not found"}), 404

            image_data = result['image_data']
            report_text = result['report_text']

            # JSON 응답 (report_text 포함)
            return jsonify({
                "report_text": report_text,
                "image_url": f"/images/{image_id}/data"  # 이미지 URL
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 위험도 데이터만 반환 API
@image_routes.route('/images/<int:image_id>/risk', methods=['GET'])
def get_image_risk(image_id):
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            query = "SELECT risk FROM image WHERE id = %s"
            cursor.execute(query, (image_id,))
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Image not found"}), 404

            risk = result['risk']

            # JSON 응답 (risk만 반환)
            return jsonify({
                "risk": risk
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 이미지 데이터만 반환 (추가 엔드포인트)
@image_routes.route('/images/<int:image_id>/data', methods=['GET'])
def get_image_data(image_id):
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            query = "SELECT image_data FROM image WHERE id = %s"
            cursor.execute(query, (image_id,))
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Image not found"}), 404

            image_data = result['image_data']

            # 바이너리 데이터를 스트림으로 반환
            return send_file(
                io.BytesIO(image_data),
                mimetype='image/jpeg',
                as_attachment=False,
                download_name=f'image_{image_id}.jpg'
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
