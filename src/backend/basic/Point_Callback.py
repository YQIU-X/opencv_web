from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/point_callback', methods=['POST'])
def click_coordinates():
    data = request.json
    x = data.get('x')
    y = data.get('y')
    print(x)
    print(y)
    return jsonify({"status": "success", "x": x, "y": y})

if __name__ == '__main__':
    app.run(debug=False, port=5001, threaded=True)
