from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, name, timeout=15):
        self.name = name
        self.timeout = timeout
        self.jobs = []

    @abstractmethod
    def scrape(self, query, location):
        """Abstrakte Methode zum Scrapen"""
        pass

    def fetch_page(self, url, params=None, headers=None):
        """Ruft eine Webseite ab"""
        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            logger.error(f"{self.name}: Timeout beim Abrufen der Seite")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"{self.name}: Verbindungsfehler")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.name}: Fehler beim Abrufen: {e}")
            return None

    def parse_jobs(self, html, selector_config):
        """Parst HTML und extrahiert Jobs"""
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        # Wird in Subklassen implementiert
        return jobs

    def format_job(self, title, company, location, link, description=""):
        """Formatiert einen Job für die Datenbank"""
        return {
            "Datum": datetime.now().strftime("%Y-%m-%d"),
            "Plattform": self.name,
            "Titel": title,
            "Unternehmen": company,
            "Standort": location,
            "Link": link,
            "Beschreibung": description
        }
