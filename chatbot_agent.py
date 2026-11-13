import re
import requests
from bs4 import BeautifulSoup
import sympy as sp
import random
from datetime import datetime
from nlp_processor import NLPProcessor
from sentiment_analyzer import SentimentAnalyzer
from external_apis import ExternalAPIs
from web_search_engine import WebSearchEngine
from text_summarizer import TextSummarizer

class ChatbotAgent:
    def __init__(self):
        self.name = "ELF"
        self.full_name = "Enhanced Learning Friend"
        self.nlp = NLPProcessor()
        self.sentiment = SentimentAnalyzer()
        self.apis = ExternalAPIs()
        self.search_engine = WebSearchEngine()
        self.summarizer = TextSummarizer()
        
        # Conversation context for human-like interaction
        self.conversation_history = []
        self.user_preferences = {}
        self.last_topic = None
        self.conversation_depth = 0
        
        print("✅ ELF (Enhanced Learning Friend) initialized!")
        print("💬 Ready for human-like conversation!")
        
    def process_message(self, message):
        """Process message with context awareness and human-like responses"""
        # Store in conversation history
        self.conversation_history.append({
            'message': message,
            'timestamp': datetime.now(),
            'type': 'user'
        })
        
        # Keep only last 10 messages for context
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        # Extract entities and analyze
        entities = self.nlp.extract_entities(message)
        intents = self.nlp.detect_intent(message)
        sentiment_data = self.sentiment.get_detailed_sentiment(message)
        
        # Store analysis results
        self.last_analysis = {
            'entities': entities,
            'intents': intents,
            'sentiment': sentiment_data,
            'keywords': self.nlp.extract_keywords(message)
        }
        
        # Detect follow-up questions
        is_followup = self._is_followup_question(message)
        
        # Process based on intent with context
        response = self._generate_contextual_response(message, intents, sentiment_data, is_followup)
        
        # Add response to history
        self.conversation_history.append({
            'message': response,
            'timestamp': datetime.now(),
            'type': 'bot'
        })
        
        self.conversation_depth += 1
        
        return response
    
    def _is_followup_question(self, message):
        """Detect if message is a follow-up question"""
        followup_indicators = [
            'what about', 'how about', 'also', 'and', 'tell me more',
            'explain', 'elaborate', 'another', 'more', 'else',
            'why', 'that', 'this', 'it', 'can you'
        ]
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in followup_indicators)
    
    def _generate_contextual_response(self, message, intents, sentiment_data, is_followup):
        """Generate contextually aware, human-like response"""
        # Handle based on primary intent
        if 'web_search' in intents or 'search' in intents:
            response = self.handle_web_search(message)
            self.last_topic = 'search'
        elif 'summarize' in intents:
            response = self.handle_summarization(message)
            self.last_topic = 'summary'
        elif 'weather' in intents:
            response = self.handle_weather(message, self.last_analysis['entities'])
            self.last_topic = 'weather'
        elif 'news' in intents:
            response = self.handle_news(message)
            self.last_topic = 'news'
        elif 'sentiment_check' in intents:
            response = self.analyze_user_sentiment(sentiment_data)
            self.last_topic = 'sentiment'
        elif 'greeting' in intents:
            response = self.greet_with_sentiment(sentiment_data)
            self.last_topic = 'greeting'
        elif 'farewell' in intents:
            response = self.farewell()
            self.last_topic = 'farewell'
        elif 'math' in intents:
            response = self.solve_math(message)
            self.last_topic = 'math'
        elif 'help' in intents:
            response = self.show_capabilities()
            self.last_topic = 'help'
        elif 'time' in intents:
            response = self.get_current_time()
            self.last_topic = 'time'
        else:
            response = self.conversational_response(message, sentiment_data, is_followup)
        
        # Add human-like follow-up suggestions
        response = self._add_conversation_continuity(response, intents)
        
        return response
    
    def _add_conversation_continuity(self, response, intents):
        """Add follow-up suggestions to keep conversation flowing"""
        # Don't add to certain responses
        skip_intents = ['greeting', 'farewell', 'help']
        if any(intent in intents for intent in skip_intents):
            return response
        
        # Random follow-up suggestions based on context
        followups = []
        
        if self.last_topic == 'search':
            followups = [
                "\n\n💬 Want me to summarize any of these results?",
                "\n\n💬 Need more details about any of these?",
                "\n\n💬 Interested in related topics?"
            ]
        elif self.last_topic == 'weather':
            followups = [
                "\n\n💬 Want weather for another city?",
                "\n\n💬 Curious about the forecast?",
                "\n\n💬 Need travel advice?"
            ]
        elif self.last_topic == 'news':
            followups = [
                "\n\n💬 Want news from a different category?",
                "\n\n💬 Interested in related topics?",
                "\n\n💬 Need more details on any story?"
            ]
        
        # Add a random follow-up occasionally (30% chance)
        if followups and random.random() < 0.3:
            return response + random.choice(followups)
        
        return response
    
    def handle_web_search(self, message):
        """Handle web search with improved Google search"""
        # Extract search query
        query = re.sub(r'(search for|search|find|look up|google|look for)', '', message, flags=re.IGNORECASE)
        query = query.strip()
        
        if not query or len(query) < 2:
            return "🤔 What would you like me to search for? Be as specific as you'd like!\n\nExample: 'search for Python machine learning tutorials'"
        
        # Add personality to searching
        searching_messages = [
            f"🔍 Searching the web for '{query}'...",
            f"🔎 Let me find the best results about '{query}'...",
            f"🌐 Looking up '{query}' for you...",
        ]
        
        # Perform search
        search_results = self.search_engine.search_web(query, num_results=5)
        
        # Format and return with AI summary
        if search_results['success']:
            return self.search_engine.format_search_results(search_results)
        else:
            return f"😕 I had trouble searching for '{query}'. Could you try:\n• Rephrasing your query\n• Checking your internet connection\n• Being more specific\n\nOr ask me something else!"
    
    def handle_summarization(self, message):
        """Handle text summarization"""
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message)
        
        if urls:
            url = urls[0]
            return f"📝 Fetching and summarizing content from {url}...\n\n" + self._summarize_url(url)
        else:
            text = re.sub(r'(summarize|summary|tldr|brief)', '', message, flags=re.IGNORECASE).strip()
            
            if len(text) < 50:
                return "📝 I can summarize content for you! Just:\n\n1. Paste a URL: 'summarize https://example.com'\n2. Or paste text: 'summarize: [your long text]'\n\nWhat would you like me to summarize?"
            
            summary = self.summarizer.summarize(text, num_sentences=3)
            return self.summarizer.format_summary(summary)
    
    def _summarize_url(self, url):
        """Summarize URL content"""
        url_content = self.search_engine.fetch_page_content(url)
        if url_content['success']:
            summary = self.summarizer.summarize_url(url_content, num_sentences=3)
            return self.summarizer.format_summary(summary)
        else:
            return f"😕 I couldn't access that webpage. Make sure:\n• The URL is correct\n• The site doesn't require login\n• It's not behind a paywall\n\nWant to try another URL?"
    
    def handle_weather(self, message, entities):
        """Handle weather with conversational tone"""
        city = None
        for entity in entities:
            if entity['label'] in ['GPE', 'LOC', 'ENTITY']:
                city = entity['text']
                break
        
        if not city:
            return "🌤️ Which city's weather would you like to know? Just tell me the city name!"
        
        weather_data = self.apis.get_weather(city)
        response = self.apis.format_weather_response(weather_data)
        
        # Add conversational element
        if not weather_data.get('error'):
            temp = weather_data['temperature']
            if temp > 25:
                response += "\n\n☀️ Quite warm! Stay hydrated!"
            elif temp < 10:
                response += "\n\n🧥 Chilly! Don't forget your jacket!"
        
        return response
    
    def handle_news(self, message):
        """Handle news requests"""
        message_lower = message.lower()
        categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology']
        category = 'general'
        
        for cat in categories:
            if cat in message_lower:
                category = cat
                break
        
        news_data = self.apis.get_news(category=category)
        return self.apis.format_news_response(news_data)
    
    def analyze_user_sentiment(self, sentiment_data):
        """Provide empathetic sentiment analysis"""
        sentiment = sentiment_data['vader']['sentiment']
        compound = sentiment_data['vader']['compound']
        emoji = sentiment_data['vader']['emoji']
        
        response = f"💭 **Your Emotional State:**\n\n"
        response += f"I sense you're feeling **{sentiment}** {emoji}\n"
        response += f"Confidence Level: {abs(compound):.0%}\n\n"
        
        response += f"**Emotional Breakdown:**\n"
        response += f"• Positivity: {sentiment_data['vader']['positive']:.0%}\n"
        response += f"• Neutrality: {sentiment_data['vader']['neutral']:.0%}\n"
        response += f"• Negativity: {sentiment_data['vader']['negative']:.0%}\n\n"
        
        # Empathetic response
        if sentiment == 'positive':
            response += "😊 That's wonderful! Your positive energy is contagious! Keep spreading those good vibes!"
        elif sentiment == 'negative':
            response += "💙 I understand things might be tough right now. Remember, it's okay to feel this way. I'm here if you want to talk about it."
        else:
            response += "😌 You seem calm and balanced. That's a good place to be!"
        
        return response
    
    def greet_with_sentiment(self, sentiment_data):
        """Warm, personalized greetings"""
        sentiment = sentiment_data['vader']['sentiment']
        hour = datetime.now().hour
        
        # Time-based greeting
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        greetings = {
            'positive': [
                f"{time_greeting}! 😊 You seem cheerful! I'm ELF, and I'm excited to help you today! What's on your mind?",
                f"Hey there! {time_greeting}! 🌟 Love your positive energy! I'm ELF, your friendly AI assistant. How can I make your day even better?",
            ],
            'negative': [
                f"{time_greeting}. I'm ELF, and I'm here for you. 💙 Whatever you need, I'll do my best to help. What can I do?",
                f"Hello. {time_greeting}. I'm ELF, your AI friend. If something's troubling you, feel free to share. I'm listening.",
            ],
            'neutral': [
                f"{time_greeting}! I'm ELF (Enhanced Learning Friend) 🤖 I can help with searches, summaries, weather, news, math, and more! What brings you here today?",
                f"Hi! {time_greeting}! I'm ELF, your AI assistant! Whether you need information, a friendly chat, or help with tasks, I'm here! What would you like to explore?",
            ]
        }
        
        return random.choice(greetings.get(sentiment, greetings['neutral']))
    
    def farewell(self):
        """Warm goodbye messages"""
        farewells = [
            "Goodbye, friend! 👋 It's been wonderful chatting with you! Come back anytime you need me!",
            "See you later! 🌟 Feel free to return whenever you like. I'll be here! Take care!",
            "Farewell! ✨ Thanks for the great conversation! Remember, ELF is always here when you need help!",
            "Bye for now! 💙 I hope I was helpful! Don't hesitate to come back. Stay awesome!",
        ]
        return random.choice(farewells)
    
    def solve_math(self, expression):
        """Solve math with friendly responses"""
        try:
            expression = re.sub(r'(calculate|solve|what is|compute|math)', '', expression, flags=re.IGNORECASE)
            expression = expression.replace('x', '*').replace('×', '*').replace('÷', '/')
            expression = expression.strip('? ')
            
            result = sp.sympify(expression)
            evaluated = result.evalf()
            
            return f"🔢 **Math Solution:**\n\n{expression} = **{evaluated}**\n\n✅ There's your answer! Need me to solve anything else?"
        except Exception as e:
            return f"🤔 Hmm, I had trouble solving that. Could you rephrase it? Try something like:\n• calculate 15 * 23\n• solve 2^10\n• what is 100 / 8"
    
    def get_current_time(self):
        """Get current time with personality"""
        now = datetime.now()
        date_str = now.strftime('%A, %B %d, %Y')
        time_str = now.strftime('%I:%M %p')
        
        return f"⏰ **Right now it's:**\n\n📅 {date_str}\n🕐 {time_str}\n\n💭 Time flies when you're having fun, right?"
    
    def show_capabilities(self):
        """Show capabilities with friendly tone"""
        return """👋 **Hi! I'm ELF (Enhanced Learning Friend)**

I'm here to be your intelligent companion! Here's what I can do:

**🔍 Web Search**
- Search Google for anything
- Get AI-powered summaries
- Find the latest information
Try: "search for Python tutorials"

**📝 Smart Summarization**
- Summarize articles and websites
- Extract key points from text
- Multiple summarization methods
Try: "summarize https://example.com"

**🌤️ Weather Updates**
- Real-time weather anywhere
- Temperature and conditions
- Humidity and wind info
Try: "weather in Paris"

**📰 Latest News**
- Breaking headlines
- Category-specific news
- Multiple news sources
Try: "technology news"

**🔢 Math Solver**
- Complex calculations
- Equations and expressions
- Instant results
Try: "calculate 25 * 17 + 89"

**😊 Emotional Intelligence**
- Sentiment analysis
- Empathetic responses
- Mood tracking
Try: "I'm feeling great!"

**💬 Natural Conversation**
- Context-aware chat
- Follow-up questions
- Human-like interaction
Just chat naturally!

**🎤 Voice Input & 🔊 Output**
- Speak your questions
- Listen to my responses

I'm always learning and improving! What would you like to explore together? 🌟"""
    
    def conversational_response(self, message, sentiment_data, is_followup):
        """Enhanced conversational responses with context"""
        sentiment = sentiment_data['vader']['sentiment']
        emoji = sentiment_data['vader']['emoji']
        message_lower = message.lower()
        
        # Empathetic acknowledgment
        sentiment_responses = {
            'positive': ["That's great!", "Wonderful!", "Awesome!", "I love that!"],
            'negative': ["I understand.", "I hear you.", "That's tough.", "I'm sorry to hear that."],
            'neutral': ["I see.", "Okay.", "Got it.", "Alright."]
        }
        
        acknowledgment = random.choice(sentiment_responses[sentiment])
        
        # Specific responses
        responses = {
            "how are you": f"I'm doing fantastic, thanks for asking! {emoji} I'm always excited to help! How are YOU doing?",
            "thank": f"{acknowledgment} You're very welcome! It's my pleasure to help! Need anything else? 😊",
            "joke": "Haha! Want to hear one? Why did the AI cross the road? To optimize the other side! 😄 Got any more requests?",
            "love": f"Aww, that's so sweet! {emoji} I'm glad I could help! What else can I do for you?",
            "awesome": f"Right?! {emoji} I'm excited too! What's next on your mind?",
            "smart": "Thank you! I try my best! 😊 But I'm only as good as my ability to help YOU. What do you need?",
        }
        
        for key, response in responses.items():
            if key in message_lower:
                return f"{acknowledgment} {emoji} {response}"
        
        # Context-aware responses
        if is_followup and self.last_topic:
            if self.last_topic == 'search':
                return f"{acknowledgment} Want me to search for something else? Or maybe summarize one of those results? Just let me know!"
            elif self.last_topic == 'weather':
                return f"{acknowledgment} Need weather for another location? Or something completely different? I'm here!"
            elif self.last_topic == 'news':
                return f"{acknowledgment} Want news from a different category? Or shall we explore something else?"
        
        # Extract keywords for intelligent response
        keywords = self.nlp.extract_keywords(message)
        
        if keywords:
            key_topics = ', '.join(keywords[:2])
            return f"{acknowledgment} {emoji} I see you're interested in: {key_topics}. I can help you:\n\n🔍 Search for information about this\n📝 Summarize articles\n💬 Discuss it further\n🌐 Find related resources\n\nWhat would you like to do?"
        
        # Friendly default response
        friendly_defaults = [
            f"{acknowledgment} {emoji} I'm here to help! I can search the web, summarize content, check weather, get news, solve math, or just chat! What interests you?",
            f"{acknowledgment} {emoji} Tell me more! Or if you'd like, I can help with searches, summaries, weather, news, calculations, and more! What's on your mind?",
            f"{acknowledgment} {emoji} I'm listening! Whether you need information, analysis, or just want to chat, I'm here! What can I do for you?",
        ]
        
        return random.choice(friendly_defaults)
    
    def get_last_analysis(self):
        """Return the last NLP analysis"""
        return getattr(self, 'last_analysis', {})
    
    def get_conversation_context(self):
        """Get conversation context"""
        return {
            'history': self.conversation_history[-5:],  # Last 5 exchanges
            'last_topic': self.last_topic,
            'depth': self.conversation_depth
        }

        
    def process_message(self, message):
        """Process message with NLP and intent detection"""
        # Extract entities and analyze
        entities = self.nlp.extract_entities(message)
        intents = self.nlp.detect_intent(message)
        sentiment_data = self.sentiment.get_detailed_sentiment(message)
        
        # Store analysis results
        self.last_analysis = {
            'entities': entities,
            'intents': intents,
            'sentiment': sentiment_data,
            'keywords': self.nlp.extract_keywords(message)
        }
        
        # Process based on primary intent
        if 'web_search' in intents or 'search' in intents:
            return self.handle_web_search(message)
        elif 'summarize' in intents:
            return self.handle_summarization(message)
        elif 'weather' in intents:
            return self.handle_weather(message, entities)
        elif 'news' in intents:
            return self.handle_news(message)
        elif 'sentiment_check' in intents:
            return self.analyze_user_sentiment(sentiment_data)
        elif 'greeting' in intents:
            return self.greet_with_sentiment(sentiment_data)
        elif 'farewell' in intents:
            return self.farewell()
        elif 'math' in intents:
            return self.solve_math(message)
        elif 'help' in intents:
            return self.show_capabilities()
        elif 'time' in intents:
            return self.get_current_time()
        else:
            return self.conversational_response(message, sentiment_data)
    
    def handle_web_search(self, message):
        """Handle web search requests"""
        # Extract search query
        query = re.sub(r'(search for|search|find|look up|google)', '', message, flags=re.IGNORECASE)
        query = query.strip()
        
        if not query:
            return "Please specify what you'd like me to search for. Example: 'search for Python tutorials'"
        
        # Perform search
        search_results = self.search_engine.search_web(query, num_results=5)
        
        # Format and return results
        return self.search_engine.format_search_results(search_results)
    
    def handle_summarization(self, message):
        """Handle text summarization requests"""
        # Check if URL is provided
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message)
        
        if urls:
            # Summarize URL content
            url = urls[0]
            url_content = self.search_engine.fetch_page_content(url)
            summary = self.summarizer.summarize_url(url_content, num_sentences=3)
            return self.summarizer.format_summary(summary)
        else:
            # Extract text to summarize
            text = re.sub(r'(summarize|summary|tldr|brief)', '', message, flags=re.IGNORECASE)
            text = text.strip()
            
            if len(text) < 50:
                return "Please provide more text to summarize, or provide a URL. Example: 'summarize https://example.com' or paste long text after 'summarize:'"
            
            # Summarize provided text
            summary = self.summarizer.summarize(text, num_sentences=3)
            return self.summarizer.format_summary(summary)
    
    def handle_weather(self, message, entities):
        """Handle weather requests"""
        city = None
        for entity in entities:
            if entity['label'] in ['GPE', 'LOC', 'ENTITY']:
                city = entity['text']
                break
        
        weather_data = self.apis.get_weather(city)
        return self.apis.format_weather_response(weather_data)
    
    def handle_news(self, message):
        """Handle news requests"""
        message_lower = message.lower()
        
        categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology']
        category = 'general'
        
        for cat in categories:
            if cat in message_lower:
                category = cat
                break
        
        news_data = self.apis.get_news(category=category)
        return self.apis.format_news_response(news_data)
    
    def analyze_user_sentiment(self, sentiment_data):
        """Provide sentiment analysis of user's message"""
        sentiment = sentiment_data['vader']['sentiment']
        compound = sentiment_data['vader']['compound']
        emoji = sentiment_data['vader']['emoji']
        
        response = f"📊 Sentiment Analysis:\n\n"
        response += f"Overall Mood: {sentiment.upper()} {emoji}\n"
        response += f"Confidence: {abs(compound):.2%}\n\n"
        response += f"Breakdown:\n"
        response += f"• Positive: {sentiment_data['vader']['positive']:.2%}\n"
        response += f"• Neutral: {sentiment_data['vader']['neutral']:.2%}\n"
        response += f"• Negative: {sentiment_data['vader']['negative']:.2%}\n\n"
        response += self.sentiment.generate_sentiment_response(sentiment_data)
        
        return response
    
    def greet_with_sentiment(self, sentiment_data):
        """Greet user based on their sentiment"""
        sentiment = sentiment_data['vader']['sentiment']
        
        if sentiment == 'positive':
            responses = [
                "Hello! You seem cheerful today! 😊 How can I help?",
                "Hi there! Great energy! What can I do for you?",
                "Hey! You're in a good mood! What's on your mind?"
            ]
        elif sentiment == 'negative':
            responses = [
                "Hello. I'm here to help. What's troubling you?",
                "Hi. I sense something might be wrong. How can I assist?",
                "Hey. I'm listening. What can I do for you?"
            ]
        else:
            responses = [
                "Hello! How can I assist you today?",
                "Hi there! What would you like to know?",
                "Hey! What can I help you with?"
            ]
        
        return random.choice(responses)
    
    def farewell(self):
        responses = [
            "Goodbye! It was great chatting with you! 👋",
            "See you later! Feel free to come back anytime! 😊",
            "Farewell! Take care! 🌟",
            "Bye! Have an amazing day! ✨"
        ]
        return random.choice(responses)
    
    def solve_math(self, expression):
        try:
            expression = re.sub(r'(calculate|solve|what is|compute|math)', '', expression, flags=re.IGNORECASE)
            expression = expression.replace('x', '*').replace('×', '*').replace('÷', '/')
            expression = expression.strip('? ')
            
            result = sp.sympify(expression)
            evaluated = result.evalf()
            
            return f"🔢 Mathematical Result:\n{expression} = {evaluated}"
        except Exception as e:
            return f"I couldn't solve that math problem. Please rephrase it."
    
    def get_current_time(self):
        from datetime import datetime
        now = datetime.now()
        return f"⏰ Current date and time:\n{now.strftime('%A, %B %d, %Y at %I:%M %p')}"
    
    def show_capabilities(self):
        return """🤖 I'm your Advanced AI Assistant with:

**🧠 Advanced NLP Capabilities:**
- Entity Recognition - I can identify names, places, dates
- Intent Detection - I understand what you want
- Sentiment Analysis - I can analyze emotions in text
- Keyword Extraction - I identify important topics

**🌟 Core Features:**
- 💬 Natural Conversations with emotion awareness
- 🌤️ Real-time Weather (try: "weather in Paris")
- 📰 Latest News (try: "tech news" or "sports news")
- 🔢 Math Solver (try: "calculate 15 * 8 + 20")
- 🔍 **Web Search** (try: "search for Python tutorials")
- 📝 **Text Summarization** (try: "summarize <URL>" or paste text)
- 😊 Sentiment Analysis (try: "analyze my mood")
- 🎤 Voice Input & 🔊 Voice Output
- 📊 Entity & Intent Recognition

**🔍 Web Search Examples:**
- "search for latest AI news"
- "find information about quantum computing"
- "look up best restaurants in Tokyo"

**📝 Summarization Examples:**
- "summarize https://example.com/article"
- "give me a summary of: [paste long text]"
- "tldr this: [paste content]"

Try asking me anything!"""
    
    def conversational_response(self, message, sentiment_data):
        """Enhanced conversational response with sentiment awareness"""
        sentiment = sentiment_data['vader']['sentiment']
        emoji = sentiment_data['vader']['emoji']
        
        sentiment_prefix = ""
        if sentiment == 'positive':
            sentiment_prefix = "That's wonderful! "
        elif sentiment == 'negative':
            sentiment_prefix = "I understand. "
        
        message_lower = message.lower()
        
        responses = {
            "how are you": "I'm functioning perfectly! Thanks for asking. How can I assist you?",
            "thank": "You're very welcome! Anything else I can help with?",
            "joke": "Why did the AI go to school? To improve its learning algorithms! 😄",
        }
        
        for key, response in responses.items():
            if key in message_lower:
                return sentiment_prefix + response
        
        keywords = self.nlp.extract_keywords(message)
        if keywords:
            return f"{sentiment_prefix}I see you mentioned: {', '.join(keywords[:3])}. I can help with web search, summaries, weather, news, math, or just chat! {emoji}"
        
        return f"I understand. {emoji} How can I assist you today? I can search the web, summarize articles, check weather, get news, solve math, or just chat!"
    
def get_last_analysis(self):
    """Return the last NLP analysis"""
    return getattr(self, 'last_analysis', {})