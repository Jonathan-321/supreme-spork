from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to AgriFinance Basic App"

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Basic app is running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)