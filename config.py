"""
Configuration file for Trending Topics Analyzer
Manages API keys and application settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys (loaded from .env file)
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    
    # NewsAPI Settings
    NEWS_COUNTRY = 'us'  # Country code: us, gb, in, etc.
    NEWS_CATEGORIES = ['general', 'technology', 'business', 'science']
    NEWS_TOP_N = 20  # Number of top news to analyze
    
    # RSS Feed Settings
    RSS_MAX_ITEMS_PER_FEED = 15
    RSS_TOP_N = 20
    
    # Report Settings
    REPORT_TITLE = "Trending Topics Analysis Report"
    REPORT_OUTPUT_DIR = "reports"
    
    # Data Storage
    DATA_DIR = "data"
    
    # Logging
    LOG_DIR = "logs"
    LOG_LEVEL = "INFO"
    
    @staticmethod
    def validate():
        """Validate that required configuration is present"""
        issues = []
        warnings = []
        
        # Check NewsAPI key
        if not Config.NEWS_API_KEY:
            issues.append("NEWS_API_KEY not found in .env file - NewsAPI collector will not work")
        
        # Check Anthropic API key (needed for AI analysis in Day 2)
        if not Config.ANTHROPIC_API_KEY:
            warnings.append("ANTHROPIC_API_KEY not found - needed for AI analysis (Day 2)")
        
        if warnings:
            print("\n⚠ Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if issues:
            print("\n✗ Configuration Issues:")
            for issue in issues:
                print(f"  - {issue}")
            print("\nPlease add missing values to your .env file")
            print("Note: RSS feeds will still work without NewsAPI key")
            return False
        
        print("✓ Configuration validated")
        return True
    
    @staticmethod
    def display():
        """Display current configuration (without showing API keys)"""
        print("\n" + "="*50)
        print("CURRENT CONFIGURATION")
        print("="*50)
        print(f"NewsAPI Country: {Config.NEWS_COUNTRY}")
        print(f"NewsAPI Categories: {', '.join(Config.NEWS_CATEGORIES)}")
        print(f"NewsAPI Top N: {Config.NEWS_TOP_N}")
        print(f"RSS Max Items/Feed: {Config.RSS_MAX_ITEMS_PER_FEED}")
        print(f"RSS Top N: {Config.RSS_TOP_N}")
        print(f"NewsAPI Key: {'Set ✓' if Config.NEWS_API_KEY else 'Not set ✗'}")
        print(f"Anthropic API Key: {'Set ✓' if Config.ANTHROPIC_API_KEY else 'Not set ✗ (needed for Day 2)'}")
        print("="*50 + "\n")


if __name__ == "__main__":
    # Test configuration
    Config.display()
    Config.validate()