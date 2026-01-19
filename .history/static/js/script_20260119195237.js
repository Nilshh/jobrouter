console.log('✓ Script geladen');

// Warte auf DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('✓ DOM geladen, initialisiere...');
    
    // Kurze Verzögerung um sicherzustellen dass alle Elemente vorhanden sind
    setTimeout(function() {
        initializeApp();
    }, 100);
});

function initializeApp() {
    console.log('✓ initializeApp() aufgerufen');
    
    // Lade Städte
    loadCities();
    
    // Lade initiale Jobs
    loadJobs();
    
    // Registriere Button-Handler
    registerButtonHandlers();
}

function registerButtonHandlers() {
    console.log('✓ Registriere Button-Handler...');
    
    // Search Button
    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('✓ Search-Button geklickt');
            performSearch();
        });
        console.log('✓ Search-Button Handler registriert');
    } else {
        console.error('✗ searchBtn nicht gefunden!');
    }
    
    // Reset Button
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('✓ Reset-Button geklickt');
            document.getElementById('query').value = 'CIO, CTO, Leiter IT, Direktor IT, Head of IT';
            document.getElementById('location').value = 'Deutschland';
            document.getElementById('radius').value = '50';
        });
        console.log('✓ Reset-Button Handler registriert');
    } else {
        console.error('✗ resetBtn nicht gefunden!');
    }
}

// Lade Städte
async function loadCities() {
    console.log('→ Lade Städte...');
    
    try {
        const response = await fetch('/api/cities');
        const data = await response.json();
        
        if (data.success && data.cities) {
            const select = document.getElementById('location');
            if (!select) {
                console.error('✗ Location-Select nicht gefunden!');
                return;
            }
            
            data.cities.forEach(city => {
                const exists = Array.from(select.options).some(opt => opt.value === city);
                if (!exists) {
                    const option = document.createElement('option');
                    option.value = city;
                    option.text = city;
                    select.appendChild(option);
                }
            });
            console.log(`✓ ${data.cities.length} Städte geladen`);
        }
    } catch (error) {
        console.error('✗ Fehler beim Laden der Städte:', error);
    }
}

// Führe Suche durch
async function performSearch() {
    console.log('→ performSearch() aufgerufen');
    
    const queryInput = document.getElementById('query');
    const locationSelect = document.getElementById('location');
    const radiusInput = document.getElementById('radius');
    const statusDiv = document.getElementById('scrapeStatus');
    
    if (!queryInput || !locationSelect || !radiusInput || !statusDiv) {
        console.error('✗ Formular-Elemente nicht gefunden!', {
            query: queryInput ? '✓' : '✗',
            location: locationSelect ? '✓' : '✗',
            radius: radiusInput ? '✓' : '✗',
            status: statusDiv ? '✓' : '✗'
        });
        return;
    }
    
    const query = queryInput.value.trim();
    const location = locationSelect.value;
    const radius = radiusInput.value;
    
    console.log('→ Suche mit:', { query, location, radius });
    
    if (!query) {
        statusDiv.innerHTML = '<div class="alert alert-warning">⚠ Bitte geben Sie einen Job-Titel ein!</div>';
        return;
    }
    
    statusDiv.innerHTML = '<div class="alert alert-info">⏳ Scraping läuft... Dies kann bis zu 30 Sekunden dauern</div>';
    
    try {
        console.log('→ Sende Scrape-Request...');
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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
        console.log('→ Response Data:', data);
        
        if (data.success) {
            statusDiv.innerHTML = `<div class="alert alert-success">✓ ${data.message}</div>`;
            console.log('→ Lade Jobs nach 1 Sekunde...');
            setTimeout(() => {
                loadJobs();
            }, 1000);
        } else {
            statusDiv.innerHTML = `<div class="alert alert-danger">✗ Fehler: ${data.message}</div>`;
            console.error('✗ API Fehler:', data);
        }
    } catch (error) {
        console.error('✗ Fetch-Fehler:', error);
        statusDiv.innerHTML = `<div class="alert alert-danger">✗ Fehler: ${error.message}</div>`;
    }
}

// Lade Jobs
async function loadJobs() {
    console.log('→ Lade Jobs...');
    
    try {
        const response = await fetch('/api/jobs?limit=100');
        const data = await response.json();
        const container = document.getElementById('jobsContainer');
        
        if (!container) {
            console.error('✗ jobsContainer nicht gefunden!');
            return;
        }
        
        console.log('→ Jobs Response:', data);
        
        if (data.success && data.jobs && data.jobs.length > 0) {
            // Zähle Jobs pro Plattform
            const platformCounts = {};
            data.jobs.forEach(job => {
                const p = job.Plattform || 'Demo';
                platformCounts[p] = (platformCounts[p] || 0) + 1;
            });
            
            const badges = Object.entries(platformCounts)
                .map(([p, c]) => `<span class="badge bg-info ms-2">${p}: ${c}</span>`)
                .join('');
            
            // Baue HTML
            let html = `<div class="mb-3"><small>Insgesamt: <strong>${data.count} Jobs</strong> ${badges}</small></div>`;
            html += '<table class="table table-striped table-hover">';
            html += '<thead class="table-dark"><tr>';
            html += '<th>Datum</th><th>Plattform</th><th>Titel</th><th>Unternehmen</th><th>Standort</th><th>Link</th>';
            html += '</tr></thead><tbody>';
            
            data.jobs.forEach(job => {
                html += '<tr>';
                html += `<td><small>${job.Datum || ''}</small></td>`;
                html += `<td><span class="badge bg-info">${job.Plattform || 'N/A'}</span></td>`;
                html += `<td><strong>${job.Titel || ''}</strong></td>`;
                html += `<td>${job.Unternehmen || ''}</td>`;
                html += `<td><small>${job.Standort || ''}</small></td>`;
                html += `<td><a href="${job.Link}" target="_blank" class="btn btn-sm btn-outline-primary">Link →</a></td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
            console.log(`✓ ${data.count} Jobs angezeigt`);
        } else {
            container.innerHTML = '<p class="alert alert-warning">ℹ Keine Jobs gefunden. Klicken Sie auf "Suchen"!</p>';
            console.log('ℹ Keine Jobs vorhanden');
        }
    } catch (error) {
        console.error('✗ Fehler beim Laden der Jobs:', error);
        document.getElementById('jobsContainer').innerHTML = `<div class="alert alert-danger">✗ Fehler: ${error.message}</div>`;
    }
}

console.log('✓ Alle Funktionen definiert und bereit');
