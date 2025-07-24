
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return send_file("PCT_Estimator_With_MaxVal_Branding.html")

@app.route("/fetch_pct_data", methods=["POST"])
def fetch_pct_data():
    data = request.get_json()
    pct_number = data.get("pct_number", "")

    if not pct_number:
        return jsonify({"error": "Missing PCT number"}), 400

    try:
        # Build search URL
        search_url = f"https://patentscope.wipo.int/search/en/search.jsf"
        session = requests.Session()
        response = session.get(search_url, params={"queryString": pct_number}, timeout=20)

        # Check redirect to detail page
        if "detail.jsf" not in response.url:
            return jsonify({"error": "Could not locate patent on WIPO"}), 404

        detail_page = session.get(response.url, timeout=20)
        soup = BeautifulSoup(detail_page.text, "html.parser")

        # Parse data
        filing_date = soup.find("span", {"id": "detailForm:applicationDate"}).text.strip()
        priority_date = soup.find("span", {"id": "detailForm:priorityDate"}).text.strip()
        claims = soup.find("span", {"id": "detailForm:claimNumber"}).text.strip()

        # Estimate word count from abstract + description
        abstract = soup.find("span", {"id": "detailForm:abstractText"}).text.strip() if soup.find("span", {"id": "detailForm:abstractText"}) else ""
        description = soup.find("span", {"id": "detailForm:descriptionText"}).text.strip() if soup.find("span", {"id": "detailForm:descriptionText"}) else ""
        claims_text = soup.find("span", {"id": "detailForm:claimsText"}).text.strip() if soup.find("span", {"id": "detailForm:claimsText"}) else ""

        all_text = f"{abstract} {description} {claims_text}"
        word_count = len(all_text.split())

        return jsonify({
            "filing_date": filing_date,
            "priority_date": priority_date,
            "claim_count": int(claims),
            "word_count": word_count
        })
    except Exception as e:
        return jsonify({"error": "Failed to fetch from WIPO", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
