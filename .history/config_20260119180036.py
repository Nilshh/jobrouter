import os
from datetime import datetime

# Allgemeine Einstellungen
PROJECT_NAME = "Job Scraper für IT-Führungspositionen"
PROJECT_VERSION = "2.1.0"

# Standard-Suchparameter
SEARCH_QUERY = ["CIO", "CTO", "Leiter IT", "Direktor IT", "Head of IT"]
SEARCH_LOCATION = "Hamburg"
SEARCH_RADIUS = 50  # km
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
    "demo": {"enabled": True, "timeout": 5},
    "indeed": {"enabled": True, "timeout": 15},
    "heise": {"enabled": True, "timeout": 15},
    "stepstone": {"enabled": False, "timeout": 15},
    "xing": {"enabled": False, "timeout": 15},
    "jobware": {"enabled": False, "timeout": 15},
}

# HTTP-Header
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Deutsche Städte mit Koordinaten für Radius-Suche
GERMAN_CITIES = {
    "Berlin": {"lat": 52.52, "lon": 13.405},
    "München": {"lat": 48.1351, "lon": 11.582},
    "Hamburg": {"lat": 53.5511, "lon": 9.4821},
    "Köln": {"lat": 50.9375, "lon": 6.9603},
    "Frankfurt": {"lat": 50.1109, "lon": 8.6821},
    "Stuttgart": {"lat": 48.7758, "lon": 9.1829},
    "Düsseldorf": {"lat": 51.2277, "lon": 6.7735},
    "Dortmund": {"lat": 51.5136, "lon": 7.4653},
    "Essen": {"lat": 51.4556, "lon": 7.0116},
    "Leipzig": {"lat": 51.3397, "lon": 12.3731},
    "Dresden": {"lat": 51.0504, "lon": 13.7373},
    "Hannover": {"lat": 52.3759, "lon": 9.7452},
    "Nürnberg": {"lat": 49.4521, "lon": 11.0767},
    "Duisburg": {"lat": 51.4344, "lon": 6.7573},
    "Bochum": {"lat": 51.4819, "lon": 7.2169},
    "Wuppertal": {"lat": 51.2559, "lon": 7.1501},
    "Bielefeld": {"lat": 52.0302, "lon": 8.5325},
    "Bonn": {"lat": 50.7353, "lon": 7.0920},
    "Mannheim": {"lat": 49.4875, "lon": 8.4675},
    "Karlsruhe": {"lat": 49.0069, "lon": 8.4037},
}

# Erstelle Verzeichnisse, falls nicht vorhanden
for directory in [DATA_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)
