from flask import Flask, request, jsonify, render_template, Response
from dotenv import load_dotenv
import os
from openai import OpenAI
import time
from collections import deque
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv('XAI_API_KEY'),
    base_url="https://api.x.ai/v1"
)

# Rate limiting setup
last_request_time = 0
MIN_REQUEST_INTERVAL = 1
hourly_requests = deque(maxlen=1200)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global last_request_time
    current_time = time.time()
    
    # Rate limit checks
    if current_time - last_request_time < MIN_REQUEST_INTERVAL:
        return jsonify({"error": "Please wait a moment before sending another message"}), 429

    current_datetime = datetime.now()
    one_hour_ago = current_datetime - timedelta(hours=1)
    
    while hourly_requests and hourly_requests[0] < one_hour_ago:
        hourly_requests.popleft()
    
    if len(hourly_requests) >= 1200:
        return jsonify({"error": "Hourly request limit reached"}), 429

    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Update rate limiting trackers
        last_request_time = current_time
        hourly_requests.append(current_datetime)

        def generate():
            stream = client.chat.completions.create(
                model="grok-2-latest",
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
            yield "data: [DONE]\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
