import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os

# Globale Variablen
EXCEL_FILE = "stellenausschreibungen_erweitert.xlsx"
DATE = datetime.date.today()
QUERY = "CIO OR CTO OR Leiter IT OR Direktor IT OR Head of IT"
LOCATION = "Deutschland"

# LinkedIn API (Beispiel mit Scraping, da offizielle API stark eingeschränkt)
def scrape_linkedin():
    url = "https://de.linkedin.com/jobs/search/"
    params = {"keywords": QUERY, "location": LOCATION, "f_TPR": "r86400"}  # letzte 24h
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    for job in soup.find_all("div", class_="base-card"):
        title = job.find("h3")
        company = job.find("h4")
        link = job.find("a")
        if title and link:
            jobs.append({"Datum": DATE, "Plattform": "LinkedIn", "Titel": title.get_text(strip=True), "Unternehmen": company.get_text(strip=True) if company else "", "Link": link["href"]})
    return jobs

# Stepstone Scraping
def scrape_stepstone():
    url = "https://www.stepstone.de/jobs"
    params = {"searchText": QUERY, "location": LOCATION}
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    for job in soup.find_all("div", class_="job-item"):
        title = job.find("h2")
        company = job.find("span", class_="company")
        link = job.find("a")
        if title and link:
            jobs.append({"Datum": DATE, "Plattform": "Stepstone", "Titel": title.get_text(strip=True), "Unternehmen": company.get_text(strip=True) if company else "", "Link": "https://www.stepstone.de" + link["href"]})
    return jobs

# Xing Scraping
def scrape_xing():
    url = "https://www.xing.com/jobs"
    params = {"keywords": QUERY, "location": LOCATION}
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    for job in soup.find_all("li", class_="job"):
        title = job.find("h3")
        company = job.find("span", class_="company")
        link = job.find("a")
        if title and link:
            jobs.append({"Datum": DATE, "Plattform": "Xing", "Titel": title.get_text(strip=True), "Unternehmen": company.get_text(strip=True) if company else "", "Link": "https://www.xing.com" + link["href"]})
    return jobs

# Jobware Scraping
def scrape_jobware():
    url = "https://www.jobware.de/jobsuche"
    params = {"jw_jobname": QUERY, "jw_location": LOCATION}
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    for job in soup.find_all("div", class_="job"):
        title = job.find("h2")
        company = job.find("span", class_="company")
        link = job.find("a")
        if title and link:
            jobs.append({"Datum": DATE, "Plattform": "Jobware", "Titel": title.get_text(strip=True), "Unternehmen": company.get_text(strip=True) if company else "", "Link": "https://www.jobware.de" + link["href"]})
    return jobs

# Hauptfunktion
def main():
    all_jobs = []
    all_jobs.extend(scrape_linkedin())
    all_jobs.extend(scrape_stepstone())
    all_jobs.extend(scrape_xing())
    all_jobs.extend(scrape_jobware())

    # Speichern in Excel
    df = pd.DataFrame(all_jobs)
    if os.path.exists(EXCEL_FILE):
        existing_df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([existing_df, df], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    print(f"{len(all_jobs)} neue Stellenanzeigen wurden gefunden und gespeichert.")

if __name__ == "__main__":
    main()
