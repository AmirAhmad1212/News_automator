"""
RSS Feed Collector
Fetches trending news from RSS feeds (no API key needed!)
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
from urllib.parse import urlparse


class RSSCollector:
    """Collects trending news from RSS feeds"""
    
    def __init__(self):
        """Initialize RSS collector"""
        # Popular RSS feeds - no authentication needed!
        self.feeds = {
            'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
            'CNN': 'http://rss.cnn.com/rss/cnn_topstories.rss',
            'TechCrunch': 'https://techcrunch.com/feed/',
            'The Verge': 'https://www.theverge.com/rss/index.xml',
            'Reuters': 'https://www.reutersagency.com/feed/',
            'Hacker News': 'https://news.ycombinator.com/rss',
        }
        print("✓ RSS collector initialized")
    
    def fetch_feed(self, feed_name, feed_url, max_items=20):
        """
        Fetch and parse an RSS feed
        
        Args:
            feed_name (str): Name of the feed source
            feed_url (str): URL of the RSS feed
            max_items (int): Maximum items to fetch
        
        Returns:
            list: List of feed items
        """
        try:
            print(f"Fetching {feed_name}...")
            
            # Fetch RSS feed
            response = requests.get(feed_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            items = []
            
            # Handle different RSS formats
            # Try RSS 2.0 format first
            for item in root.findall('.//item')[:max_items]:
                article = self._parse_rss_item(item, feed_name)
                if article:
                    items.append(article)
            
            # If no items, try Atom format
            if not items:
                for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry')[:max_items]:
                    article = self._parse_atom_entry(entry, feed_name)
                    if article:
                        items.append(article)
            
            print(f"✓ Fetched {len(items)} items from {feed_name}")
            return items
            
        except Exception as e:
            print(f"✗ Error fetching {feed_name}: {e}")
            return []
    
    def _parse_rss_item(self, item, source):
        """Parse RSS 2.0 item"""
        try:
            title = item.find('title')
            link = item.find('link')
            description = item.find('description')
            pub_date = item.find('pubDate')
            
            return {
                'title': title.text if title is not None else '',
                'description': description.text if description is not None else '',
                'url': link.text if link is not None else '',
                'published_at': pub_date.text if pub_date is not None else '',
                'source': source
            }
        except:
            return None
    
    def _parse_atom_entry(self, entry, source):
        """Parse Atom feed entry"""
        try:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            title = entry.find('atom:title', ns)
            link = entry.find('atom:link', ns)
            summary = entry.find('atom:summary', ns)
            published = entry.find('atom:published', ns)
            
            return {
                'title': title.text if title is not None else '',
                'description': summary.text if summary is not None else '',
                'url': link.get('href') if link is not None else '',
                'published_at': published.text if published is not None else '',
                'source': source
            }
        except:
            return None
    
    def fetch_all_feeds(self, max_items_per_feed=15):
        """
        Fetch from all RSS feeds
        
        Args:
            max_items_per_feed (int): Max items per feed
        
        Returns:
            list: Combined list of all articles
        """
        all_articles = []
        
        for feed_name, feed_url in self.feeds.items():
            articles = self.fetch_feed(feed_name, feed_url, max_items_per_feed)
            all_articles.extend(articles)
        
        return all_articles
    
    def analyze_trending_topics(self, articles):
        """
        Analyze articles to extract trending topics
        
        Args:
            articles (list): List of articles
        
        Returns:
            list: Trending topics with metadata
        """
        if not articles:
            return []
        
        topics = []
        
        for i, article in enumerate(articles, 1):
            if not article.get('title'):
                continue
            
            topic = {
                'rank': i,
                'title': article.get('title', 'No title'),
                'description': article.get('description', '')[:200],
                'source': article.get('source', 'Unknown'),
                'published_at': article.get('published_at', ''),
                'url': article.get('url', ''),
                'category': self._categorize_article(article),
                'recency_score': self._calculate_recency(article.get('published_at', ''))
            }
            topics.append(topic)
        
        # Sort by recency (newer = better)
        topics.sort(key=lambda x: x['recency_score'], reverse=True)
        
        # Re-rank
        for i, topic in enumerate(topics, 1):
            topic['rank'] = i
        
        return topics
    
    def _categorize_article(self, article):
        """Categorize article based on content"""
        title_desc = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        source = article.get('source', '').lower()
        
        # Category keywords
        if 'techcrunch' in source or 'verge' in source or 'hacker' in source:
            return 'Technology'
        elif any(word in title_desc for word in ['tech', 'ai', 'software', 'app', 'cyber', 'digital']):
            return 'Technology'
        elif any(word in title_desc for word in ['business', 'market', 'stock', 'economy', 'finance']):
            return 'Business'
        elif any(word in title_desc for word in ['politics', 'government', 'election', 'president']):
            return 'Politics'
        elif any(word in title_desc for word in ['sports', 'game', 'player', 'team']):
            return 'Sports'
        elif any(word in title_desc for word in ['health', 'medical', 'vaccine', 'disease']):
            return 'Health'
        elif any(word in title_desc for word in ['science', 'research', 'study', 'space']):
            return 'Science'
        else:
            return 'General'
    
    def _calculate_recency(self, pub_date_str):
        """Calculate recency score (newer = higher)"""
        if not pub_date_str:
            return 0
        
        try:
            # Try parsing different date formats
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ']:
                try:
                    pub_date = datetime.strptime(pub_date_str, fmt)
                    hours_old = (datetime.now(pub_date.tzinfo) - pub_date).total_seconds() / 3600
                    
                    # Newer articles get higher scores
                    if hours_old < 1:
                        return 100
                    elif hours_old < 6:
                        return 90
                    elif hours_old < 24:
                        return 70
                    elif hours_old < 48:
                        return 50
                    else:
                        return 30
                except:
                    continue
        except:
            pass
        
        return 25  # Default score
    
    def collect_comprehensive_trends(self, max_items_per_feed=15, top_n=20):
        """
        Collect comprehensive trending news from RSS feeds
        
        Args:
            max_items_per_feed (int): Max items per feed
            top_n (int): Number of top trends to return
        
        Returns:
            dict: Comprehensive trending data
        """
        print("\n" + "="*50)
        print("COLLECTING RSS FEEDS DATA")
        print("="*50 + "\n")
        
        # Fetch all feeds
        all_articles = self.fetch_all_feeds(max_items_per_feed)
        
        print(f"\nTotal articles collected: {len(all_articles)}")
        
        # Analyze trending topics
        trending_topics = self.analyze_trending_topics(all_articles)
        
        # Take top N
        top_trends = trending_topics[:top_n]
        
        # Compile result
        result = {
            'source': 'RSS Feeds',
            'collection_time': datetime.now().isoformat(),
            'feeds_monitored': list(self.feeds.keys()),
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
            filename = f'rss_feeds_{timestamp}.json'
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        filepath = os.path.join('data', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Data saved to: {filepath}")
        return filepath


# Test function
def test_collector():
    """Test the RSS collector"""
    print("Testing RSS Collector...\n")
    
    try:
        # Initialize collector
        collector = RSSCollector()
        
        # Collect data
        data = collector.collect_comprehensive_trends(
            max_items_per_feed=10,
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