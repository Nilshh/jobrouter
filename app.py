from flask import Flask, render_template, request, jsonify
import logging
import os
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, LOG_LEVEL, PROJECT_NAME, LOG_FILE
from scrapers.job_aggregator import JobAggregator

# Logging konfigurieren
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
aggregator = JobAggregator()

@app.route('/')
def index():
    """Hauptseite"""
    logger.info("Index-Seite aufgerufen")
    return render_template('index.html', title=PROJECT_NAME)

@app.route('/api/scrape', methods=['POST'])
def scrape_jobs():
    """API-Endpoint zum Starten des Scrapings"""
    try:
        data = request.json or {}
        query = data.get('query', 'CIO OR CTO OR Leiter IT OR Direktor IT OR Head of IT')
        location = data.get('location', 'Deutschland')
        
        logger.info(f"Starte Scraping mit Query: {query}, Location: {location}")
        
        jobs = aggregator.scrape_all(query, location)
        aggregator.save_to_excel()
        
        logger.info(f"Scraping abgeschlossen: {len(jobs)} Jobs gefunden")
        
        return jsonify({
            "success": True,
            "message": f"{len(jobs)} Jobs gefunden",
            "count": len(jobs)
        })
    except Exception as e:
        logger.error(f"Fehler beim Scraping: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """API-Endpoint zum Abrufen der gespeicherten Jobs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        jobs = aggregator.get_latest_jobs(limit)
        
        logger.info(f"Jobs abgerufen: {len(jobs)} Einträge")
        
        return jsonify({
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        })
    except Exception as e:
        logger.error(f"Fehler beim Abrufen von Jobs: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Fehler: {error}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Fehler: {error}", exc_info=True)
    return render_template('500.html'), 500

if __name__ == '__main__':
    logger.info(f"=== Starte {PROJECT_NAME} ===")
    logger.info(f"Host: {FLASK_HOST}, Port: {FLASK_PORT}, Debug: {FLASK_DEBUG}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
