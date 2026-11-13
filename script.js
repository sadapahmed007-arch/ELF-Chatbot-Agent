const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const voiceBtn = document.getElementById('voiceBtn');
const ttsBtn = document.getElementById('ttsBtn');
const historyBtn = document.getElementById('historyBtn');
const statsBtn = document.getElementById('statsBtn');
const searchHistoryBtn = document.getElementById('searchHistoryBtn');
const summaryHistoryBtn = document.getElementById('summaryHistoryBtn');
const clearBtn = document.getElementById('clearBtn');
const themeBtn = document.getElementById('themeBtn');
const sentimentEmoji = document.getElementById('sentimentEmoji');
const sentimentText = document.getElementById('sentimentText');
const sentimentFill = document.getElementById('sentimentFill');
const sentimentScore = document.getElementById('sentimentScore');
const typingIndicator = document.getElementById('typingIndicator');
const toastContainer = document.getElementById('toastContainer');

// Search & Summary elements
const searchInput = document.getElementById('searchInput');
const searchGoBtn = document.getElementById('searchGoBtn');
const searchResults = document.getElementById('searchResults');
const summaryUrlInput = document.getElementById('summaryUrlInput');
const summaryGoBtn = document.getElementById('summaryGoBtn');
const summaryResult = document.getElementById('summaryResult');

let ttsEnabled = true;
let currentAudio = null;
let messageCount = 0;

// Initialize particles
function createParticles() {
    const particles = document.getElementById('particles');
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = '3px';
        particle.style.height = '3px';
        particle.style.background = 'rgba(255, 255, 255, 0.5)';
        particle.style.borderRadius = '50%';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animation = `float ${5 + Math.random() * 10}s infinite ease-in-out`;
        particle.style.animationDelay = Math.random() * 5 + 's';
        particles.appendChild(particle);
    }
}

// Toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    toast.innerHTML = `${icons[type]} ${message}`;
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Send message
function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    userInput.value = '';
    
    typingIndicator.style.display = 'flex';

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        typingIndicator.style.display = 'none';
        
        if (data.response) {
            addMessage(data.response, 'bot');
            updateAnalysisPanel(data.analysis);
            updateSentimentIndicator(data.analysis.sentiment);
            
            if (ttsEnabled) {
                speakText(data.response);
            }
            
            messageCount++;
            if (messageCount % 5 === 0) {
                showToast('Keep the conversation going! 🎉', 'success');
            }
        }
    })
    .catch(error => {
        typingIndicator.style.display = 'none';
        addMessage('Error: ' + error, 'bot');
        showToast('Connection error. Please try again.', 'error');
    });
}

// Web Search functionality
function performWebSearch() {
    const query = searchInput.value.trim();
    if (!query) {
        showToast('Please enter a search query', 'warning');
        return;
    }

    searchResults.innerHTML = '<p style="color: white; padding: 10px;">Searching...</p>';
    showToast('Searching the web... 🔍', 'info');

    fetch('/web-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, num_results: 5 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.results.length > 0) {
            displaySearchResults(data.results);
            addMessage(`🔍 Found ${data.count} results for "${query}"`, 'bot');
            showToast(`Found ${data.count} results! ✅`, 'success');
        } else {
            searchResults.innerHTML = '<p style="color: rgba(255,255,255,0.7); padding: 10px;">No results found</p>';
            showToast('No results found', 'warning');
        }
    })
    .catch(error => {
        searchResults.innerHTML = '<p style="color: rgba(255,255,255,0.7); padding: 10px;">Search failed</p>';
        showToast('Search failed: ' + error, 'error');
    });
}

function displaySearchResults(results) {
    searchResults.innerHTML = '';
    results.forEach((result, index) => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.innerHTML = `
            <h5>${index + 1}. ${result.title}</h5>
            <p>${result.snippet.substring(0, 100)}...</p>
            <a href="${result.url}" target="_blank">${result.url.substring(0, 50)}...</a>
        `;
        searchResults.appendChild(item);
    });
}

