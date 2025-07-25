from flask import Flask, request, jsonify
import openai
import os
import jwt  # PyJWT 필요
import base64

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    content_type = request.headers.get("Content-Type")

    # 1. 카카오 보안 이벤트 (ex: 로그인 연결됨)
    if content_type == "application/secevent+jwt":
        token = request.data.decode("utf-8")
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            print("✅ Received Security Event Webhook:", payload)
            return "", 200
        except Exception as e:
            return jsonify({"error": f"❌ Invalid JWT: {str(e)}"}), 400

    # 2. 일반 채팅 메시지 처리
    elif content_type == "application/json":
        try:
            data = request.get_json()
            user_msg = data.get("userRequest", {}).get("utterance", "")
            print("💬 사용자 메시지:", user_msg)

            # GPT 호출
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "친절한 어조로 짧게 대답해줘"},
                    {"role": "user", "content": user_msg}
                ]
            )
            reply_text = gpt_response.choices[0].message.content.strip()

            # 카카오 챗봇 응답 형식
            return jsonify({
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": reply_text
                            }
                        }
                    ]
                }
            })
        except Exception as e:
            return jsonify({
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": f"⚠️ 오류가 발생했어요: {str(e)}"
                            }
                        }
                    ]
                }
            })

    # 그 외 Content-Type 처리
    return "Unsupported Media Type", 415
