from flask import Flask, request, jsonify
import openai
import os
import json

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 카카오 요청은 application/x-www-form-urlencoded 형식으로 오며, payload라는 키에 JSON 문자열이 담김
        raw_payload = request.form['payload']
        data = json.loads(raw_payload)

        user_msg = data.get("userRequest", {}).get("utterance", "")
        
        # GPT 응답 생성
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}]
        )
        reply = gpt_response.choices[0].message["content"]

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": reply
                        }
                    }
                ]
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400
