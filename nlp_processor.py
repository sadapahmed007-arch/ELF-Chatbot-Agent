import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
import re

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

class NLPProcessor:
    def __init__(self):
        try:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set(['the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but'])
        
        print("✅ NLP Processor initialized (with Search & Summary support)!")
    
    def extract_entities(self, text):
        """Extract basic entities from text"""
        entities = []
        
        # Extract capitalized words (likely names/places)
        words = text.split()
        for i, word in enumerate(words):
            if word and word[0].isupper() and i > 0:
                entities.append({
                    'text': word,
                    'label': 'ENTITY',
                    'description': 'Capitalized word (possible name/place)'
                })
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        for date in dates:
            entities.append({
                'text': date,
                'label': 'DATE',
                'description': 'Date reference'
            })
        
        # Extract URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        for url in urls:
            entities.append({
                'text': url,
                'label': 'URL',
                'description': 'Web URL'
            })
        
        return entities
    
    def extract_keywords(self, text, top_n=5):
        """Extract keywords from text"""
        try:
            words = word_tokenize(text.lower())
        except:
            words = text.lower().split()
        
        words = [word for word in words if word.isalnum() and word not in self.stop_words and len(word) > 2]
        
        word_freq = Counter(words)
        keywords = [word for word, freq in word_freq.most_common(top_n)]
        
        return keywords
    
    def get_pos_tags(self, text):
        """Get part-of-speech tags (simplified)"""
        try:
            words = word_tokenize(text)
            pos_tags = nltk.pos_tag(words)
            
            return [{'word': word, 'pos': pos, 'tag': pos} for word, pos in pos_tags]
        except:
            return []
    
    def detect_intent(self, text):
        """Detect user intent from text"""
        text_lower = text.lower()
        
        intents = {
            'web_search': ['search for', 'find', 'look up', 'google', 'search', 'look for', 'find me'],
            'summarize': ['summarize', 'summary', 'tldr', 'brief', 'sum up', 'give me a summary', 'key points'],
            'weather': ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy', 'hot', 'cold', 'climate'],
            'news': ['news', 'headlines', 'latest', 'happening', 'current events', 'today', 'update'],
            'greeting': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good evening', 'good afternoon'],
            'farewell': ['bye', 'goodbye', 'see you', 'farewell', 'exit', 'quit', 'leave'],
            'math': ['calculate', 'solve', 'compute', 'math', '+', '-', '*', '/', '=', 'equation'],
            'help': ['help', 'what can you do', 'capabilities', 'features', 'how do', 'commands'],
            'time': ['time', 'date', 'day', 'clock', 'when', 'today'],
            'sentiment_check': ['how do i feel', 'my mood', 'analyze my message', 'sentiment', 'analyze my mood']
        }
        
        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_intents.append(intent)
        
        return detected_intents if detected_intents else ['general']
    
    def analyze_sentence_structure(self, text):
        """Analyze sentence structure (simplified)"""
        sentences = text.split('.')
        words = text.split()
        
        return {
            'num_sentences': len([s for s in sentences if s.strip()]),
            'num_words': len(words),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0
        }