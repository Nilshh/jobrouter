import logging
from scrapers.base_scraper import BaseScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import SELENIUM_CONFIG
import time

logger = logging.getLogger(__name__)

class LinkedInSeleniumScraper(BaseScraper):
    """Selenium-basierter LinkedIn Scraper"""
    
    def __init__(self, name="LinkedIn", timeout=30):
        super().__init__(name, timeout)
        self.driver = None
    
    def scrape(self, query, location, radius=50):
        """Scrape LinkedIn mit Selenium"""
        logger.info(f"{self.name}: Starte Selenium-Scraping...")
        
        jobs = []
        driver = None
        
        try:
            driver = self._init_driver()
            
            # Baue URL
            query_str = "%20".join(query) if isinstance(query, list) else query
            url = f"https://de.linkedin.com/jobs/search/?keywords={query_str}&location={location}&sort=date"
            
            logger.info(f"{self.name}: Öffne URL: {url}")
            driver.get(url)
            
            # Warte auf Job-Listings
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "base-card"))
                )
            except TimeoutException:
                logger.warning(f"{self.name}: Timeout beim Warten auf Job-Listings")
                return []
            
            # Scroll für mehr Jobs
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            # Parse Jobs
            jobs = self._parse_jobs(driver)
            
            logger.info(f"{self.name}: {len(jobs)} Jobs gefunden")
            return jobs
            
        except Exception as e:
            logger.error(f"{self.name}: Fehler - {e}", exc_info=True)
            return []
        finally:
            if driver:
                driver.quit()
    
    def _init_driver(self):
        """Initialisiert Selenium WebDriver"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            
            if SELENIUM_CONFIG.get("headless"):
                options.add_argument("--headless")
            
            for arg in SELENIUM_CONFIG.get("chrome_options", []):
                options.add_argument(arg)
            
            options.add_argument(f"user-agent={SELENIUM_CONFIG.get('user_agent')}")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            logger.debug(f"{self.name}: WebDriver initialisiert")
            return driver
            
        except Exception as e:
            logger.error(f"{self.name}: Fehler beim Initialisieren des WebDrivers: {e}")
            raise
    
    def _parse_jobs(self, driver):
        """Parse Jobs von der Seite"""
        jobs = []
        
        try:
            job_cards = driver.find_elements(By.CLASS_NAME, "base-card")
            logger.debug(f"{self.name}: {len(job_cards)} Job-Cards gefunden")
            
            for card in job_cards[:20]:  # Max 20 Jobs
                try:
                    title = card.find_element(By.CLASS_NAME, "base-search-card__title").text
                    company = card.find_element(By.CLASS_NAME, "base-search-card__company").text
                    link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    job = self.format_job(title, company, "Deutschland", link)
                    jobs.append(job)
                    
                except NoSuchElementException:
                    continue
            
        except Exception as e:
            logger.error(f"{self.name}: Parse-Fehler: {e}")
        
        return jobs
