// ============================================================================
// INITIALISIERUNG
// ============================================================================

console.log('✓ Script geladen');

document.addEventListener('DOMContentLoaded', function() {
    console.log('✓ DOM geladen, initialisiere...');
    initializeApp();
});

function initializeApp() {
    console.log('✓ Initialisiere Anwendung...');
    
    // Lade Städte
    setTimeout(loadCities, 100);
    
    // Lade initiale Jobs
    setTimeout(loadJobs, 200);
    
    // Registriere Form Handler
    setTimeout(registerFormHandler, 300);
    
    console.log('✓ Initialisierung abgeschlossen');
}

// ============================================================================
// FORM HANDLER
// ============================================================================

function registerFormHandler() {
    console.log('✓ Registriere Form Handler...');
    
    const scrapeForm = document.getElementById('scrapeForm');
    
    if (!scrapeForm) {
        console.error('✗ Form nicht gefunden!');
        return;
    }
    
    // Entferne alte Event Listener
    const newForm = scrapeForm.cloneNode(true);
    scrapeForm.parentNode.replaceChild(newForm, scrapeForm);
    
    // Registriere neuen Listener
    document.getElementById('scrapeForm').addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('✓ Form submitted');
        performSearch();
    });
    
    console.log('✓ Form Handler registriert');
}

// ============================================================================
// SUCHE DURCHFÜHREN
// ============================================================================

async function performSearch() {
    console.log('→ Starte performSearch()');
    
    const queryInput = document.getElementById('query');
    const locationSelect = document.getElementById('location');
    const radiusInput = document.getElementById('radius');
    const statusDiv = document.getElementById('scrapeStatus');
    
    if (!queryInput || !locationSelect || !radiusInput || !statusDiv) {
        console.error('✗ Form-Elemente nicht gefunden!');
        return;
    }
    
    const query = queryInput.value.trim();
    const location = locationSelect.value;
    const radius = radiusInput.value;
    
    console.log('→ Suche mit:', { query, location, radius });
    
    if (!query) {
        statusDiv.innerHTML = '<div class="alert alert-warning">✗ Bitte geben Sie mindestens einen Job-Titel ein!</div>';
        return;
    }
    
    // Zeige Lade-Status
    statusDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Lädt...</span>
            </div>
            Scraping läuft... Dies kann bis zu 30 Sekunden dauern
        </div>
    `;
    
    try {
        console.log('→ Sende Scrape-Request...');
        
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
        
        console.log('→ Response Status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('→ Response Daten:', data);
        
        if (data.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    ✓ ${data.message}
                </div>
            `;
            
            console.log('→ Lade Jobs nach 1 Sekunde...');
            setTimeout(() => {
                loadJobs();
            }, 1000);
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-danger">
                    ✗ Fehler: ${data.message}
                </div>
            `;
            console.error('✗ API Error:', data);
        }
    } catch (error) {
        console.error('✗ Fetch Error:', error);
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                ✗ Fehler: ${error.message}
                <br><small>Konsole öffnen (F12) für Details</small>
            </div>
        `;
    }
}

// ============================================================================
// STÄDTE LADEN
// ============================================================================

async function loadCities() {
    console.log('→ loadCities() gestartet');
    
    try {
        const response = await fetch('/api/cities');
        console.log('→ Cities Response:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('→ Städte erhalten:', data.cities?.length || 0);
        
        if (data.success && data.cities && Array.isArray(data.cities)) {
            const locationSelect = document.getElementById('location');
            
            if (!locationSelect) {
                console.error('✗ Location-Select nicht gefunden!');
                return;
            }
            
            const currentValue = locationSelect.value;
            console.log('→ Aktueller Wert:', currentValue);
            
            // Füge alle Städte hinzu
            data.cities.forEach(city => {
                const exists = Array.from(locationSelect.options).some(opt => opt.value === city);
                
                if (!exists && city !== 'Deutschland') {
                    const option = document.createElement('option');
                    option.value = city;
                    option.text = city;
                    locationSelect.appendChild(option);
                    console.log('→ Stadt hinzugefügt:', city);
                }
            });
            
            console.log(`✓ ${data.cities.length} Städte geladen`);
        }
    } catch (error) {
        console.error('✗ Fehler beim Laden der Städte:', error);
    }
}

// ============================================================================
// JOBS LADEN
// ============================================================================

async function loadJobs() {
    console.log('→ loadJobs() gestartet');
    
    const jobsContainer = document.getElementById('jobsContainer');
    
    if (!jobsContainer) {
        console.error('✗ JobsContainer nicht gefunden!');
        return;
    }
    
    try {
        const response = await fetch('/api/jobs?limit=100');
        console.log('→ Jobs Response:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('→ Jobs erhalten:', data.count || 0);
        
        if (data.success && data.jobs && Array.isArray(data.jobs) && data.jobs.length > 0) {
            // Zähle Jobs pro Plattform
            const platformCounts = {};
            data.jobs.forEach(job => {
                const platform = job.Plattform || 'Unbekannt';
                platformCounts[platform] = (platformCounts[platform] || 0) + 1;
            });
            
            const platformSummary = Object.entries(platformCounts)
                .map(([platform, count]) => `<span class="badge bg-info ms-2">${platform}: ${count}</span>`)
                .join('');
            
            // Baue Tabelle
            const table = `
                <div class="mb-3">
                    <small>
                        Insgesamt: <strong>${data.count} Jobs</strong> 
                        ${platformSummary}
                    </small>
                </div>
                <table class="table table-striped table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>Datum</th>
                            <th>Plattform</th>
                            <th>Titel</th>
                            <th>Unternehmen</th>
                            <th>Standort</th>
                            <th>Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.jobs.map((job) => `
                            <tr>
                                <td><small>${formatDate(job.Datum)}</small></td>
                                <td><span class="badge bg-info platform-badge">${job.Plattform || 'N/A'}</span></td>
                                <td><strong>${escapeHtml(job.Titel) || 'N/A'}</strong></td>
                                <td>${escapeHtml(job.Unternehmen) || 'N/A'}</td>
                                <td><small>${escapeHtml(job.Standort) || 'Deutschland'}</small></td>
                                <td>
                                    ${job.Link ? `<a href="${escapeHtml(job.Link)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-primary">Zur Stelle →</a>` : '<small>Kein Link</small>'}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            
            jobsContainer.innerHTML = table;
            console.log(`✓ ${data.count} Jobs angezeigt`);
        } else {
            jobsContainer.innerHTML = `
                <p class="alert alert-warning">
                    ℹ Keine Jobs gefunden. Klicken Sie auf "Suchen" um Jobs zu laden.
                </p>
            `;
            console.log('ℹ Keine Jobs gefunden');
        }
    } catch (error) {
        console.error('✗ Fehler beim Laden der Jobs:', error);
        jobsContainer.innerHTML = `
            <p class="alert alert-danger">
                ✗ Fehler beim Laden: ${error.message}
            </p>
        `;
    }
}

// ============================================================================
// HILFSFUNKTIONEN
// ============================================================================

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('de-DE');
    } catch (error) {
        console.warn('Fehler beim Formatieren:', dateString);
        return dateString;
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

console.log('✓ Alle Funktionen definiert');
