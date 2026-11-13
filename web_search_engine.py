import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
import re
from datetime import datetime
import time

class WebSearchEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Brave/1.85.118',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        print("✅ Web Search Engine initialized with Google Search!")
    
    def search_web(self, query, num_results=5):
        """Search Google and return results with AI summary"""
        try:
            # Search Google
            results = self._google_search(query, num_results)
            
            if not results:
                return {
                    'success': False,
                    'error': 'No results found',
                    'query': query,
                    'results': []
                }
            
            # Generate AI summary of search results
            summary = self._generate_search_summary(query, results)
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results),
                'summary': summary,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Search error: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'results': []
            }
    
    def _google_search(self, query, num_results=5):
        """Perform Google search"""
        try:
            # Construct Google search URL
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
            
            # Add delay to be respectful
            time.sleep(0.5)
            
            # Make request
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Google search returned status code: {response.status_code}")
                return []
            
            # Parse results
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Find search result divs (Google's structure)
            search_divs = soup.find_all('div', class_='g')
            
            for div in search_divs[:num_results]:
                try:
                    # Extract title
                    title_elem = div.find('h3')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract URL
                    link_elem = div.find('a')
                    if not link_elem or not link_elem.get('href'):
                        continue
                    url = link_elem['href']
                    
                    # Clean URL (remove Google redirect)
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    # Extract snippet/description
                    snippet_elem = div.find('div', class_=['VwiC3b', 'yXK7lf', 'lVm3ye'])
                    if not snippet_elem:
                        snippet_elem = div.find('span', class_=['aCOpRe', 'st'])
                    
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No description available"
                    
                    # Extract domain
                    domain = urlparse(url).netloc
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'domain': domain,
                        'source': 'Google'
                    })
                    
                except Exception as e:
                    print(f"Error parsing result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"Google search error: {e}")
            return []
    
    def _generate_search_summary(self, query, results):
        """Generate Gemini-style AI summary of search results"""
        if not results:
            return f"No results found for '{query}'."
        
        # Extract key information from results
        titles = [r['title'] for r in results[:3]]
        snippets = [r['snippet'][:150] for r in results[:3]]
        domains = [r['domain'] for r in results[:3]]
        
        # Create intelligent summary
        summary = f"🔍 **Search Summary for '{query}':**\n\n"
        
        # Identify common themes
        all_text = ' '.join(titles + snippets).lower()
        
        # Generate contextual summary
        if len(results) >= 3:
            summary += f"I found {len(results)} relevant results. Here's what I discovered:\n\n"
            
            # Main finding from top result
            summary += f"**Key Finding:** {snippets[0][:200]}\n\n"
            
            # Additional insights
            summary += f"**Top Sources:**\n"
            for i, (title, domain) in enumerate(zip(titles[:3], domains[:3]), 1):
                summary += f"{i}. {title} ({domain})\n"
            
            summary += f"\n💡 **Quick Answer:** Based on the search results, "
            
            # Generate contextual answer based on query type
            if any(word in query.lower() for word in ['what', 'define', 'meaning']):
                summary += f"here's a definition: {snippets[0][:150]}..."
            elif any(word in query.lower() for word in ['how', 'tutorial', 'guide']):
                summary += f"the top resources explain: {snippets[0][:150]}..."
            elif any(word in query.lower() for word in ['best', 'top', 'recommend']):
                summary += f"the top recommendations include: {titles[0]}"
            elif any(word in query.lower() for word in ['news', 'latest', 'recent']):
                summary += f"recent updates show: {snippets[0][:150]}..."
            else:
                summary += f"{snippets[0][:150]}..."
        else:
            summary += f"Found {len(results)} result(s). {snippets[0][:200]}" if snippets else "Limited results available."
        
        return summary
    
    def fetch_page_content(self, url):
        """Fetch and extract text content from a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Get title
            title = soup.title.string if soup.title else 'No title'
            
            return {
                'success': True,
                'url': url,
                'content': text[:10000],  # Limit to first 10000 chars
                'title': title,
                'length': len(text)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def format_search_results(self, search_data):
        """Format search results with AI summary for display"""
        if not search_data['success']:
            return f"❌ Search failed: {search_data.get('error', 'Unknown error')}\n\nTip: Try rephrasing your query or check your internet connection."
        
        if not search_data['results']:
            return f"🔍 No results found for '{search_data['query']}'\n\nTry:\n• Using different keywords\n• Being more specific\n• Checking spelling"
        
        # Start with AI-generated summary
        output = search_data['summary'] + "\n\n"
        
        # Add detailed results
        output += "📋 **Detailed Results:**\n\n"
        
        for i, result in enumerate(search_data['results'], 1):
            output += f"**{i}. {result['title']}**\n"
            output += f"   🌐 {result['domain']}\n"
            output += f"   🔗 {result['url']}\n"
            if result['snippet']:
                snippet = result['snippet'][:200]
                output += f"   📝 {snippet}...\n"
            output += "\n"
        
        # Add helpful footer
        output += "💬 Need more details? Ask me to summarize any of these links!\n"
        output += f"Example: 'summarize {search_data['results'][0]['url']}'"
        
        return output