// Summarization functionality
function performSummarization() {
    const input = summaryUrlInput.value.trim();
    if (!input) {
        showToast('Please enter text or URL to summarize', 'warning');
        return;
    }

    const method = document.querySelector('input[name="summaryMethod"]:checked').value;
    const numSentences = parseInt(document.getElementById('summaryLength').value);

    summaryResult.innerHTML = '<p style="color: white; padding: 10px;">Summarizing...</p>';
    showToast('Generating summary... 📝', 'info');

    // Check if input is URL
    const isUrl = input.startsWith('http://') || input.startsWith('https://');

    fetch('/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: isUrl ? input : '',
            text: isUrl ? '' : input,
            num_sentences: numSentences,
            method: method
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displaySummary(data);
            addMessage(`📝 Summary generated (${data.compression_ratio * 100}% of original)`, 'bot');
            showToast('Summary ready! ✅', 'success');
        } else {
            summaryResult.innerHTML = `<p style="color: rgba(255,255,255,0.7);">Error: ${data.error}</p>`;
            showToast('Summarization failed', 'error');
        }
    })
    .catch(error => {
        summaryResult.innerHTML = '<p style="color: rgba(255,255,255,0.7);">Summarization failed</p>';
        showToast('Error: ' + error, 'error');
    });
}

function displaySummary(data) {
    let html = '';
    if (data.title) {
        html += `<strong>Title:</strong> ${data.title}<br><br>`;
    }
    html += `<strong>Summary:</strong><br>${data.summary}<br><br>`;
    html += `<small>Method: ${data.method} | Compression: ${(data.compression_ratio * 100).toFixed(0)}%</small>`;
    
    summaryResult.innerHTML = html;
}

// Add message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = sender === 'bot' ? 'avatar bot-avatar' : 'avatar user-avatar';
    avatar.textContent = sender === 'bot' ? '🧝' : '👤';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    
    const nameSpan = document.createElement('strong');
    nameSpan.textContent = sender === 'bot' ? 'ELF' : 'You';
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'timestamp';
    timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    headerDiv.appendChild(nameSpan);
    headerDiv.appendChild(timeSpan);
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = formatMessage(text);
    
    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(textDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Format message text
function formatMessage(text) {
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    text = text.replace(/\n/g, '<br>');
    return text;
}

// Update analysis panel
function updateAnalysisPanel(analysis) {
    const sentimentText = analysis.sentiment ? analysis.sentiment.toUpperCase() : '-';
    document.getElementById('analysisSentiment').textContent = sentimentText;
    
    const entities = analysis.entities && analysis.entities.length > 0 
        ? analysis.entities.map(e => e.text).join(', ') 
        : 'None detected';
    document.getElementById('analysisEntities').textContent = entities;
    
    const intents = analysis.intents && analysis.intents.length > 0 
        ? analysis.intents.join(', ') 
        : 'general';
    document.getElementById('analysisIntent').textContent = intents;
    
    const keywords = analysis.keywords && analysis.keywords.length > 0 
        ? analysis.keywords.join(', ') 
        : 'None';
    document.getElementById('analysisKeywords').textContent = keywords;
}

// Update sentiment indicator
function updateSentimentIndicator(sentiment) {
    const sentiments = {
        'positive': { 
            emoji: '😊', 
            text: 'Positive Vibes', 
            color: '#4ade80',
            score: 0.8
        },
        'negative': { 
            emoji: '😞', 
            text: 'Needs Support', 
            color: '#f87171',
            score: 0.3
        },
        'neutral': { 
            emoji: '😐', 
            text: 'Neutral Mood', 
            color: '#fbbf24',
            score: 0.5
        }
    };
    
    const data = sentiments[sentiment] || sentiments['neutral'];
    sentimentEmoji.textContent = data.emoji;
    sentimentText.textContent = data.text;
    sentimentFill.style.width = (data.score * 100) + '%';
    sentimentFill.style.background = `linear-gradient(90deg, ${data.color}, ${data.color}dd)`;
    sentimentScore.textContent = data.score.toFixed(1);
}

// Text-to-speech
function speakText(text) {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    
    const cleanText = text.replace(/[\u{1F300}-\u{1F9FF}]/gu, '').substring(0, 200);
    
    fetch('/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: cleanText })
    })
    .then(response => response.blob())
    .then(blob => {
        const audioUrl = URL.createObjectURL(blob);
        currentAudio = new Audio(audioUrl);
        currentAudio.play();
    })
    .catch(error => console.log('TTS Error:', error));
}

