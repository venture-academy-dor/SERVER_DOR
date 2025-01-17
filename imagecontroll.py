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
        risk = request.form.get('risk')  # risk 값은 선택
        report_text = request.form.get('report_text')  # report_text 값은 선택

        # 이미지 데이터를 읽기
        image_data = file.read()

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
                int(risk) if risk else None,  # risk 값이 없으면 NULL
                report_text if report_text else None  # report_text 값이 없으면 NULL
            ))
            connection.commit()

        return jsonify({"message": "Image uploaded successfully"}), 201

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

# 이미지 조회 API (ID 기반)
@image_routes.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # risk, report_text 추가 조회
            query = "SELECT image_data, risk, report_text FROM image WHERE id = %s"
            cursor.execute(query, (image_id,))
            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Image not found"}), 404

            # 응답 데이터 구성
            image_data = result['image_data']  # 바이너리 이미지 데이터
            risk = result['risk']
            report_text = result['report_text']

            # JSON 응답
            return jsonify({
                "risk": risk,
                "report_text": report_text,
                "image_url": f"/images/{image_id}/data"
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
