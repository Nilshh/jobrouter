import logging
import math
from config import GERMAN_CITIES

logger = logging.getLogger(__name__)

class SearchHelper:
    """Hilfsfunktionen für Job-Suche"""
    
    @staticmethod
    def get_cities_in_radius(city_name, radius_km):
        """
        Findet alle Städte im Umkreis einer bestimmten Stadt
        
        Args:
            city_name: Name der Ausgangsstadt
            radius_km: Radius in Kilometern
            
        Returns:
            Liste von Stadtnamen im Radius
        """
        if city_name not in GERMAN_CITIES:
            logger.warning(f"Stadt '{city_name}' nicht in Datenbank, gebe {city_name} zurück")
            return [city_name]
        
        center = GERMAN_CITIES[city_name]
        cities_in_radius = [city_name]
        
        for city, coords in GERMAN_CITIES.items():
            if city == city_name:
                continue
            
            # Haversine-Formel für Distanzberechnung
            distance = SearchHelper._haversine_distance(
                center["lat"], center["lon"],
                coords["lat"], coords["lon"]
            )
            
            if distance <= radius_km:
                cities_in_radius.append(city)
                logger.debug(f"Stadt {city} ist {distance:.1f}km von {city_name} entfernt")
        
        logger.info(f"Gefunden {len(cities_in_radius)} Städte im {radius_km}km Radius von {city_name}")
        return cities_in_radius
    
    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """
        Berechnet die Distanz zwischen zwei geografischen Punkten
        
        Returns:
            Distanz in Kilometern
        """
        R = 6371  # Erdradius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def format_search_query(job_titles):
        """
        Formatiert Job-Titel für Suchanfrage
        
        Args:
            job_titles: String oder Liste von Job-Titeln
            
        Returns:
            Formatierter Such-String mit OR-Operatoren
        """
        if isinstance(job_titles, str):
            titles = [t.strip() for t in job_titles.split(",") if t.strip()]
        else:
            titles = job_titles
        
        return " OR ".join(titles)
    
    @staticmethod
    def get_available_cities():
        """Gibt Liste aller verfügbaren Städte zurück"""
        return sorted(list(GERMAN_CITIES.keys()))
