import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import EMAIL_CONFIG

logger = logging.getLogger(__name__)

class EmailService:
    """Service für E-Mail-Benachrichtigungen"""
    
    @staticmethod
    def send_job_notification(recipient_email, jobs, query, location):
        """Sendet E-Mail mit neuen Jobs"""
        
        if not EMAIL_CONFIG.get('enabled'):
            logger.info("E-Mail-Service ist deaktiviert")
            return False
        
        try:
            # Baue HTML-Content
            html_content = EmailService._build_html(jobs, query, location)
            
            # Erstelle E-Mail
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎯 {len(jobs)} neue IT-Jobs gefunden - {query}"
            msg['From'] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['sender_email']}>"
            msg['To'] = recipient_email
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Versende
            logger.info(f"Sende E-Mail an {recipient_email}...")
            
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
                server.send_message(msg)
            
            logger.info(f"✓ E-Mail versendet an {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Fehler beim Versenden der E-Mail: {e}")
            return False
    
    @staticmethod
    def _build_html(jobs, query, location):
        """Baut HTML-Content für E-Mail"""
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }}
                h1 {{ color: #007bff; }}
                .job {{ border-left: 4px solid #007bff; padding: 15px; margin: 15px 0; background-color: #f9f9f9; }}
                .job-title {{ font-size: 18px; font-weight: bold; color: #333; }}
                .job-company {{ color: #666; font-size: 14px; }}
                .job-location {{ color: #999; font-size: 12px; }}
                .job-link {{ margin-top: 10px; }}
                a {{ color: #007bff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 {len(jobs)} neue IT-Jobs gefunden!</h1>
                
                <p>
                    <strong>Suchkriterien:</strong><br>
                    Job-Titel: {query}<br>
                    Standort: {location}
                </p>
                
                <hr>
        """
        
        for job in jobs:
            salary_info = ""
            if job.get('Salary_Min') and job.get('Salary_Max'):
                salary_info = f" | {job['Salary_Min']:,.0f} - {job['Salary_Max']:,.0f} EUR"
            
            html += f"""
                <div class="job">
                    <div class="job-title">{job.get('Titel', 'N/A')}</div>
                    <div class="job-company">{job.get('Unternehmen', 'N/A')}</div>
                    <div class="job-location">{job.get('Standort', 'N/A')} {salary_info}</div>
                    <div class="job-link">
                        <a href="{job.get('Link', '#')}">Zur Stellenanzeige →</a>
                    </div>
                </div>
            """
        
        html += f"""
                <div class="footer">
                    <p>Nachricht vom Job Scraper<br>
                    {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
