from flask import Flask, render_template, request, jsonify
import logging
import os
from datetime import datetime
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, LOG_LEVEL, PROJECT_NAME, LOG_FILE
from scrapers.job_aggregator import JobAggregator
from utils.search_helper import SearchHelper

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

# Flask-App initialisieren
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Globale Objekte
aggregator = JobAggregator()
search_helper = SearchHelper()

# ============================================================================
# SEITEN-ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Hauptseite"""
    try:
        logger.info("Index-Seite aufgerufen")
        cities = search_helper.get_available_cities()
        return render_template('index.html', title=PROJECT_NAME, cities=cities)
    except Exception as e:
        logger.error(f"Fehler auf Hauptseite: {e}", exc_info=True)
        return render_template('500.html'), 500

@app.route('/test')
def test_page():
    """Test-Seite für Debugging"""
    try:
        logger.info("Test-Seite aufgerufen")
        return render_template('test.html', title="Test")
    except Exception as e:
        logger.error(f"Fehler auf Test-Seite: {e}", exc_info=True)
        return render_template('500.html'), 500

# ============================================================================
# API-ENDPOINTS
# ============================================================================

@app.route('/api/test', methods=['GET'])
def api_test():
    """Test-Endpoint zum Debugging"""
    try:
        logger.info("API Test aufgerufen")
        return jsonify({
            "success": True,
            "message": "API funktioniert",
            "timestamp": datetime.now().isoformat(),
            "project": PROJECT_NAME
        }), 200
    except Exception as e:
        logger.error(f"Fehler in API Test: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/cities', methods=['GET'])
def api_cities():
    """API-Endpoint für verfügbare Städte"""
    try:
        logger.info("Cities-Endpoint aufgerufen")
        cities = search_helper.get_available_cities()
        logger.info(f"Rückgabe {len(cities)} Städte")
        return jsonify({
            "success": True,
            "cities": cities,
            "count": len(cities)
        }), 200
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Städte: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API-Endpoint zum Starten des Scrapings"""
    try:
        data = request.json or {}
        query = data.get('query', 'CIO OR CTO OR Leiter IT OR Direktor IT OR Head of IT')
        location = data.get('location', 'Deutschland')
        radius = int(data.get('radius', 50))
        
        logger.info(f"Scrape-Endpoint aufgerufen")
        logger.info(f"  - Query: {query}")
        logger.info(f"  - Location: {location}")
        logger.info(f"  - Radius: {radius}km")
        
        # Starte Scraping
        jobs = aggregator.scrape_all(query, location, radius)
        logger.info(f"Scraping abgeschlossen: {len(jobs)} Jobs gefunden")
        
        # Speichere in Excel
        aggregator.save_to_excel()
        logger.info("Daten gespeichert")
        
        return jsonify({
            "success": True,
            "message": f"{len(jobs)} Jobs gefunden und gespeichert",
            "count": len(jobs),
            "query": query,
            "location": location,
            "radius": radius
        }), 200
        
    except ValueError as e:
        logger.error(f"Validierungsfehler beim Scraping: {e}")
        return jsonify({
            "success": False,
            "message": f"Validierungsfehler: {str(e)}"
        }), 400
    except Exception as e:
        logger.error(f"Fehler beim Scraping: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Fehler beim Scraping: {str(e)}"
        }), 500

@app.route('/api/jobs', methods=['GET'])
def api_jobs():
    """API-Endpoint zum Abrufen der gespeicherten Jobs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        logger.info(f"Jobs-Endpoint aufgerufen (limit={limit})")
        
        jobs = aggregator.get_latest_jobs(limit)
        logger.info(f"Rückgabe {len(jobs)} Jobs")
        
        return jsonify({
            "success": True,
            "count": len(jobs),
            "limit": limit,
            "jobs": jobs
        }), 200
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen von Jobs: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Fehler beim Abrufen: {str(e)}"
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 Error Handler"""
    logger.warning(f"404 Fehler: {error}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 Error Handler"""
    logger.error(f"500 Fehler: {error}", exc_info=True)
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Globaler Exception Handler"""
    logger.error(f"Unerwarteter Fehler: {e}", exc_info=True)
    return jsonify({
        "success": False,
        "message": "Interner Server-Fehler"
    }), 500

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health Check Endpoint"""
    return jsonify({
        "status": "healthy",
        "project": PROJECT_NAME,
        "timestamp": datetime.now().isoformat()
    }), 200

# ============================================================================
# BEFORE & AFTER HANDLERS
# ============================================================================

@app.before_request
def before_request():
    """Vor jedem Request"""
    logger.debug(f"{request.method} {request.path}")

@app.after_request
def after_request(response):
    """Nach jedem Request"""
    logger.debug(f"Response: {response.status_code}")
    return response

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info(f"Starte {PROJECT_NAME}")
    logger.info(f"Version: {PROJECT_VERSION if 'PROJECT_VERSION' in dir() else 'unbekannt'}")
    logger.info(f"Host: {FLASK_HOST}")
    logger.info(f"Port: {FLASK_PORT}")
    logger.info(f"Debug: {FLASK_DEBUG}")
    logger.info("=" * 80)
    
    try:
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {e}", exc_info=True)
        raise
