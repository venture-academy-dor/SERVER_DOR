from flask import Flask
from imagecontroll import image_routes  # imagecontroll에서 Blueprint 가져오기

app = Flask(__name__)

# Blueprint 등록
app.register_blueprint(image_routes)

if __name__ == '__main__':
    app.run(debug=True)
