#importing libraries 
from flask import Flask, request, jsonify, render_template_string
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from transformers import pipeline, BlenderbotTokenizer, BlenderbotForConditionalGeneration
from google.cloud import translate_v2 as translate
import random
from datetime import datetime
import os

app = Flask(__name__)

# Configure JWT
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with secure key in production
jwt = JWTManager(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['mental_health_db']
users = db['users']
chat_history = db['chat_history']
mood_logs = db['mood_logs']

# Initialize NLP models
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
conversational_model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-400M-distill")
tokenizer = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-400M-distill")

# Google Translate setup
translate_client = translate.Client()  # Set up with Google Cloud credentials

# Sample responses
responses = {
    "POSITIVE": ["Great to hear you're doing well!", "Love the positive energy!"],
    "NEGATIVE": ["I'm here for you. Want to talk more?", "That sounds tough. I'm listening."],
    "NEUTRAL": ["Thanks for sharing! What's on your mind?", "All good? Let's chat."]
}

# Mental health resources
resources = [
    {"name": "Crisis Text Line", "url": "https://www.crisistextline.org", "region": "US"},
    {"name": "BetterHelp", "url": "https://www.betterhelp.com", "region": "Global"}
]

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if users.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400
    users.insert_one({'username': username, 'password': password})  # Hash password in production
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = users.find_one({'username': username, 'password': password})
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    user = get_jwt_identity()
    data = request.json
    user_input = data.get('message', '')
    lang = data.get('language', 'en')

    if not user_input:
        return jsonify({'response': 'Please type something!'}), 400

    # Translate input to English if not in English
    if lang != 'en':
        user_input = translate_client.translate(user_input, target_language='en')['translatedText']

    # Sentiment analysis
    sentiment_result = sentiment_analyzer(user_input)[0]
    sentiment = sentiment_result['label']
    confidence = sentiment_result['score']

    # Generate conversational response
    inputs = tokenizer([user_input], return_tensors="pt")
    reply_ids = conversational_model.generate(**inputs)
    bot_response = tokenizer.decode(reply_ids[0], skip_special_tokens=True)

    # Fallback to predefined responses if needed
    if not bot_response.strip():
        bot_response = random.choice(responses.get(sentiment, responses["NEUTRAL"]))

    # Translate response back to user's language
    if lang != 'en':
        bot_response = translate_client.translate(bot_response, target_language=lang)['translatedText']

    # Add resource for negative sentiment
    if sentiment == "NEGATIVE" and confidence > 0.7:
        resource = random.choice([r for r in resources if r['region'] in ['Global', data.get('region', 'Global')]])
        bot_response += f"\n\nResource: [{resource['name']}]({resource['url']})"

    # Save chat and mood log
    chat_history.insert_one({
        'user': user,
        'message': user_input,
        'response': bot_response,
        'sentiment': sentiment,
        'confidence': confidence,
        'timestamp': datetime.utcnow()
    })
    mood_logs.insert_one({
        'user': user,
        'sentiment': sentiment,
        'confidence': confidence,
        'timestamp': datetime.utcnow()
    })

    return jsonify({'response': bot_response, 'sentiment': sentiment.lower(), 'confidence': round(confidence, 2)})

@app.route('/mood_trend', methods=['GET'])
@jwt_required()
def mood_trend():
    user = get_jwt_identity()
    logs = list(mood_logs.find({'user': user}).sort('timestamp', -1).limit(30))
    return jsonify([{
        'sentiment': log['sentiment'],
        'confidence': log['confidence'],
        'timestamp': log['timestamp'].isoformat()
    } for log in logs])

if __name__ == '__main__':
    app.run(debug=True)