// Voice recognition
function startVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        showToast('Voice recognition not supported. Use Chrome browser.', 'error');
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    voiceBtn.classList.add('recording');
    showToast('Listening... Speak now! 🎤', 'info');

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        voiceBtn.classList.remove('recording');
        showToast('Voice captured! ✅', 'success');
        sendMessage();
    };

    recognition.onerror = function(event) {
        voiceBtn.classList.remove('recording');
        showToast('Voice error: ' + event.error, 'error');
    };

    recognition.onend = function() {
        voiceBtn.classList.remove('recording');
    };

    recognition.start();
}

// Toggle TTS
function toggleTTS() {
    ttsEnabled = !ttsEnabled;
    ttsBtn.classList.toggle('active', ttsEnabled);
    showToast(ttsEnabled ? 'Voice output enabled 🔊' : 'Voice output disabled 🔇', 'info');
}

// View search history
function viewSearchHistory() {
    fetch('/search-history?limit=10')
    .then(response => response.json())
    .then(data => {
        if (data.searches && data.searches.length > 0) {
            let msg = '🔍 Recent Searches:\n\n';
            data.searches.forEach((search, index) => {
                msg += `${index + 1}. "${search.query}" (${search.num_results} results)\n`;
            });
            addMessage(msg, 'bot');
            showToast('Search history loaded! 🔍', 'success');
        } else {
            showToast('No search history yet', 'info');
        }
    })
    .catch(() => showToast('Error loading search history', 'error'));
}

// View summary history
function viewSummaryHistory() {
    fetch('/summary-history?limit=10')
    .then(response => response.json())
    .then(data => {
        if (data.summaries && data.summaries.length > 0) {
            let msg = '📝 Recent Summaries:\n\n';
            data.summaries.forEach((summary, index) => {
                const source = summary.url || 'Text';
                msg += `${index + 1}. ${source} (${summary.method})\n`;
            });
            addMessage(msg, 'bot');
            showToast('Summary history loaded! 📝', 'success');
        } else {
            showToast('No summary history yet', 'info');
        }
    })
    .catch(() => showToast('Error loading summary history', 'error'));
}

// View history
function viewHistory() {
    fetch('/history?limit=10')
    .then(response => response.json())
    .then(data => {
        if (data.history && data.history.length > 0) {
            showToast('Loading conversation history...', 'info');
            chatBox.innerHTML = '';
            data.history.reverse().forEach((item) => {
                addMessage(item.user_message, 'user');
                addMessage(item.bot_response, 'bot');
            });
        } else {
            showToast('No conversation history found.', 'warning');
        }
    })
    .catch(() => showToast('Error loading history.', 'error'));
}

// View sentiment stats
function viewSentimentStats() {
    fetch('/sentiment-stats')
    .then(response => response.json())
    .then(data => {
        if (data.stats && data.stats.length > 0) {
            let statsMsg = '📊 Sentiment Statistics:\n\n';
            data.stats.forEach(stat => {
                const emoji = stat.sentiment === 'positive' ? '😊' : 
                             stat.sentiment === 'negative' ? '😞' : '😐';
                statsMsg += `${emoji} ${stat.sentiment.toUpperCase()}: ${stat.count} messages (Score: ${stat.avg_score.toFixed(2)})\n`;
            });
            addMessage(statsMsg, 'bot');
            showToast('Sentiment stats loaded! 📊', 'success');
        } else {
            showToast('No sentiment data yet. Keep chatting!', 'info');
        }
    })
    .catch(() => showToast('Error loading stats.', 'error'));
}

