import logging
import re
from config import SALARY_CONFIG

logger = logging.getLogger(__name__)

class SalaryExtractor:
    """Extrahiert Gehaltsinformationen aus Job-Beschreibungen"""
    
    # Regex-Muster für verschiedene Formate
    PATTERNS = [
        # "50.000 - 70.000 EUR"
        r'€?\s*(\d+\.?\d*)\s*k?\s*[-–]\s*€?\s*(\d+\.?\d*)\s*k?\s*(€|EUR|K)?',
        # "ab 60.000 EUR"
        r'ab\s*€?\s*(\d+\.?\d*)\s*k?\s*(€|EUR)?',
        # "€ 70000 - € 90000"
        r'€?\s*(\d+\.?\d+)\s*[-–]\s*€?\s*(\d+\.?\d+)',
    ]
    
    @staticmethod
    def extract(description):
        """
        Extrahiert Gehalt aus Beschreibung
        
        Returns:
            dict mit 'min' und 'max' Werten oder None
        """
        if not description:
            return None
        
        description = description.lower()
        
        for pattern in SalaryExtractor.PATTERNS:
            matches = re.findall(pattern, description, re.IGNORECASE)
            
            if matches:
                try:
                    if len(matches[0]) >= 2:
                        min_salary = int(float(matches[0][0].replace('.', '')) * 1000)
                        max_salary = int(float(matches[0][1].replace('.', '')) * 1000)
                        
                        # Validierung
                        if (SALARY_CONFIG['min_range'] <= min_salary <= SALARY_CONFIG['max_range'] and
                            SALARY_CONFIG['min_range'] <= max_salary <= SALARY_CONFIG['max_range']):
                            return {
                                'min': min_salary,
                                'max': max_salary
                            }
                except (ValueError, IndexError):
                    continue
        
        logger.debug("Kein Gehalt gefunden")
        return None
