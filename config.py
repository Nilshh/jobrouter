import os
from datetime import datetime

# Allgemeine Einstellungen
PROJECT_NAME = "Job Scraper für IT-Führungspositionen"
PROJECT_VERSION = "2.0.0"

# Suchparameter
SEARCH_QUERY = ["CIO", "CTO", "Leiter IT", "Direktor IT", "Head of IT"]
SEARCH_LOCATION = "Deutschland"
SEARCH_LANGUAGE = "de"

# Dateieinstellungen
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
EXCEL_FILE = os.path.join(DATA_DIR, "stellenausschreibungen.xlsx")

# Excel-Spalten
EXCEL_COLUMNS = ["Datum", "Plattform", "Titel", "Unternehmen", "Standort", "Link", "Beschreibung"]

# Flask-Einstellungen
FLASK_DEBUG = True
FLASK_PORT = 5000
FLASK_HOST = "0.0.0.0"

# Logging
LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")
LOG_LEVEL = "INFO"

# Jobbörsen-Einstellungen
SCRAPERS = {
    "linkedin": {"enabled": True, "timeout": 15},
    "stepstone": {"enabled": True, "timeout": 15},
    "xing": {"enabled": True, "timeout": 15},
    "jobware": {"enabled": True, "timeout": 15},
}

# HTTP-Header
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Erstelle Verzeichnisse, falls nicht vorhanden
for directory in [DATA_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)
