from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)

XAI_API_KEY = os.getenv('XAI_API_KEY')
XAI_API_URL = "https://api.x.ai/v1"  # Note: Replace this with actual xAI endpoint

@app.route('/')
def home():
    return 'Hello! This is my xAI chatbot.'

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    # Basic error checking
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # We'll add the xAI API call here in the next step
    return jsonify({"response": f"Echo: {user_message}"})

if __name__ == '__main__':
    app.run(debug=True)
