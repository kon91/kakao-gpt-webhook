from flask import Flask, request, jsonify
import openai
import os
import jwt  # PyJWT 필요
import base64

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    content_type = request.headers.get("Content-Type", "").lower()

    if content_type == "application/secevent+jwt":
        # 🔐 JWT Security Event (user-linked 등)
        token = request.data.decode("utf-8")
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            print("📬 Received Security Event Webhook:", payload)
            return "", 200
        except Exception as e:
            return jsonify({"error": f"Invalid JWT: {str(e)}"}), 400

    elif content_type == "application/json":
        # 💬 일반 카카오 챗봇 메시지 처리
        data = request.get_json()
        user_msg = data.get("userRequest", {}).get("utterance", "")

        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_msg}
            ]
        )
        answer = gpt_response.choices[0].message.content
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": answer
                        }
                    }
                ]
            }
        })

    else:
        return jsonify({"error": "Unsupported Content-Type"}), 415
