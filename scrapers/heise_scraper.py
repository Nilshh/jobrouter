import logging
from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from config import DEFAULT_HEADERS
from utils.search_helper import SearchHelper

logger = logging.getLogger(__name__)

class HeiseScraper(BaseScraper):
    """Scraper für jobs.heise.de"""
    
    def scrape(self, query, location, radius=50):
        """Scrape Heise Jobs"""
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
            city_string = ", ".join(cities[:5])  # Max 5 Städte
            
            # Heise Jobs URL
            url = "https://jobs.heise.de/it/jobs"
            params = {
                "search": query_str,
                "location": city_string
            }
            
            html = self.fetch_page(url, params=params, headers=DEFAULT_HEADERS)
            if not html:
                logger.warning(f"{self.name}: Keine HTML-Antwort")
                return []
            
            jobs = self._parse_jobs(html, location)
            logger.info(f"{self.name}: {len(jobs)} Jobs gefunden")
            return jobs
            
        except Exception as e:
            logger.error(f"{self.name}: Fehler - {e}", exc_info=True)
            return []

    def _parse_jobs(self, html, location):
        """Parse Heise HTML"""
        jobs = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            job_listings = soup.find_all("a", class_="job-item")
            
            if not job_listings:
                job_listings = soup.find_all("div", class_="job")
            
            logger.debug(f"{self.name}: Gefundene Job-Container: {len(job_listings)}")
            
            for item in job_listings:
                try:
                    title_elem = item.find("h2") or item.find("h3")
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    company_elem = item.find("span", class_="company")
                    company = company_elem.get_text(strip=True) if company_elem else ""
                    
                    link_elem = item.find("a", href=True)
                    link = link_elem["href"] if link_elem else ""
                    if link and not link.startswith("http"):
                        link = "https://jobs.heise.de" + link
                    
                    location_elem = item.find("span", class_="location")
                    job_location = location_elem.get_text(strip=True) if location_elem else location
                    
                    if title and company and link:
                        job = self.format_job(title, company, job_location, link)
                        jobs.append(job)
                        logger.debug(f"{self.name}: Job hinzugefügt - {title}")
                
                except Exception as e:
                    logger.debug(f"{self.name}: Fehler beim Parsen: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"{self.name}: Parse-Fehler - {e}", exc_info=True)
        
        return jobs