// Clear chat
function clearChat() {
    chatBox.innerHTML = '';
    messageCount = 0;
    showToast('Chat cleared! Starting fresh. 🗑️', 'success');
    addMessage('Chat cleared! 🧹 I\'m ELF, and I\'m still here ready to help with anything you need - searches, summaries, weather, news, math, or just a friendly chat! What would you like to explore? 🚀', 'bot');
}

// Theme toggle
function toggleTheme() {
    showToast('Theme customization coming soon! 🎨', 'info');
}

// Quick action chips
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('chip')) {
        const action = e.target.getAttribute('data-action');
        userInput.value = action;
        sendMessage();
    }
});

// Feature card interactions
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('click', function() {
        const feature = this.getAttribute('data-feature');
        const messages = {
            'nlp': 'Tell me about your NLP capabilities, ELF',
            'sentiment': 'Analyze my mood: I\'m feeling great!',
            'search': 'search for latest AI developments',
            'summary': 'How does your summarization work?',
            'weather': 'What\'s the weather in London?',
            'news': 'Show me technology news',
            'voice': 'Tell me about your voice features',
            'math': 'Calculate 15 * 23 + 100'
        };
        userInput.value = messages[feature];
        sendMessage();
    });
});

// Event listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
voiceBtn.addEventListener('click', startVoiceRecognition);
ttsBtn.addEventListener('click', toggleTTS);
historyBtn.addEventListener('click', viewHistory);
statsBtn.addEventListener('click', viewSentimentStats);
searchHistoryBtn.addEventListener('click', viewSearchHistory);
summaryHistoryBtn.addEventListener('click', viewSummaryHistory);
clearBtn.addEventListener('click', clearChat);
themeBtn.addEventListener('click', toggleTheme);

// Search & Summary event listeners
searchGoBtn.addEventListener('click', performWebSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performWebSearch();
});
summaryGoBtn.addEventListener('click', performSummarization);

// Initialize
window.addEventListener('load', () => {
    console.log('🧝 ELF (Enhanced Learning Friend) is online!');
    console.log('✨ Features: Web Search with AI Summaries, Text Summarization, NLP, Sentiment, Weather, News, Voice I/O');
    console.log('💬 Interactive, human-like conversation enabled!');
    
    createParticles();
    showToast('Hey there! I\'m ELF, your new AI friend! 👋🧝', 'success');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeIn 0.6s ease-out';
            }
        });
    });
    
    document.querySelectorAll('.feature-card').forEach(card => {
        observer.observe(card);
    });
});

// Initialize particles
function createParticles() {
    const particles = document.getElementById('particles');
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = '3px';
        particle.style.height = '3px';
        particle.style.background = 'rgba(255, 255, 255, 0.5)';
        particle.style.borderRadius = '50%';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animation = `float ${5 + Math.random() * 10}s infinite ease-in-out`;
        particle.style.animationDelay = Math.random() * 5 + 's';
        particles.appendChild(particle);
    }
}

// Toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    toast.innerHTML = `${icons[type]} ${message}`;
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Send message
function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    userInput.value = '';
    
    // Show typing indicator
    typingIndicator.style.display = 'flex';

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        // Hide typing indicator
        typingIndicator.style.display = 'none';
        
        if (data.response) {
            addMessage(data.response, 'bot');
            
            // Update analysis panel
            updateAnalysisPanel(data.analysis);
            
            // Update sentiment indicator
            updateSentimentIndicator(data.analysis.sentiment);
            
            // Text-to-speech
            if (ttsEnabled) {
                speakText(data.response);
            }
            
            messageCount++;
            if (messageCount % 5 === 0) {
                showToast('Keep the conversation going! 🎉', 'success');
            }
        }
    })
    .catch(error => {
        typingIndicator.style.display = 'none';
        addMessage('Error: ' + error, 'bot');
        showToast('Connection error. Please try again.', 'error');
    });
}

