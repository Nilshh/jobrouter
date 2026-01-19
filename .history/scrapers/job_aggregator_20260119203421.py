import logging
from datetime import datetime
import pandas as pd
from config import EXCEL_FILE, EXCEL_COLUMNS, SCRAPERS, DEFAULT_HEADERS
from scrapers.demo_scraper import DemoScraper
from scrapers.selenium_indeed import IndeedSeleniumScraper
from scrapers.selenium_linkedin import LinkedInSeleniumScraper
from scrapers.indeed_scraper import IndeedScraper
from scrapers.heise_scraper import HeiseScraper
from scrapers.stepstone_scraper import StepstoneScraper
from scrapers.xing_scraper import XingScraper
from scrapers.jobware_scraper import JobwareScraper
from utils.search_helper import SearchHelper
from utils.salary_extractor import SalaryExtractor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobAggregator:
    def __init__(self):
        self.scrapers = {
            "demo": DemoScraper("Demo", timeout=5),
            "indeed_selenium": IndeedSeleniumScraper("Indeed (Selenium)", timeout=30),
            "linkedin_selenium": LinkedInSeleniumScraper("LinkedIn (Selenium)", timeout=30),
            "indeed": IndeedScraper("Indeed", timeout=SCRAPERS.get("indeed", {}).get("timeout", 15)),
            "heise": HeiseScraper("Heise", timeout=SCRAPERS.get("heise", {}).get("timeout", 15)),
            "stepstone": StepstoneScraper("Stepstone", timeout=SCRAPERS.get("stepstone", {}).get("timeout", 15)),
            "xing": XingScraper("Xing", timeout=SCRAPERS.get("xing", {}).get("timeout", 15)),
            "jobware": JobwareScraper("Jobware", timeout=SCRAPERS.get("jobware", {}).get("timeout", 15)),
        }
        self.all_jobs = []

    def scrape_all(self, query, location, radius=50):
        """Scrape alle aktivierten Jobbörsen"""
        logger.info(f"Starte Scraping für '{query}' in '{location}' (Radius: {radius}km)...")
        self.all_jobs = []
        
        priority_order = ["demo", "indeed_selenium", "linkedin_selenium", "indeed", "heise", "stepstone", "xing", "jobware"]
        
        for scraper_name in priority_order:
            if scraper_name not in self.scrapers:
                continue
            
            scraper = self.scrapers[scraper_name]
            
            if scraper_name == "demo":
                try:
                    logger.info(f"Scrape {scraper_name}...")
                    jobs = scraper.scrape(query, location)
                    jobs = self._enrich_jobs(jobs)
                    self.all_jobs.extend(jobs)
                    logger.info(f"{scraper_name}: {len(jobs)} Jobs gefunden")
                except Exception as e:
                    logger.error(f"Fehler bei {scraper_name}: {e}")
                continue
            
            if not SCRAPERS.get(scraper_name.replace('_selenium', ''), {}).get("enabled", True):
                logger.info(f"{scraper_name} ist deaktiviert, überspringe...")
                continue
            
            try:
                logger.info(f"Scrape {scraper_name}...")
                jobs = scraper.scrape(query, location, radius)
                jobs = self._enrich_jobs(jobs)
                self.all_jobs.extend(jobs)
                logger.info(f"{scraper_name}: {len(jobs)} Jobs gefunden")
            except Exception as e:
                logger.error(f"Fehler bei {scraper_name}: {e}")
                continue

        logger.info(f"Insgesamt {len(self.all_jobs)} Jobs gefunden")
        return self.all_jobs

    def _enrich_jobs(self, jobs):
        """Reichert Jobs mit zusätzlichen Informationen an"""
        for job in jobs:
            # Extrahiere Gehalt
            salary_info = SalaryExtractor.extract(job.get('Beschreibung', ''))
            if salary_info:
                job['Salary_Min'] = salary_info['min']
                job['Salary_Max'] = salary_info['max']
            else:
                job['Salary_Min'] = None
                job['Salary_Max'] = None
        
        return jobs

    def save_to_excel(self):
        """Speichert Jobs in Excel"""
        try:
            if not self.all_jobs:
                logger.warning("Keine Jobs zum Speichern vorhanden")
                return

            df = pd.DataFrame(self.all_jobs, columns=EXCEL_COLUMNS)
            
            try:
                existing_df = pd.read_excel(EXCEL_FILE)
                df = pd.concat([existing_df, df], ignore_index=True)
                df = df.drop_duplicates(subset=['Titel', 'Link'], keep='first')
            except FileNotFoundError:
                pass

            df.to_excel(EXCEL_FILE, index=False)
            logger.info(f"Daten gespeichert in {EXCEL_FILE} ({len(df)} Einträge)")
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")

    def get_latest_jobs(self, limit=50, min_salary=None, max_salary=None):
        """Gibt die neuesten Jobs zurück, optional mit Salary-Filter"""
        try:
            df = pd.read_excel(EXCEL_FILE)
            
            # Salary-Filter anwenden
            if min_salary:
                df = df[df['Salary_Max'].fillna(0) >= min_salary]
            if max_salary:
                df = df[df['Salary_Min'].fillna(999999) <= max_salary]
            
            jobs = df.tail(limit).to_dict('records')
            logger.info(f"Abrufen: {len(jobs)} Jobs")
            return jobs
        except FileNotFoundError:
            logger.warning("Excel-Datei nicht gefunden")
            return []
        except Exception as e:
            logger.error(f"Fehler beim Abrufen: {e}")
            return []
