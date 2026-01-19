import logging
from scrapers.base_scraper import BaseScraper
from config import DEFAULT_HEADERS

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    def scrape(self, query, location):
        """Scrape LinkedIn Jobs"""
        logger.info(f"{self.name}: Starte Scraping...")
        
        try:
            url = "https://de.linkedin.com/jobs/search/"
            query_str = " OR ".join(query) if isinstance(query, list) else query
            params = {
                "keywords": query_str,
                "location": location,
                "f_TPR": "r86400"  # Letzte 24 Stunden
            }
            
            html = self.fetch_page(url, params=params, headers=DEFAULT_HEADERS)
            if not html:
                logger.warning(f"{self.name}: Keine HTML-Antwort")
                return []
            
            logger.warning(f"{self.name}: LinkedIn erfordert Selenium für vollständiges Scraping")
            return []
        except Exception as e:
            logger.error(f"{self.name}: Fehler - {e}")
            return []
