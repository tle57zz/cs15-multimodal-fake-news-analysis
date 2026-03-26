from flask import Flask, request, send_file, render_template_string
import requests
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>Simple MHTML Saver</title>
</head>
<body>
    <h1>Cs15-2 Comparison of Different Types of True and Fake News, Both in Text and Visuals</h1>
    <h2>Save webpage as .mhtml</h2>
    <form method="post" action="/save">
        <input type="text" name="url" placeholder="https://example.com" style="width: 400px;" required>
        <button type="submit">Save</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)

@app.route("/save", methods=["POST"])
def save_page():
    url = request.form.get("url", "").strip()

    if not url.startswith(("http://", "https://")):
        return "Invalid URL. Please include http:// or https://", 400

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        # simple MHTML-like file content
        now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        mhtml_content = f"""From: <Saved by Flask>
Subject: {url}
Date: {now}
MIME-Version: 1.0
Content-Type: multipart/related; boundary="BOUNDARY"

--BOUNDARY
Content-Type: text/html; charset="utf-8"
Content-Location: {url}

{resp.text}

--BOUNDARY--
"""

        output_path = Path("saved_page.mhtml")
        output_path.write_text(mhtml_content, encoding="utf-8")

        return send_file(
            output_path,
            as_attachment=True,
            download_name="saved_page.mhtml"
        )

    except requests.RequestException as e:
        return f"Failed to fetch page: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)