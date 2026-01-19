import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config import SCHEDULER_CONFIG, SEARCH_QUERY, SEARCH_LOCATION, SEARCH_RADIUS
from scrapers.job_aggregator import JobAggregator
from utils.email_service import EmailService
from datetime import datetime

logger = logging.getLogger(__name__)

class JobScheduler:
    """Verwaltet automatisierte Scraping-Jobs"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(timezone=SCHEDULER_CONFIG['timezone'])
        self.aggregator = JobAggregator()
    
    def start(self):
        """Startet den Scheduler"""
        if not SCHEDULER_CONFIG.get('enabled'):
            logger.info("Scheduler ist deaktiviert")
            return
        
        try:
            logger.info("Starte Scheduler...")
            
            # Registriere Scraping-Jobs für jede Uhrzeit
            for time_str in SCHEDULER_CONFIG['scrape_times']:
                hour, minute = map(int, time_str.split(':'))
                
                self.scheduler.add_job(
                    self._scheduled_scrape,
                    CronTrigger(hour=hour, minute=minute),
                    id=f'scrape_{hour}_{minute}',
                    name=f'Scrape um {time_str} Uhr'
                )
                
                logger.info(f"✓ Job registriert: tägliches Scraping um {time_str} Uhr")
            
            self.scheduler.start()
            logger.info("✓ Scheduler gestartet")
            
        except Exception as e:
            logger.error(f"✗ Fehler beim Starten des Schedulers: {e}")
    
    def stop(self):
        """Stoppt den Scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✓ Scheduler gestoppt")
    
    def _scheduled_scrape(self):
        """Wird zu geplanten Zeiten aufgerufen"""
        try:
            logger.info(f"⏰ Geplantes Scraping gestartet um {datetime.now().strftime('%H:%M:%S')}")
            
            # Führe Scraping durch
            jobs = self.aggregator.scrape_all(
                SEARCH_QUERY,
                SEARCH_LOCATION,
                SEARCH_RADIUS
            )
            
            # Speichere Daten
            self.aggregator.save_to_excel()
            
            logger.info(f"✓ Geplantes Scraping abgeschlossen: {len(jobs)} Jobs gefunden")
            
            # Optional: Sende E-Mail bei neuen Jobs
            # if jobs:
            #     EmailService.send_job_notification(
            #         "your-email@example.com",
            #         jobs,
            #         " OR ".join(SEARCH_QUERY),
            #         SEARCH_LOCATION
            #     )
            
        except Exception as e:
            logger.error(f"✗ Fehler beim geplanten Scraping: {e}", exc_info=True)
