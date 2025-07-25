from flask import Flask, request
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    user_input = data['userRequest']['utterance']

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}]
    )

    answer = response['choices'][0]['message']['content'].strip()

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": answer}}
            ]
        }
    }

if __name__ == "__main__":
    app.run()
