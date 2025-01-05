from flask import Flask, request, jsonify, render_template, Response
from dotenv import load_dotenv
import os
from openai import OpenAI
import time

load_dotenv()

app = Flask(__name__)

XAI_API_KEY = os.getenv('XAI_API_KEY')
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

# Simple rate limiting
last_request_time = 0
MIN_REQUEST_INTERVAL = 1  # Minimum time between requests in seconds

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global last_request_time
    
    # Check rate limit
    current_time = time.time()
    if current_time - last_request_time < MIN_REQUEST_INTERVAL:
        return jsonify({"error": "Please wait a moment before sending another message"}), 429
    
    last_request_time = current_time
    
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        # Add retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                stream = client.chat.completions.create(
                    model="grok-2-latest",
                    messages=[
                        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."},
                        {"role": "user", "content": user_message},
                    ],
                    stream=True
                )
                
                def generate():
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            yield f"data: {chunk.choices[0].delta.content}\n\n"
                
                return Response(generate(), mimetype='text/event-stream')
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                raise
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
