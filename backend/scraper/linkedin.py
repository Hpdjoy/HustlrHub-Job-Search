import requests
from bs4 import BeautifulSoup
import re
import time
import concurrent.futures
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from backend.config import settings
from backend.utils import helpers
from backend.storage import manager

# Track seen jobs to avoid duplicates within a session
seen_jobs = set()

def build_url(role, start, experience_level="1,2"):
    """Build LinkedIn job search URL with fresher filters."""
    # Experience levels: 1=Internship, 2=Entry level, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive
    # f_TPR=r86400 filters for last 24 hours (smallest reliable unit for Guest API)
    return (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={role.replace(' ', '%20')}"
        f"&location={settings.LOCATION.replace(' ', '%20')}"
        f"&f_E={experience_level}"  # Filter by experience level
        f"&f_TPR=r86400"  # Filter by time posted (last 24 hours)
        f"&start={start}"
        f"&sortBy=DD"  # Sort by date (most recent first)
    )

def get_job_details_with_selenium(job_url):
    """Fetch job details including applicant count using Selenium."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(job_url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Extract applicant count
        applicants = "N/A"
        try:
            applicant_element = driver.find_element(By.CSS_SELECTOR, ".num-applicants__caption")
            applicants = applicant_element.text.strip()
        except NoSuchElementException:
            try:
                # Alternative selector
                applicant_element = driver.find_element(By.XPATH, "//*[contains(text(), 'applicants')]")
                applicants = applicant_element.text.strip()
            except:
                pass
        
        # Extract job description
        description = ""
        try:
            desc_element = driver.find_element(By.CLASS_NAME, "show-more-less-html__markup")
            description = desc_element.text.strip()
        except NoSuchElementException:
            pass
        
        # Extract location
        location = ""
        try:
            location_element = driver.find_element(By.CSS_SELECTOR, ".topcard__flavor--bullet")
            location = location_element.text.strip()
        except NoSuchElementException:
            pass
        
        driver.quit()
        
        return {
            "applicants": applicants,
            "description": description,
            "location": location
        }
    except Exception as e:
        print(f"Error fetching job details: {e}")
        return {
            "applicants": "N/A",
            "description": "",
            "location": ""
        }

def extract_jobs(html):
    """Extract jobs from LinkedIn HTML response."""
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for job in soup.find_all("li"):

        # -------- Extract Title, Company, Link --------
        title_tag = job.find("h3")
        company_tag = job.find("h4")
        link_tag = job.find("a", href=True)

        if not (title_tag and company_tag and link_tag):
            continue

        title = title_tag.text.strip()
        company = company_tag.text.strip()

        # Skip blacklisted companies
        if any(blacklisted.lower() in company.lower() for blacklisted in settings.BLACKLISTED_COMPANIES):
            continue

        raw_link = link_tag["href"]

        # --- FIX MALFORMED LINKS ---
        if raw_link.startswith("http"):
            link = raw_link
        else:
            link = "https://www.linkedin.com" + raw_link

        link = link.replace("https://www.linkedin.comhttps//", "https://")
        link = link.replace("https//", "https://")
        link = link.replace("https:https://", "https://")
        # ------------------------------------------------

        # Extract job ID for duplicate detection
        job_id_match = re.search(r'/view/([^?/]+)', link)
        job_id = job_id_match.group(1) if job_id_match else link
        
        # Skip duplicates
        if job_id in seen_jobs:
            continue
        
        # -------- Parse posted time --------
        time_tag = job.find("time")
        time_text = time_tag.text if time_tag else ""
        posted_minutes = helpers.parse_posted_time(time_text)
        
        # Skip if no time info OR posted more than MAX_JOB_AGE_MINUTES
        if posted_minutes is None or posted_minutes > settings.MAX_JOB_AGE_MINUTES:
            continue
        # ------------------------------------

        # Extract location
        location_tag = job.find("span", class_="job-search-card__location")
        location = location_tag.text.strip() if location_tag else "N/A"

        # Initial fresher check based on title
        if not helpers.is_fresher_friendly(title):
            continue

        # Determine category
        category = helpers.detect_category(title)

        jobs.append({
            "title": title,
            "company": company,
            "link": link,
            "category": category,
            "posted_minutes": posted_minutes,
            "posted_text": time_text,
            "location": location,
            "applicants": "Loading...",  # Will be updated later
            "job_id": job_id,
            "timestamp": datetime.now().isoformat()
        })

    return jobs

def fetch_jobs_for_role(role):
    """Fetch jobs for a specific role across multiple pages."""
    found_jobs = []
    print(f"🔍 Searching for: {role}")
    
    for page in range(settings.MAX_PAGES):
        url = build_url(role, page * 25)
        try:
            response = requests.get(url, timeout=10)
            if len(response.text.strip()) == 0:
                break
            
            jobs = extract_jobs(response.text)
            found_jobs.extend(jobs)
            
            # Reduced sleep time for faster execution
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   Error fetching {role} page {page + 1}: {e}")
            continue
            
    return found_jobs

def search_jobs():
    """Search for jobs across multiple roles and pages using parallelism."""
    # Load existing jobs from last 24 hours
    jobs_history = manager.load_jobs_history()
    jobs_history = manager.clean_old_jobs(jobs_history)
    
    new_jobs_found = []
    print(f"\n{'='*60}")
    print(f"Starting job search at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Previously stored jobs: {len(jobs_history)}")
    print(f"{'='*60}")

    # Use ThreadPoolExecutor to fetch roles in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_role = {executor.submit(fetch_jobs_for_role, role): role for role in settings.ROLES}
        
        for future in concurrent.futures.as_completed(future_to_role):
            role = future_to_role[future]
            try:
                jobs = future.result()
                
                # Process found jobs
                for job in jobs:
                    job_id = job['job_id']
                    
                    # Add only if not already in history
                    if job_id not in jobs_history:
                        job['saved_at'] = datetime.now().isoformat()
                        jobs_history[job_id] = job
                        new_jobs_found.append(job)
                        
                        # Mark as seen in this session
                        seen_jobs.add(job_id)
                        
                print(f"✅ Finished {role}: Found {len(jobs)} candidates")
                
            except Exception as e:
                print(f"❌ Error processing role {role}: {e}")

    # Save updated history
    manager.save_jobs_history(jobs_history)
    
    print(f"\n✅ New jobs found: {len(new_jobs_found)}")
    print(f"📊 Total jobs in 24hr window: {len(jobs_history)}")
    
    return list(jobs_history.values())  # Return all jobs in history
