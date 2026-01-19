from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time

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
            time.sleep(1)
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            logger.debug(f"{self.name}: Seite erfolgreich geladen ({len(response.text)} bytes)")
            return response.text
        except Exception as e:
            logger.error(f"{self.name}: Fehler beim Abrufen: {e}")
            return None

    def format_job(self, title, company, location="Deutschland", link="", description=""):
        """Formatiert einen Job für die Datenbank"""
        return {
            "Datum": datetime.now().strftime("%Y-%m-%d"),
            "Plattform": self.name,
            "Titel": title.strip() if title else "",
            "Unternehmen": company.strip() if company else "",
            "Standort": location.strip() if location else "Deutschland",
            "Link": link.strip() if link else "",
            "Beschreibung": description.strip() if description else ""
        }
