from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route("/")
def serve_html():
    return send_file("PCT_Estimator_With_MaxVal_Branding.html")

@app.route("/api/fetch-pct", methods=["GET"])
def fetch_pct_data():
    pct_number = request.args.get("pct", "")
    if not pct_number:
        return jsonify({"error": "Missing PCT number"}), 400

    try:
        base_url = f"https://patentscope.wipo.int/search/en/detail.jsf?docId={pct_number}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        resp = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()

        priority_date = re.search(r"Priority Date\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
        filing_date = re.search(r"International Filing Date\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
        claims_count = re.search(r"Number of Claims\s+([0-9]+)", text)

        description = soup.find(id="descriptionTabContent")
        abstract = soup.find(id="abstractTabContent")
        claims = soup.find(id="claimsTabContent")

        desc_text = description.get_text(separator=" ") if description else ""
        abstract_text = abstract.get_text(separator=" ") if abstract else ""
        claims_text = claims.get_text(separator=" ") if claims else ""

        all_text = f"{abstract_text} {desc_text} {claims_text}"
        words = re.findall(r"\w+", all_text)
        total_word_count = len(words)

        return jsonify({
            "priority_date": priority_date.group(1) if priority_date else None,
            "filing_date": filing_date.group(1) if filing_date else None,
            "number_of_claims": int(claims_count.group(1)) if claims_count else None,
            "word_count": total_word_count
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
