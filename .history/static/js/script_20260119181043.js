// Warte bis das DOM vollständig geladen ist
document.addEventListener('DOMContentLoaded', function() {
    console.log('✓ DOM geladen');
    
    // Initialisiere die Anwendung
    initializeApp();
});

function initializeApp() {
    console.log('✓ Initialisiere Anwendung...');
    
    // Lade Städte
    loadCities();
    
    // Lade initiale Jobs
    loadJobs();
    
    // Registriere Form-Handler
    registerFormHandler();
}

// Registriere Form Submit Handler
function registerFormHandler() {
    console.log('✓ Registriere Form Handler...');
    
    const scrapeForm = document.getElementById('scrapeForm');
    
    if (!scrapeForm) {
        console.error('✗ Form mit ID "scrapeForm" nicht gefunden!');
        return;
    }
    
    scrapeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        performSearch();
    });
    
    console.log('✓ Form Handler registriert');
}

// Führe Suche durch
async function performSearch() {
    const query = document.getElementById('query')?.value || '';
    const location = document.getElementById('location')?.value || 'Deutschland';
    const radius = document.getElementById('radius')?.value || '50';
    const statusDiv = document.getElementById('scrapeStatus');
    
    if (!query) {
        statusDiv.innerHTML = '<div class="alert alert-warning">✗ Bitte geben Sie mindestens einen Job-Titel ein!</div>';
        return;
    }
    
    console.log('→ Starte Scraping mit:', { query, location, radius });
    
    // Zeige Lade-Status
    statusDiv.innerHTML = `
        <div class="alert alert-info">
            <span class="loading"></span> Scraping läuft... 
            <br><small>Dies kann bis zu 30 Sekunden dauern</small>
        </div>
    `;
    
    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                location: location,
                radius: parseInt(radius)
            })
        });
        
        console.log('→ Response erhalten:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP Fehler: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('→ Response-Daten:', data);
        
        if (data.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    ✓ ${data.message}
                </div>
            `;
            
            // Lade Jobs nach kurzer Verzögerung
            setTimeout(() => {
                console.log('→ Lade aktualisierte Jobs...');
                loadJobs();
            }, 1000);
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    ✗ Fehler: ${data.message}
                </div>
            `;
            console.error('✗ API-Fehler:', data);
        }
    } catch (error) {
        console.error('✗ Fetch-Fehler:', error);
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                ✗ Fehler: ${error.message}
                <br><small>Überprüfen Sie die Browser-Konsole (F12) für mehr Details</small>
            </div>
        `;
    }
}

// Lade verfügbare Städte
async function loadCities() {
    console.log('→ Lade Städte...');
    
    try {
        const response = await fetch('/api/cities');
        
        if (!response.ok) {
            throw new Error(`HTTP Fehler: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('→ Städte erhalten:', data.cities?.length || 0);
        
        if (data.success && data.cities && Array.isArray(data.cities)) {
            const locationSelect = document.getElementById('location');
            
            if (!locationSelect) {
                console.error('✗ Select-Element mit ID "location" nicht gefunden!');
                return;
            }
            
            const currentValue = locationSelect.value;
            
            // Füge Städte hinzu
            data.cities.forEach(city => {
                // Prüfe, ob Option bereits existiert
                const exists = Array.from(locationSelect.options).some(opt => opt.value === city);
                
                if (!exists) {
                    const option = document.createElement('option');
                    option.value = city;
                    option.text = city;
                    locationSelect.appendChild(option);
                }
            });
            
            // Behalte den aktuellen Wert
            if (locationSelect.querySelector(`option[value="${currentValue}"]`)) {
                locationSelect.value = currentValue;
            }
            
            console.log(`✓ ${data.cities.length} Städte geladen`);
        } else {
            console.warn('⚠ Keine Städte in Response gefunden');
        }
    } catch (error) {
        console.error('✗ Fehler beim Laden der St
