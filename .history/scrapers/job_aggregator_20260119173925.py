import logging
from datetime import datetime
import pandas as pd
from config import EXCEL_FILE, EXCEL_COLUMNS, SCRAPERS, DEFAULT_HEADERS
from scrapers.demo_scraper import DemoScraper
from scrapers.stepstone_scraper import StepstoneScraper
from scrapers.xing_scraper import XingScraper
from scrapers.jobware_scraper import JobwareScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobAggregator:
    def __init__(self):
        self.scrapers = {
            "demo": DemoScraper("Demo", timeout=5),  # Zuerst Demo-Scraper
            "stepstone": StepstoneScraper("Stepstone", timeout=SCRAPERS["stepstone"]["timeout"]),
            "xing": XingScraper("Xing", timeout=SCRAPERS["xing"]["timeout"]),
            "jobware": JobwareScraper("Jobware", timeout=SCRAPERS["jobware"]["timeout"]),
        }
        self.all_jobs = []

    def scrape_all(self, query, location):
        """Scrape alle aktivierten Jobbörsen"""
        logger.info(f"Starte Scraping für '{query}' in '{location}'...")
        self.all_jobs = []
        
        for scraper_name, scraper in self.scrapers.items():
            # Demo-Scraper läuft immer
            if scraper_name == "demo":
                try:
                    logger.info(f"Scrape {scraper_name}...")
                    jobs = scraper.scrape(query, location)
                    self.all_jobs.extend(jobs)
                    logger.info(f"{scraper_name}: {len(jobs)} Jobs gefunden")
                except Exception as e:
                    logger.error(f"Fehler bei {scraper_name}: {e}")
                    continue
            else:
                # Andere Scraper nur wenn aktiviert
                if not SCRAPERS.get(scraper_name, {}).get("enabled", True):
                    logger.info(f"{scraper_name} ist deaktiviert, überspringe...")
                    continue
                
                try:
                    logger.info(f"Scrape {scraper_name}...")
                    jobs = scraper.scrape(query, location)
                    self.all_jobs.extend(jobs)
                    logger.info(f"{scraper_name}: {len(jobs)} Jobs gefunden")
                except Exception as e:
                    logger.error(f"Fehler bei {scraper_name}: {e}")
                    continue

        logger.info(f"Insgesamt {len(self.all_jobs)} Jobs gefunden")
        return self.all_jobs

    def save_to_excel(self):
        """Speichert Jobs in Excel"""
        try:
            if not self.all_jobs:
                logger.warning("Keine Jobs zum Speichern vorhanden")
                return

            df = pd.DataFrame(self.all_jobs, columns=EXCEL_COLUMNS)
            
            # Lade existierende Daten und merge
            try:
                existing_df = pd.read_excel(EXCEL_FILE)
                df = pd.concat([existing_df, df], ignore_index=True)
                # Entferne Duplikate
                df = df.drop_duplicates(subset=['Titel', 'Link'], keep='first')
            except FileNotFoundError:
                pass

            df.to_excel(EXCEL_FILE, index=False)
            logger.info(f"Daten gespeichert in {EXCEL_FILE} ({len(df)} Einträge)")
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")

    def get_latest_jobs(self, limit=50):
        """Gibt die neuesten Jobs zurück"""
        try:
            df = pd.read_excel(EXCEL_FILE)
            jobs = df.tail(limit).to_dict('records')
            logger.info(f"Abrufen: {len(jobs)} Jobs")
            return jobs
        except FileNotFoundError:
            logger.warning("Excel-Datei nicht gefunden")
            return []
        except Exception as e:
            logger.error(f"Fehler beim Abrufen: {e}")
            return []
