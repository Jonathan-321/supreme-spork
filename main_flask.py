from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to AgriFinance - Simplified Version"

@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "message": "Basic Flask application is running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)