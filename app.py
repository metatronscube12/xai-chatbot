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

# Increase rate limiting
last_request_time = 0
MIN_REQUEST_INTERVAL = 5  # Increased to 5 seconds between requests

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global last_request_time
    
    # Strict rate limiting
    current_time = time.time()
    time_since_last_request = current_time - last_request_time
    
    if time_since_last_request < MIN_REQUEST_INTERVAL:
        wait_time = MIN_REQUEST_INTERVAL - time_since_last_request
        return jsonify({
            "error": f"Please wait {round(wait_time)} seconds before sending another message"
        }), 429
    
    last_request_time = current_time
    
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        response = client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."},
                {"role": "user", "content": user_message},
            ],
            stream=False  # Changed to non-streaming for now
        )
        
        # Extract the response content
        if hasattr(response, 'choices') and len(response.choices) > 0:
            return jsonify({"response": response.choices[0].message.content})
        else:
            return jsonify({"error": "No response content received"}), 500
                
    except Exception as e:
        error_message = str(e)
        if "429" in error_message:
            return jsonify({
                "error": "Rate limit reached. Please wait 30 seconds before trying again."
            }), 429
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