// Add message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = sender === 'bot' ? 'avatar bot-avatar' : 'avatar user-avatar';
    avatar.textContent = sender === 'bot' ? '🤖' : '👤';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    
    const nameSpan = document.createElement('strong');
    nameSpan.textContent = sender === 'bot' ? 'AI Assistant' : 'You';
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'timestamp';
    timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    headerDiv.appendChild(nameSpan);
    headerDiv.appendChild(timeSpan);
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.innerHTML = formatMessage(text);
    
    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(textDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Format message text
function formatMessage(text) {
    // Convert URLs to links
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    // Convert newlines to <br>
    text = text.replace(/\n/g, '<br>');
    return text;
}

// Update analysis panel
function updateAnalysisPanel(analysis) {
    const sentimentText = analysis.sentiment ? analysis.sentiment.toUpperCase() : '-';
    document.getElementById('analysisSentiment').textContent = sentimentText;
    
    const entities = analysis.entities && analysis.entities.length > 0 
        ? analysis.entities.map(e => e.text).join(', ') 
        : 'None detected';
    document.getElementById('analysisEntities').textContent = entities;
    
    const intents = analysis.intents && analysis.intents.length > 0 
        ? analysis.intents.join(', ') 
        : 'general';
    document.getElementById('analysisIntent').textContent = intents;
    
    const keywords = analysis.keywords && analysis.keywords.length > 0 
        ? analysis.keywords.join(', ') 
        : 'None';
    document.getElementById('analysisKeywords').textContent = keywords;
}

// Update sentiment indicator
function updateSentimentIndicator(sentiment) {
    const sentiments = {
        'positive': { 
            emoji: '😊', 
            text: 'Positive Vibes', 
            color: '#4ade80',
            score: 0.8
        },
        'negative': { 
            emoji: '😞', 
            text: 'Needs Support', 
            color: '#f87171',
            score: 0.3
        },
        'neutral': { 
            emoji: '😐', 
            text: 'Neutral Mood', 
            color: '#fbbf24',
            score: 0.5
        }
    };
    
    const data = sentiments[sentiment] || sentiments['neutral'];
    sentimentEmoji.textContent = data.emoji;
    sentimentText.textContent = data.text;
    sentimentFill.style.width = (data.score * 100) + '%';
    sentimentFill.style.background = `linear-gradient(90deg, ${data.color}, ${data.color}dd)`;
    sentimentScore.textContent = data.score.toFixed(1);
}

// Text-to-speech
function speakText(text) {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    
    const cleanText = text.replace(/[\u{1F300}-\u{1F9FF}]/gu, '').substring(0, 200);
    
    fetch('/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: cleanText })
    })
    .then(response => response.blob())
    .then(blob => {
        const audioUrl = URL.createObjectURL(blob);
        currentAudio = new Audio(audioUrl);
        currentAudio.play();
    })
    .catch(error => console.log('TTS Error:', error));
}

// Voice recognition
function startVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        showToast('Voice recognition not supported. Use Chrome browser.', 'error');
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    voiceBtn.classList.add('recording');
    showToast('Listening... Speak now! 🎤', 'info');

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        voiceBtn.classList.remove('recording');
        showToast('Voice captured! ✅', 'success');
        sendMessage();
    };

    recognition.onerror = function(event) {
        voiceBtn.classList.remove('recording');
        showToast('Voice error: ' + event.error, 'error');
    };

    recognition.onend = function() {
        voiceBtn.classList.remove('recording');
    };

    recognition.start();
}

