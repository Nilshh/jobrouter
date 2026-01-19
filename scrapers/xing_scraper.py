import logging
from scrapers.base_scraper import BaseScraper
from config import DEFAULT_HEADERS
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class XingScraper(BaseScraper):
    def scrape(self, query, location):
        """Scrape Xing Jobs"""
        logger.info(f"{self.name}: Starte Scraping...")
        
        try:
            url = "https://www.xing.com/jobs"
            query_str = " OR ".join(query) if isinstance(query, list) else query
            params = {
                "keywords": query_str,
                "location": location
            }
            
            html = self.fetch_page(url, params=params, headers=DEFAULT_HEADERS)
            if not html:
                logger.warning(f"{self.name}: Keine HTML-Antwort")
                return []
            
            jobs = self._parse_jobs(html)
            logger.info(f"{self.name}: {len(jobs)} Jobs gefunden")
            return jobs
        except Exception as e:
            logger.error(f"{self.name}: Fehler - {e}", exc_info=True)
            return []

    def _parse_jobs(self, html):
        """Parse Xing HTML"""
        jobs = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Versuche verschiedene Selektoren zu finden
            job_listings = soup.find_all("article", class_="job-item")
            
            if not job_listings:
                job_listings = soup.find_all("div", class_="job-card")
            
            if not job_listings:
                job_listings = soup.find_all("li", class_="job")
            
            logger.debug(f"{self.name}: Gefundene Job-Container: {len(job_listings)}")
            
            for item in job_listings:
                try:
                    # Versuche Titel zu extrahieren
                    title_elem = item.find("h2") or item.find("a")
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # Versuche Unternehmen zu extrahieren
                    company_elem = item.find("span", class_="company") or item.find("div", class_="company")
                    company = company_elem.get_text(strip=True) if company_elem else ""
                    
                    # Versuche Link zu extrahieren
                    link_elem = item.find("a", href=True)
                    link = link_elem["href"] if link_elem else ""
                    if link and not link.startswith("http"):
                        link = "https://www.xing.com" + link
                    
                    # Versuche Standort zu extrahieren
                    location_elem = item.find("span", class_="location")
                    location = location_elem.get_text(strip=True) if location_elem else "Deutschland"
                    
                    if title and company and link:
                        job = self.format_job(title, company, location, link)
                        jobs.append(job)
                        logger.debug(f"{self.name}: Job hinzugefügt - {title} bei {company}")
                
                except Exception as e:
                    logger.debug(f"{self.name}: Fehler beim Parsen eines Job-Items: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"{self.name}: Parse-Fehler - {e}", exc_info=True)
        
        return jobs
