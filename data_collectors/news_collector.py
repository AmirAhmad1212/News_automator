"""
NewsAPI Data Collector
Fetches trending news articles from NewsAPI
"""

import requests
import json
import os
from datetime import datetime, timedelta


class NewsAPICollector:
    """Collects trending news from NewsAPI"""
    
    def __init__(self, api_key):
        """
        Initialize NewsAPI collector
        
        Args:
            api_key (str): NewsAPI key
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        
        if not api_key:
            raise ValueError("NewsAPI key is required!")
        
        print("✓ NewsAPI collector initialized")
    
    def get_top_headlines(self, country='us', category=None, page_size=50):
        """
        Get top headlines
        
        Args:
            country (str): Country code (us, gb, in, etc.)
            category (str): Category (business, technology, etc.)
            page_size (int): Number of articles (max 100)
        
        Returns:
            list: List of articles
        """
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'country': country,
                'pageSize': min(page_size, 100)
            }
            
            if category:
                params['category'] = category
            
            print(f"Fetching top headlines ({country}, {category or 'all categories'})...")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'ok':
                articles = data.get('articles', [])
                print(f"✓ Fetched {len(articles)} articles")
                return articles
            else:
                print(f"✗ API error: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"✗ Error fetching headlines: {e}")
            return []
    
    def get_trending_by_keyword(self, keyword, days=7, page_size=50):
        """
        Get articles by keyword from recent days
        
        Args:
            keyword (str): Search keyword
            days (int): Number of days to look back
            page_size (int): Number of articles
        
        Returns:
            list: List of articles
        """
        try:
            url = f"{self.base_url}/everything"
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            params = {
                'apiKey': self.api_key,
                'q': keyword,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'sortBy': 'popularity',
                'pageSize': min(page_size, 100)
            }
            
            print(f"Searching for: {keyword}...")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'ok':
                articles = data.get('articles', [])
                print(f"✓ Found {len(articles)} articles for '{keyword}'")
                return articles
            else:
                print(f"✗ API error: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"✗ Error searching for {keyword}: {e}")
            return []
    
    def analyze_trending_topics(self, articles):
        """
        Analyze articles to extract trending topics
        
        Args:
            articles (list): List of news articles
        
        Returns:
            list: Trending topics with metadata
        """
        if not articles:
            return []
        
        topics = []
        
        for i, article in enumerate(articles, 1):
            # Skip articles without titles
            if not article.get('title'):
                continue
            
            topic = {
                'rank': i,
                'title': article.get('title', 'No title'),
                'description': article.get('description', '')[:200],  # Limit length
                'source': article.get('source', {}).get('name', 'Unknown'),
                'author': article.get('author', 'Unknown'),
                'published_at': article.get('publishedAt', ''),
                'url': article.get('url', ''),
                'category': self._extract_category(article),
                'engagement_score': self._calculate_engagement(article)
            }
            topics.append(topic)
        
        # Sort by engagement score
        topics.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        # Re-rank after sorting
        for i, topic in enumerate(topics, 1):
            topic['rank'] = i
        
        return topics
    
    def _extract_category(self, article):
        """Extract category from article"""
        # Simple keyword-based categorization
        title_desc = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        categories = {
            'Technology': ['tech', 'ai', 'software', 'computer', 'digital', 'internet', 'app', 'cyber'],
            'Business': ['business', 'market', 'stock', 'economy', 'trade', 'finance', 'company'],
            'Politics': ['politics', 'government', 'election', 'congress', 'senate', 'president', 'policy'],
            'Sports': ['sports', 'game', 'player', 'team', 'championship', 'nfl', 'nba', 'soccer'],
            'Entertainment': ['movie', 'music', 'celebrity', 'actor', 'film', 'tv', 'show', 'entertainment'],
            'Health': ['health', 'medical', 'doctor', 'disease', 'hospital', 'treatment', 'vaccine'],
            'Science': ['science', 'research', 'study', 'scientist', 'discovery', 'space', 'nasa']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_desc for keyword in keywords):
                return category
        
        return 'General'
    
    def _calculate_engagement(self, article):
        """
        Calculate engagement score for an article
        
        Args:
            article (dict): Article data
        
        Returns:
            int: Engagement score (0-100)
        """
        score = 50  # Base score
        
        # Boost for reputable sources
        source = article.get('source', {}).get('name', '').lower()
        reputable = ['bbc', 'cnn', 'reuters', 'ap', 'nyt', 'washington post', 'guardian']
        if any(rep in source for rep in reputable):
            score += 20
        
        # Boost for recent articles
        published = article.get('publishedAt', '')
        if published:
            try:
                pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                hours_old = (datetime.now(pub_date.tzinfo) - pub_date).total_seconds() / 3600
                if hours_old < 24:
                    score += 20
                elif hours_old < 48:
                    score += 10
            except:
                pass
        
        # Boost for having description
        if article.get('description'):
            score += 10
        
        return min(score, 100)
    
    def collect_comprehensive_trends(self, country='us', categories=None, top_n=20):
        """
        Collect comprehensive trending news
        
        Args:
            country (str): Country code
            categories (list): List of categories to fetch
            top_n (int): Number of top trends to return
        
        Returns:
            dict: Comprehensive trending data
        """
        print("\n" + "="*50)
        print("COLLECTING NEWSAPI TRENDS DATA")
        print("="*50 + "\n")
        
        all_articles = []
        
        if categories is None:
            categories = ['general', 'technology', 'business', 'science']
        
        # Fetch from each category
        for category in categories:
            articles = self.get_top_headlines(country=country, category=category, page_size=20)
            all_articles.extend(articles)
        
        print(f"\nTotal articles collected: {len(all_articles)}")
        
        # Analyze and get trending topics
        trending_topics = self.analyze_trending_topics(all_articles)
        
        # Take top N
        top_trends = trending_topics[:top_n]
        
        # Compile result
        result = {
            'source': 'NewsAPI',
            'country': country,
            'collection_time': datetime.now().isoformat(),
            'categories_fetched': categories,
            'total_articles': len(all_articles),
            'total_trending_topics': len(trending_topics),
            'top_trends_count': len(top_trends),
            'trends': top_trends,
            'category_breakdown': self._get_category_stats(top_trends)
        }
        
        print(f"\n✓ Successfully collected {len(top_trends)} trending topics!")
        print("="*50 + "\n")
        
        return result
    
    def _get_category_stats(self, trends):
        """Get breakdown of trends by category"""
        category_counts = {}
        for trend in trends:
            cat = trend['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        return category_counts
    
    def save_to_file(self, data, filename=None):
        """
        Save collected data to JSON file
        
        Args:
            data (dict): Data to save
            filename (str): Output filename (optional)
        
        Returns:
            str: Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'newsapi_{timestamp}.json'
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        filepath = os.path.join('data', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Data saved to: {filepath}")
        return filepath


# Test function
def test_collector():
    """Test the NewsAPI collector"""
    print("Testing NewsAPI Collector...\n")
    
    # Load API key from environment
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('NEWS_API_KEY')
    
    if not api_key:
        print("✗ NEWS_API_KEY not found in .env file!")
        print("Add it to .env: NEWS_API_KEY=your_key_here")
        return
    
    try:
        # Initialize collector
        collector = NewsAPICollector(api_key)
        
        # Collect data
        data = collector.collect_comprehensive_trends(
            country='us',
            categories=['technology', 'business', 'science'],
            top_n=15
        )
        
        # Save to file
        if data:
            filepath = collector.save_to_file(data)
            print(f"\n✓ Test successful! Check {filepath}")
            
            # Print sample
            print("\nSample trending topics:")
            for trend in data['trends'][:5]:
                print(f"  {trend['rank']}. {trend['title'][:60]}...")
                print(f"     Source: {trend['source']} | Category: {trend['category']}")
        else:
            print("✗ No data collected")
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_collector()