import logging
import feedparser
from scrapers.base_scraper import BaseScraper
from datetime import datetime
from utils.search_helper import SearchHelper

logger = logging.getLogger(__name__)

class IndeedScraper(BaseScraper):
    """Scraper für Indeed.de RSS-Feeds"""
    
    def scrape(self, query, location, radius=50):
        """Scrape Indeed über RSS-Feed"""
        logger.info(f"{self.name}: Starte Scraping mit Radius {radius}km...")
        
        try:
            # Formatiere Query
            if isinstance(query, list):
                query_str = " OR ".join(query)
            else:
                query_str = query
            
            # Hole Städte im Radius
            search_helper = SearchHelper()
            cities = search_helper.get_cities_in_radius(location, radius)
            
            all_jobs = []
            
            # Suche in jeder Stadt
            for city in cities:
                try:
                    logger.debug(f"{self.name}: Suche in {city}...")
                    
                    # Indeed RSS-Feed URL
                    feed_url = f"https://de.indeed.com/rss?q={query_str}&l={city}&sort=date"
                    logger.debug(f"{self.name}: Feed-URL: {feed_url}")
                    
                    feed = feedparser.parse(feed_url)
                    
                    if feed.bozo:
                        logger.warning(f"{self.name}: Feed-Parsing-Fehler für {city}")
                        continue
                    
                    logger.debug(f"{self.name}: {len(feed.entries)} Einträge in {city} gefunden")
                    
                    for entry in feed.entries[:10]:  # Max 10 pro Stadt
                        try:
                            title = entry.get('title', '')
                            summary = entry.get('summary', '')
                            link = entry.get('link', '')
                            
                            # Extrahiere Unternehmen
                            company = self._extract_company(summary)
                            
                            if title and link:
                                job = self.format_job(
                                    title=title,
                                    company=company or 'Indeed',
                                    location=city,
                                    link=link,
                                    description=summary[:200] if summary else ""
                                )
                                all_jobs.append(job)
                                logger.debug(f"{self.name}: Job hinzugefügt - {title} in {city}")
                        
                        except Exception as e:
                            logger.debug(f"{self.name}: Fehler beim Parsen eines Eintrags: {e}")
                            continue
                
                except Exception as e:
                    logger.warning(f"{self.name}: Fehler bei Stadt {city}: {e}")
                    continue
            
            logger.info(f"{self.name}: {len(all_jobs)} Jobs gefunden")
            return all_jobs
            
        except Exception as e:
            logger.error(f"{self.name}: Fehler - {e}", exc_info=True)
            return []

    def _extract_company(self, summary):
        """Extrahiert Unternehmen aus Summary"""
        try:
            import re
            clean_summary = re.sub('<[^<]+?>', '', summary)
            lines = clean_summary.split('\n')
            if lines:
                return lines[0].strip()
        except:
            pass
        return ""
