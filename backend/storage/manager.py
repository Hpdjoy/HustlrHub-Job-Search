import json
import os
from datetime import datetime, timedelta
from backend.config import settings

def load_jobs_history():
    """Load previously saved jobs from storage."""
    if not os.path.exists(settings.JOBS_STORAGE_FILE):
        return {}
    
    try:
        with open(settings.JOBS_STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading jobs history: {e}")
        return {}

def save_jobs_history(jobs_dict):
    """Save jobs to persistent storage and export to JS for frontend."""
    try:
        # Ensure directories exist
        os.makedirs(os.path.dirname(settings.JOBS_STORAGE_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(settings.FRONTEND_DATA_FILE), exist_ok=True)

        # Save JSON (Backend storage)
        with open(settings.JOBS_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(jobs_dict, f, ensure_ascii=False, indent=2)
            
        # Save JS (Frontend data source)
        # We wrap the JSON in a global variable assignment so index.html can read it locally
        js_content = f"window.JOB_DATA = {json.dumps(jobs_dict, ensure_ascii=False, indent=2)};"
        with open(settings.FRONTEND_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
            
        print(f"Saved {len(jobs_dict)} jobs to history and updated frontend data.")
    except Exception as e:
        print(f"Error saving jobs history: {e}")

def clean_old_jobs(jobs_dict):
    """Remove jobs older than JOBS_RETENTION_HOURS."""
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=settings.JOBS_RETENTION_HOURS)
    
    jobs_to_keep = {}
    removed_count = 0
    
    for job_id, job_data in jobs_dict.items():
        try:
            saved_time = datetime.fromisoformat(job_data['saved_at'])
            if saved_time > cutoff_time:
                jobs_to_keep[job_id] = job_data
            else:
                removed_count += 1
        except Exception:
            # Keep jobs with parsing errors
            jobs_to_keep[job_id] = job_data
    
    if removed_count > 0:
        print(f"🗑️  Removed {removed_count} old jobs (older than {settings.JOBS_RETENTION_HOURS} hours)")
    
    return jobs_to_keep
