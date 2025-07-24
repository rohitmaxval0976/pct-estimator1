
from flask import Flask, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def serve_html():
    return send_file("PCT_Estimator_With_MaxVal_Branding.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
