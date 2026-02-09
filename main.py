"""
Main script for Trending Topics Analyzer
Orchestrates data collection, analysis, and reporting
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import collectors
from data_collectors.news_collector import NewsAPICollector
from data_collectors.rss_collector import RSSCollector
from config import Config


def test_data_collection():
    """Test both data collectors"""
    print("\n" + "="*70)
    print("TESTING DATA COLLECTION PIPELINE")
    print("="*70 + "\n")
    
    # Display configuration
    Config.display()
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # ===== TEST NEWSAPI =====
    print("\n>>> STEP 1: Testing NewsAPI Collector...")
    print("-" * 70)
    
    news_data = None
    if Config.NEWS_API_KEY:
        try:
            news_collector = NewsAPICollector(Config.NEWS_API_KEY)
            news_data = news_collector.collect_comprehensive_trends(
                country=Config.NEWS_COUNTRY,
                categories=Config.NEWS_CATEGORIES,
                top_n=Config.NEWS_TOP_N
            )
            
            if news_data:
                news_file = news_collector.save_to_file(news_data)
                print(f"✓ NewsAPI data collected successfully!")
                print(f"  File: {news_file}")
                print(f"  Trends found: {len(news_data.get('trends', []))}")
            else:
                print("✗ Failed to collect NewsAPI data")
                news_data = None
                
        except Exception as e:
            print(f"✗ Error with NewsAPI: {e}")
            news_data = None
    else:
        print("⚠ NewsAPI key not configured - skipping NewsAPI")
        print("  Add NEWS_API_KEY to .env file to enable NewsAPI")
    
    # ===== TEST RSS FEEDS =====
    print("\n>>> STEP 2: Testing RSS Feeds Collector...")
    print("-" * 70)
    
    try:
        rss_collector = RSSCollector()
        rss_data = rss_collector.collect_comprehensive_trends(
            max_items_per_feed=Config.RSS_MAX_ITEMS_PER_FEED,
            top_n=Config.RSS_TOP_N
        )
        
        if rss_data:
            rss_file = rss_collector.save_to_file(rss_data)
            print(f"✓ RSS feeds data collected successfully!")
            print(f"  File: {rss_file}")
            print(f"  Trends found: {len(rss_data.get('trends', []))}")
        else:
            print("✗ Failed to collect RSS data")
            rss_data = None
            
    except Exception as e:
        print(f"✗ Error with RSS feeds: {e}")
        import traceback
        traceback.print_exc()
        rss_data = None
    
    # ===== COMBINE DATA =====
    print("\n>>> STEP 3: Combining Data Sources...")
    print("-" * 70)
    
    combined_data = {
        'collection_timestamp': datetime.now().isoformat(),
        'sources': []
    }
    
    if news_data:
        combined_data['sources'].append('NewsAPI')
        combined_data['newsapi'] = news_data
    
    if rss_data:
        combined_data['sources'].append('RSS Feeds')
        combined_data['rss_feeds'] = rss_data
    
    # Save combined data
    if combined_data['sources']:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        combined_file = os.path.join('data', f'combined_trends_{timestamp}.json')
        
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Combined data saved to: {combined_file}")
        print(f"  Data sources: {', '.join(combined_data['sources'])}")
    else:
        print("✗ No data collected from any source")
        combined_file = None
    
    # ===== SUMMARY =====
    print("\n" + "="*70)
    print("COLLECTION SUMMARY")
    print("="*70)
    
    if news_data:
        print(f"✓ NewsAPI: {len(news_data.get('trends', []))} trends")
        print("  Top 3:")
        for trend in news_data.get('trends', [])[:3]:
            print(f"    {trend['rank']}. {trend['title'][:60]}...")
            print(f"       Source: {trend['source']} | Category: {trend['category']}")
    else:
        print("✗ NewsAPI: Not configured or failed")
    
    print()
    
    if rss_data:
        print(f"✓ RSS Feeds: {len(rss_data.get('trends', []))} trending topics")
        print("  Top 3:")
        for trend in rss_data.get('trends', [])[:3]:
            print(f"    {trend['rank']}. {trend['title'][:60]}...")
            print(f"       Source: {trend['source']} | Category: {trend['category']}")
    else:
        print("✗ RSS Feeds: Failed")
    
    print("\n" + "="*70)
    
    if combined_file:
        print(f"\n✓ SUCCESS! Data collection complete.")
        print(f"✓ Combined data file: {combined_file}")
        print(f"✓ Total sources: {len(combined_data['sources'])}")
        print("\nNext steps:")
        print("  1. Review the collected data in the data/ folder")
        print("  2. Get Anthropic API key for AI analysis (Day 2)")
        print("  3. Implement AI analysis pipeline")
        print("  4. Generate PDF report (Day 3)")
    else:
        print("\n✗ FAILED - No data collected")
        print("Please check error messages above")
        print("\nTroubleshooting:")
        print("  - Add NEWS_API_KEY to .env file")
        print("  - Check internet connection")
        print("  - Verify RSS feeds are accessible")
    
    print("\n" + "="*70 + "\n")
    
    return combined_data if combined_file else None


def main():
    """Main entry point"""
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          TRENDING TOPICS ANALYZER - DATA COLLECTION TEST           ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    # Run test
    result = test_data_collection()
    
    if result:
        print("✓ Test completed successfully!")
        return 0
    else:
        print("✗ Test failed - but RSS feeds should still work!")
        print("  Make sure you have NEWS_API_KEY in your .env file")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)