// Lade Jobs beim Seitenstart
document.addEventListener('DOMContentLoaded', function() {
    console.log('Seite geladen, lade Jobs...');
    loadJobs();
});

// Form Submit Handler
const scrapeForm = document.getElementById('scrapeForm');
if (scrapeForm) {
    scrapeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const query = document.getElementById('query').value;
        const location = document.getElementById('location').value;
        const statusDiv = document.getElementById('scrapeStatus');
        
        console.log('Starte Scraping mit Query:', query, 'Location:', location);
        
        statusDiv.innerHTML = '<div class="alert alert-info"><span class="loading"></span> Scraping läuft...</div>';
        
        try {
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query, location })
            });
            
            const data = await response.json();
            console.log('Scraping Response:', data);
            
            if (data.success) {
                statusDiv.innerHTML = `<div class="alert alert-success">✓ ${data.message}</div>`;
                setTimeout(() => {
                    loadJobs();
                }, 1000);
            } else {
                statusDiv.innerHTML = `<div class="alert alert-danger">✗ Fehler: ${data.message}</div>`;
            }
        } catch (error) {
            console.error('Fehler:', error);
            statusDiv.innerHTML = `<div class="alert alert-danger">✗ Fehler: ${error.message}</div>`;
        }
    });
}

// Lade Jobs vom Server
async function loadJobs() {
    console.log('Lade Jobs vom Server...');
    
    try {
        const response = await fetch('/api/jobs?limit=50');
        const data = await response.json();
        
        console.log('Jobs Response:', data);
        
        if (data.success && data.jobs && data.jobs.length > 0) {
            const jobsContainer = document.getElementById('jobsContainer');
            
            const table = `
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
                        ${data.jobs.map((job, index) => `
                            <tr>
                                <td>${formatDate(job.Datum)}</td>
                                <td><span class="badge bg-info platform-badge">${job.Plattform || 'N/A'}</span></td>
                                <td><strong>${job.Titel || 'N/A'}</strong></td>
                                <td>${job.Unternehmen || 'N/A'}</td>
                                <td>${job.Standort || 'Deutschland'}</td>
                                <td>
                                    ${job.Link ? `<a href="${job.Link}" target="_blank" class="btn btn-sm btn-outline-primary">Zur Stelle →</a>` : 'Kein Link'}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            jobsContainer.innerHTML = table;
        } else {
            const jobsContainer = document.getElementById('jobsContainer');
            jobsContainer.innerHTML = '<p class="alert alert-warning">Keine Jobs gefunden. Klicken Sie auf "Suchen" um Jobs zu laden.</p>';
        }
    } catch (error) {
        console.error('Fehler beim Laden:', error);
        const jobsContainer = document.getElementById('jobsContainer');
        jobsContainer.innerHTML = `<p class="alert alert-danger">Fehler beim Laden: ${error.message}</p>`;
    }
}

// Formatiere Datum
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE');
}

// Refresh Button (optional)
function refreshJobs() {
    console.log('Aktualisiere Jobs...');
    loadJobs();
}
