import os
import base64
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        data = request.get_json()
        image_base64 = data.get("image")

        if not image_base64:
            return jsonify({"error": "Görsel bulunamadı"}), 400

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Bu görselde bir müze eseri, tarihi yapı veya sanat eseri var mı? "
                                "Varsa sadece JSON formatında şu bilgileri ver, başka hiçbir şey yazma:\n"
                                "{\"recognized\": true, \"name\": \"eserin İngilizce adı\", \"confidence\": 0.95}\n"
                                "Eğer tanıyamadıysan sadece şunu yaz:\n"
                                "{\"recognized\": false}"
                            )
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(GEMINI_URL, json=payload, timeout=15)
        result = response.json()

        # Hata kontrolü
        if "error" in result:
            return jsonify({"error": result["error"]}), 500

        if "candidates" not in result or len(result["candidates"]) == 0:
            return jsonify({"recognized": False})

        text = result["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip().replace("```json", "").replace("```", "").strip()
        
        try:
            parsed = json.loads(text)
        except:
            # JSON parse edilemezse tanıyamadı say
            return jsonify({"recognized": False})

        return jsonify(parsed)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)