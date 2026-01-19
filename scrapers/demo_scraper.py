import logging
from scrapers.base_scraper import BaseScraper
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class DemoScraper(BaseScraper):
    """Demo-Scraper mit echten Beispiel-Daten für Tests"""
    
    # Vordefinierte Demo-Daten
    DEMO_JOBS = [
        {
            "title": "Chief Information Officer (CIO)",
            "company": "Allianz Deutschland",
            "location": "München, Bayern",
            "link": "https://jobs.allianz.de/cio-position",
            "description": "Wir suchen einen erfahrenen CIO für unsere Digital-Transformation"
        },
        {
            "title": "Chief Technology Officer (CTO)",
            "company": "SAP SE",
            "location": "Walldorf, Baden-Württemberg",
            "link": "https://jobs.sap.com/cto-role",
            "description": "Leiter der technologischen Strategie"
        },
        {
            "title": "Leiter IT / IT-Director",
            "company": "Deutsche Telekom",
            "location": "Bonn, Nordrhein-Westfalen",
            "link": "https://jobs.telekom.de/it-director",
            "description": "Verantwortung für IT-Infrastruktur und Governance"
        },
        {
            "title": "Head of IT Governance",
            "company": "BMW Group",
            "location": "München, Bayern",
            "link": "https://jobs.bmw.de/it-governance",
            "description": "Aufbau und Leitung des IT-Governance-Bereichs"
        },
        {
            "title": "Director of IT Operations",
            "company": "Siemens",
            "location": "Berlin, Berlin",
            "link": "https://jobs.siemens.de/it-ops",
            "description": "Leitung der IT-Betriebsabläufe"
        },
        {
            "title": "CIO - IT-Strategieleiter",
            "company": "Deutsche Bank",
            "location": "Frankfurt, Hessen",
            "link": "https://jobs.deutschebank.de/cio",
            "description": "Strategische IT-Leitung für Finanzbereich"
        },
        {
            "title": "Leiter IT-Sicherheit & Governance",
            "company": "Commerzbank",
            "location": "Frankfurt, Hessen",
            "link": "https://jobs.commerzbank.de/it-security",
            "description": "IT-Sicherheit und Compliance-Leitung"
        },
        {
            "title": "Head of Digital Transformation",
            "company": "Daimler",
            "location": "Stuttgart, Baden-Württemberg",
            "link": "https://jobs.daimler.de/digital",
            "description": "Leitung digitale Transformation"
        },
        {
            "title": "Chief Digital Officer",
            "company": "Volkswagen Group",
            "location": "Wolfsburg, Niedersachsen",
            "link": "https://jobs.vw.de/cdo",
            "description": "Digitale Strategie und Innovation"
        },
        {
            "title": "IT Director - Cloud & Infrastructure",
            "company": "ZF Friedrichshafen",
            "location": "Friedrichshafen, Baden-Württemberg",
            "link": "https://jobs.zf.de/it-director",
            "description": "Cloud-Infrastruktur und Betrieb"
        },
        {
            "title": "Direktor IT-Management",
            "company": "Lufthansa Group",
            "location": "Frankfurt, Hessen",
            "link": "https://jobs.lufthansa.de/it-management",
            "description": "IT-Management für globale Luftfahrtgruppe"
        },
        {
            "title": "Head of Enterprise Architecture",
            "company": "Bosch",
            "location": "Stuttgart, Baden-Württemberg",
            "link": "https://jobs.bosch.de/architecture",
            "description": "Enterprise Architecture Leitung"
        }
    ]

    def scrape(self, query, location):
        """Gibt Demo-Jobs zurück"""
        logger.info(f"{self.name}: Starte Demo-Scraping...")
        
        jobs = []
        
        # Filtere Jobs nach Query
        query_terms = query.lower().split(" or ") if isinstance(query, str) else query
        
        for demo_job in self.DEMO_JOBS:
            title_lower = demo_job["title"].lower()
            
            # Prüfe ob Suchbegriff im Titel enthalten ist
            if any(term.strip().lower() in title_lower for term in query_terms):
                job = self.format_job(
                    title=demo_job["title"],
                    company=demo_job["company"],
                    location=demo_job["location"],
                    link=demo_job["link"],
                    description=demo_job["description"]
                )
                jobs.append(job)
        
        logger.info(f"{self.name}: {len(jobs)} Demo-Jobs gefunden")
        return jobs
