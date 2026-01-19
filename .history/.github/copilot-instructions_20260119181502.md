# Copilot / AI Agent Instructions

Kurz: Diese Datei hilft AI-Codieragenten, schnell produktiv zu werden.

1) Big Picture
- Dieses Projekt ist eine einfache Flask-Web-App (`app.py`) die Job-Angebote aus mehreren Scraper-Modulen sammelt, zusammenführt und in einer Excel-Datei persistiert (`data/stellenausschreibungen.xlsx`).
- Architektur: HTTP-API (Flask) -> `scrapers/job_aggregator.py` orchestriert einzelne Scraper in `scrapers/*.py` -> Ergebnisse werden mit `pandas` in `EXCEL_FILE` gespeichert.

2) Wichtige Dateien & Rollen
- [app.py](app.py): Flask-Routen (`/`, `/api/scrape`, `/api/jobs`, `/api/cities`) und Logging-Setup.
- [config.py](config.py): zentrale Konfiguration (SCRAPERS feature flags, EXCEL_COLUMNS, Pfade, GERMAN_CITIES).
- [scrapers/base_scraper.py](scrapers/base_scraper.py): gemeinsame Basis-API: `fetch_page`, `format_job` und abstrakte `scrape()`.
- `scrapers/*.py`: Implementierungen; besonders `demo_scraper.py`, `indeed_scraper.py` und `job_aggregator.py` (Orchestrator).
- [utils/search_helper.py](utils/search_helper.py): Geodaten-Utilities (`get_cities_in_radius`) und Query-Formatierung.

3) Konventionen & Patterns (Projekt-spezifisch)
- Scraper-Registrierung: `JobAggregator.__init__` baut ein `self.scrapers` dict; Reihenfolge und Aktivierung werden in `config.SCRAPERS` gesteuert.
- Jeder Scraper liefert eine Liste von dicts mit exakt den Spalten `EXCEL_COLUMNS` (siehe `config.EXCEL_COLUMNS`). Verwende `BaseScraper.format_job` zum Konsistenthalten der Felder.
- Deduplication: `save_to_excel()` hängt neue Daten an und entfernt Duplikate anhand `['Titel', 'Link']` — Änderungen an diesen Spalten beeinflussen Dupe-Logik.
- Query-Format: `SearchHelper.format_search_query` und Demo-Scraper erwarten OR-getrennte Begriffe; einige Scraper (z.B. `indeed_scraper.py`) erwarten `query` als String oder Liste und bauen einen `query_str`.
- Fehlerbehandlung: Scraper-Methoden fangen Exceptions lokal und loggen Fehler; der Aggregator überspringt fehlerhafte Scraper und fährt fort.

4) Lauf- und Entwicklungs-Workflows
- Lokales Entwickeln: `python app.py` startet Flask (Konfiguration in `config.py`, `FLASK_DEBUG` standardmäßig True).
- Abhängigkeiten: `requirements.txt` (verwende eine virtuelle Umgebung und `pip install -r requirements.txt`).
- Docker: Das Repo enthält `Dockerfile` und `docker-compose.yml` — zum Bauen/Starten siehe vorhandene Dateien; Standard-Entrypoint startet vermutlich `app.py`.
- Logs/Output: Laufzeit-Logs landen in `logs/` (Pfad aus `config.LOG_FILE`), Daten werden in `data/stellenausschreibungen.xlsx` gespeichert.

5) Sicherheits- & Netzwerkkontexte
- Scraper verwenden direkte HTTP-Requests (`requests`, `feedparser`) und dürfen Timeouts/Delays respektieren (`BaseScraper.fetch_page` hat einen `time.sleep(1)`).
- `DEFAULT_HEADERS` in `config.py` enthält User-Agent; benutze das, wenn du neue HTTP-Aufrufe implementierst.

6) Änderungen, Vorschläge & typische Agent-Aufgaben
- Wenn du einen neuen Scraper hinzufügst: implementiere `class XScraper(BaseScraper)` in `scrapers/`, registriere ihn in `JobAggregator.self.scrapers` und aktiviere in `config.SCRAPERS`.
- Beim Ändern von Spalten: aktualisiere `config.EXCEL_COLUMNS` und prüfe `save_to_excel()` Dedup-Logik.
- Für Debugging: prüfe `logs/` und setze `LOG_LEVEL` in `config.py`; beim Entwickeln lokal `FLASK_DEBUG=True`.

7) Beispiele aus dem Code (schnellreferenz)
- OR-Query Verarbeitung: `indeed_scraper.py` und `demo_scraper.py` (split bzw. join mit " OR ").
- Radius-Logik: `utils/search_helper.get_cities_in_radius(city, radius)` verwendet Haversine-Formel.
- Excel Speicherung: `scrapers/job_aggregator.save_to_excel()` (pandas, drop_duplicates(['Titel','Link'])).

8) Eingrenzungen / Nicht-erkannte Annahmen
- Keine Tests im Repo — schreibe Unit-Tests für Scraper-Parsing, Query-Formattierung und Excel-Persistenz wenn nötig.
- Externe Integrationen (z.B. private APIs, authentifizierte Jobbörsen) sind nicht vorhanden; implementiere Credentials sicher (nicht in `config.py`).

Feedback
- Bitte prüfe diese Zusammenfassung. Sag mir, ob du mehr Details zu Docker, CI, oder einem konkreten Scraper möchtest — ich iteriere die Datei dann nach deinem Feedback.
