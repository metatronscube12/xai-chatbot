from flask import Flask, request, jsonify, render_template
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

# Global variable to track last request time
last_request_time = 0
MIN_REQUEST_INTERVAL = 30  # 30 seconds between requests

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global last_request_time
    current_time = time.time()
    
    # Check if enough time has passed since last request
    if current_time - last_request_time < MIN_REQUEST_INTERVAL:
        remaining_time = round(MIN_REQUEST_INTERVAL - (current_time - last_request_time))
        return jsonify({
            "error": f"Please wait {remaining_time} seconds before sending another message"
        }), 429

    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Update last request time
        last_request_time = current_time
        
        # Make the API call
        completion = client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # Get the response
        response_text = completion.choices[0].message.content
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"Error: {str(e)}")  # This will show in your Render logs
        return jsonify({"error": "An error occurred. Please try again in 30 seconds."}), 500

if __name__ == '__main__':
    app.run(debug=True)
