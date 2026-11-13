from collections import Counter
import re
import nltk
from textblob import TextBlob

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class TextSummarizer:
    def __init__(self):
        try:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set(['the', 'is', 'at', 'which', 'on', 'a', 'an'])
        
        print("✅ Text Summarizer initialized!")
    
    def summarize(self, text, num_sentences=3, method='extractive'):
        """Summarize text using specified method"""
        if method == 'extractive':
            return self.extractive_summary(text, num_sentences)
        elif method == 'abstractive':
            return self.abstractive_summary(text, num_sentences)
        else:
            return self.extractive_summary(text, num_sentences)
    
    def extractive_summary(self, text, num_sentences=3):
        """Extract most important sentences from text"""
        try:
            # Split into sentences
            sentences = self._split_sentences(text)
            
            if len(sentences) <= num_sentences:
                return {
                    'success': True,
                    'summary': text,
                    'original_length': len(text),
                    'summary_length': len(text),
                    'compression_ratio': 1.0,
                    'method': 'extractive',
                    'note': 'Text is already short'
                }
            
            # Score sentences
            sentence_scores = self._score_sentences(sentences)
            
            # Get top sentences
            top_sentences = sorted(sentence_scores.items(), 
                                  key=lambda x: x[1], 
                                  reverse=True)[:num_sentences]
            
            # Sort by original order
            top_sentences = sorted(top_sentences, 
                                  key=lambda x: sentences.index(x[0]))
            
            # Create summary
            summary = ' '.join([sent for sent, score in top_sentences])
            
            return {
                'success': True,
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': round(len(summary) / len(text), 2),
                'method': 'extractive',
                'num_sentences': len(top_sentences)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': text[:500]  # Return first 500 chars as fallback
            }
    
    def abstractive_summary(self, text, max_length=150):
        """Generate abstractive summary (simplified version)"""
        try:
            # Extract key phrases
            blob = TextBlob(text)
            noun_phrases = list(blob.noun_phrases)[:5]
            
            # Get most important sentences
            sentences = self._split_sentences(text)
            sentence_scores = self._score_sentences(sentences)
            
            top_sentence = max(sentence_scores.items(), key=lambda x: x[1])[0]
            
            # Create summary
            if noun_phrases:
                summary = f"Key topics: {', '.join(noun_phrases[:3])}. {top_sentence}"
            else:
                summary = top_sentence
            
            # Limit length
            if len(summary) > max_length:
                summary = summary[:max_length] + '...'
            
            return {
                'success': True,
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': round(len(summary) / len(text), 2),
                'method': 'abstractive',
                'key_phrases': noun_phrases[:5]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': text[:max_length]
            }
    
    def _split_sentences(self, text):
        """Split text into sentences"""
        try:
            from nltk.tokenize import sent_tokenize
            return sent_tokenize(text)
        except:
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences):
        """Score sentences based on word frequency"""
        # Calculate word frequencies
        all_words = []
        for sentence in sentences:
            words = re.findall(r'\w+', sentence.lower())
            all_words.extend([w for w in words if w not in self.stop_words])
        
        word_freq = Counter(all_words)
        
        # Score each sentence
        sentence_scores = {}
        for sentence in sentences:
            words = re.findall(r'\w+', sentence.lower())
            words = [w for w in words if w not in self.stop_words]
            
            if words:
                score = sum(word_freq[word] for word in words) / len(words)
                sentence_scores[sentence] = score
        
        return sentence_scores
    
    def summarize_url(self, url_content, num_sentences=3):
        """Summarize content fetched from URL"""
        if not url_content.get('success'):
            return {
                'success': False,
                'error': 'Could not fetch URL content'
            }
        
        text = url_content['content']
        summary = self.extractive_summary(text, num_sentences)
        
        if summary['success']:
            summary['title'] = url_content.get('title', 'No title')
            summary['url'] = url_content.get('url', '')
        
        return summary
    
    def get_key_points(self, text, num_points=5):
        """Extract key points from text"""
        try:
            sentences = self._split_sentences(text)
            sentence_scores = self._score_sentences(sentences)
            
            # Get top sentences
            top_sentences = sorted(sentence_scores.items(), 
                                  key=lambda x: x[1], 
                                  reverse=True)[:num_points]
            
            key_points = [sent for sent, score in top_sentences]
            
            return {
                'success': True,
                'key_points': key_points,
                'num_points': len(key_points)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_summary(self, summary_data):
        """Format summary for display"""
        if not summary_data.get('success'):
            return f"❌ Summarization failed: {summary_data.get('error', 'Unknown error')}"
        
        output = "📝 **Text Summary**\n\n"
        
        if 'title' in summary_data:
            output += f"**Title:** {summary_data['title']}\n"
            output += f"**URL:** {summary_data['url']}\n\n"
        
        output += f"**Summary ({summary_data['method']} method):**\n"
        output += f"{summary_data['summary']}\n\n"
        
        output += f"**Statistics:**\n"
        output += f"• Original length: {summary_data['original_length']} characters\n"
        output += f"• Summary length: {summary_data['summary_length']} characters\n"
        output += f"• Compression: {summary_data['compression_ratio']*100:.0f}% of original\n"
        
        if 'key_phrases' in summary_data:
            output += f"\n**Key Phrases:** {', '.join(summary_data['key_phrases'])}\n"
        
        return output