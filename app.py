from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from database import Database
from chatbot_agent import ChatbotAgent
from config import FLASK_CONFIG

app = Flask(__name__)
CORS(app)

# Initialize components
db = Database()
chatbot = ChatbotAgent()
recognizer = sr.Recognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process message through chatbot agent
        bot_response = chatbot.process_message(user_message)
        
        # Get NLP analysis
        analysis = chatbot.get_last_analysis()
        
        # Save to database with sentiment
        sentiment_data = analysis.get('sentiment', {}).get('vader', {})
        db.save_conversation(
            user_message, 
            bot_response,
            sentiment_data.get('sentiment'),
            sentiment_data.get('compound'),
            analysis.get('entities')
        )
        
        # Save sentiment analytics
        if sentiment_data:
            db.save_sentiment_analytics(user_message, sentiment_data)
        
        return jsonify({
            'response': bot_response,
            'analysis': {
                'sentiment': sentiment_data.get('sentiment'),
                'entities': analysis.get('entities', []),
                'intents': analysis.get('intents', []),
                'keywords': analysis.get('keywords', [])
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        
        return send_file(temp_file.name, mimetype='audio/mpeg')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-sentiment', methods=['POST'])
def analyze_sentiment():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Analyze sentiment
        sentiment_data = chatbot.sentiment.get_detailed_sentiment(text)
        
        return jsonify(sentiment_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        limit = request.args.get('limit', 10, type=int)
        history = db.get_conversation_history(limit)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sentiment-stats', methods=['GET'])
def sentiment_stats():
    try:
        stats = db.get_sentiment_stats()
        return jsonify({'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/weather/<city>', methods=['GET'])
def get_weather(city):
    try:
        weather_data = chatbot.apis.get_weather(city)
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/news', methods=['GET'])
def get_news():
    try:
        category = request.args.get('category', 'general')
        news_data = chatbot.apis.get_news(category=category)
        return jsonify(news_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Advanced AI Chatbot Agent...")
    print("📍 Visit: http://localhost:5000")
    print("✨ Features: NLP, Sentiment Analysis, Weather, News, TTS")
    app.run(**FLASK_CONFIG)