// Toggle TTS
function toggleTTS() {
    ttsEnabled = !ttsEnabled;
    ttsBtn.classList.toggle('active', ttsEnabled);
    showToast(ttsEnabled ? 'Voice output enabled 🔊' : 'Voice output disabled 🔇', 'info');
}

// View history
function viewHistory() {
    fetch('/history?limit=10')
    .then(response => response.json())
    .then(data => {
        if (data.history && data.history.length > 0) {
            showToast('Loading conversation history...', 'info');
            chatBox.innerHTML = '';
            data.history.reverse().forEach((item) => {
                addMessage(item.user_message, 'user');
                addMessage(item.bot_response, 'bot');
            });
        } else {
            showToast('No conversation history found.', 'warning');
        }
    })
    .catch(() => showToast('Error loading history.', 'error'));
}

// View sentiment stats
function viewSentimentStats() {
    fetch('/sentiment-stats')
    .then(response => response.json())
    .then(data => {
        if (data.stats && data.stats.length > 0) {
            let statsMsg = '📊 Sentiment Statistics:\n\n';
            data.stats.forEach(stat => {
                const emoji = stat.sentiment === 'positive' ? '😊' : 
                             stat.sentiment === 'negative' ? '😞' : '😐';
                statsMsg += `${emoji} ${stat.sentiment.toUpperCase()}: ${stat.count} messages (Score: ${stat.avg_score.toFixed(2)})\n`;
            });
            addMessage(statsMsg, 'bot');
            showToast('Sentiment stats loaded! 📊', 'success');
        } else {
            showToast('No sentiment data yet. Keep chatting!', 'info');
        }
    })
    .catch(() => showToast('Error loading stats.', 'error'));
}

// Clear chat
function clearChat() {
    chatBox.innerHTML = '';
    messageCount = 0;
    showToast('Chat cleared! Starting fresh. 🗑️', 'success');
    addMessage('Chat cleared! I\'m ready to help you. Try asking about weather, news, or math! 🚀', 'bot');
}

// Theme toggle (placeholder for future dark mode)
function toggleTheme() {
    showToast('Theme customization coming soon! 🎨', 'info');
}

// Quick action chips
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('chip')) {
        const action = e.target.getAttribute('data-action');
        userInput.value = action;
        sendMessage();
    }
});

// Feature card interactions
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('click', function() {
        const feature = this.getAttribute('data-feature');
        const messages = {
            'nlp': 'Tell me about advanced NLP capabilities',
            'sentiment': 'Analyze my mood: I\'m feeling great!',
            'weather': 'What\'s the weather in London?',
            'news': 'Show me technology news',
            'voice': 'This feature allows voice input and output!',
            'math': 'Calculate 15 * 23 + 100'
        };
        userInput.value = messages[feature];
        sendMessage();
    });
});

// Event listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
voiceBtn.addEventListener('click', startVoiceRecognition);
ttsBtn.addEventListener('click', toggleTTS);
historyBtn.addEventListener('click', viewHistory);
statsBtn.addEventListener('click', viewSentimentStats);
clearBtn.addEventListener('click', clearChat);
themeBtn.addEventListener('click', toggleTheme);

// Input suggestions (simple autocomplete)
const suggestions = [
    'weather in ',
    'technology news',
    'calculate ',
    'I\'m feeling ',
    'search for ',
    'sports headlines',
    'business news'
];

userInput.addEventListener('input', function() {
    const value = this.value.toLowerCase();
    // Could implement autocomplete here
});

// Initialize
window.addEventListener('load', () => {
    console.log('🚀 Advanced AI Chatbot loaded!');
    console.log('✨ Features: NLP, Sentiment, Weather, News, Voice I/O');
    
    createParticles();
    showToast('Welcome! I\'m ready to assist you. 👋', 'success');
    
    // Animate feature cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeIn 0.6s ease-out';
            }
        });
    });
    
    document.querySelectorAll('.feature-card').forEach(card => {
        observer.observe(card);
    });
});