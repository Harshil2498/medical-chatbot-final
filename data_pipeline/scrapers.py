import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScrapedArticle:
    """Represents a scraped medical article"""
    url: str
    title: str
    content: str
    category: str


class MedicalWebScraper:
    """Scrapes medical articles from various sources"""
    
    def __init__(self, user_agent: str = "MedicalChatbotMVP/1.0"):
        self.headers = {'User-Agent': user_agent}
    
    def scrape_article(self, url: str) -> Optional[ScrapedArticle]:
        """Scrape a single article"""
        try:
            print(f"🌐 Scraping: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            title = title.text.strip() if title else "Unknown Title"
            
            # Extract content paragraphs
            paragraphs = soup.find_all('p')
            content = "\n\n".join([
                p.text.strip() 
                for p in paragraphs 
                if len(p.text.strip()) > 50
            ])
            
            # Determine category
            category = self._determine_category(url)
            
            if len(content) < 100:
                print(f"   ⚠️  Content too short, skipping")
                return None
            
            print(f"   ✅ Scraped: {title} ({len(content)} chars)")
            
            return ScrapedArticle(
                url=url,
                title=title,
                content=content,
                category=category
            )
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def scrape_batch(self, urls: List[str]) -> List[ScrapedArticle]:
        """Scrape multiple URLs"""
        articles = []
        for url in urls:
            article = self.scrape_article(url)
            if article:
                articles.append(article)
        
        print(f"\n✅ Successfully scraped {len(articles)}/{len(urls)} articles\n")
        return articles
    
    def _determine_category(self, url: str) -> str:
        """Determine category from URL"""
        url_lower = url.lower()
        
        if 'diabetes' in url_lower:
            return 'diabetes'
        elif 'heart' in url_lower or 'blood-pressure' in url_lower or 'hypertension' in url_lower:
            return 'cardiology'
        elif 'mental' in url_lower or 'depression' in url_lower or 'anxiety' in url_lower:
            return 'mental_health'
        elif 'cancer' in url_lower:
            return 'oncology'
        else:
            return 'general'