from flask import Blueprint, request, jsonify, send_file
import pymysql
import io
# Blueprint 생성
image_routes = Blueprint('image_routes', __name__)

# MySQL 연결 함수
def get_mysql_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='gksl1004**',
        database='dor_workshop',
        cursorclass=pymysql.cursors.DictCursor
    )

# 이미지 업로드 API
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
        # JSON 데이터 가져오기
        road_number = request.form.get('road_number')
        risk = request.form.get('risk')  # risk 값은 선택적으로 처리

        # 입력값 검증
        if not road_number:
            return jsonify({"error": "Missing required JSON fields"}), 400

        if not road_number.isdigit():
            return jsonify({"error": "Invalid input"}), 400

        # 이미지 데이터를 읽기
        image_data = file.read()

        # MySQL에 데이터 삽입
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # risk 값이 없으면 NULL로 처리
            if not risk:
                query = "INSERT INTO image (image_data, road_number, risk) VALUES (%s, %s, NULL)"
                cursor.execute(query, (image_data, int(road_number)))
            else:
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