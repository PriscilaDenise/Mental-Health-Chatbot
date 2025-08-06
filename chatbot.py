from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import random

app = Flask(__name__)

# Initialize sentiment analysis model
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Sample responses for different sentiments
responses = {
    "POSITIVE": [
        "I'm glad you're feeling good! Want to share more?",
        "That's awesome to hear! What's got you in such a great mood?",
        "Love the positive vibes! Anything exciting happening?"
    ],
    "NEGATIVE": [
        "I'm here for you. Want to talk about what has been going on?",
        "It sounds like you're having a tough time. I'm listening if you need me.",
        "I'm sorry you're feeling down. Can I help with anything?"
    ],
    "NEUTRAL": [
        "Thanks for sharing! How can I support you today?",
        "Sounds like you're just chilling. What's on your mind?",
        "All good? Let me know what's up!"
    ]
}

# Predefined resources for escalation
resources = [
    "Consider reaching out to a professional: [BetterHelp](https://www.betterhelp.com)",
    "You might find this helpline useful: [Crisis Text Line](https://www.crisistextline.org) - Text HOME to 741741",
    "Check out mental health resources at [NAMI](https://www.nami.org)"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    if not user_input:
        return jsonify({'response': 'Please type something!'})

    # Analyze sentiment
    sentiment_result = sentiment_analyzer(user_input)[0]
    sentiment = sentiment_result['label']
    confidence = sentiment_result['score']

    # Select response based on sentiment
    bot_response = random.choice(responses.get(sentiment, responses["NEUTRAL"]))

    # Add resource suggestion for negative sentiment with high confidence
    if sentiment == "NEGATIVE" and confidence > 0.7:
        bot_response += "\n\n" + random.choice(resources)

    return jsonify({'response': bot_response, 'sentiment': sentiment.lower(), 'confidence': round(confidence, 2)})

if __name__ == '__main__':
    app.run(debug=True)