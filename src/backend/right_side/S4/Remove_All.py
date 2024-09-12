from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)


IMAGE_FILE_PATH = 'src/backend/data/IMAGEs.pkl'

@app.route('/remove_all', methods=['POST'])
def remove_all():

    if os.path.exists(IMAGE_FILE_PATH):
        os.remove(IMAGE_FILE_PATH)
        return jsonify({"message": "文件已删除并刷新页面"}), 200
    else:
        return jsonify({"message": "文件不存在"}), 404


if __name__ == '__main__':
    app.run(debug=False, port=5017, threaded=True)