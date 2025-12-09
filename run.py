import schedule
import time
from datetime import datetime
from backend.scraper import linkedin
from backend.config import settings

def job():
    """Scheduled job wrapper."""
    print(f"\nRunning scheduled job at {datetime.now().strftime('%H:%M:%S')}")
    try:
        linkedin.search_jobs()
    except Exception as e:
        print(f"Error in scheduled job: {e}")

if __name__ == "__main__":
    print(f"Job Search Bot Started.")
    print(f"Schedule interval: {settings.SCHEDULE_INTERVAL_SECONDS} seconds")
    print("Press Ctrl+C to stop.")
    
    # Run immediately on startup
    job()
    
    # Schedule subsequent runs
    schedule.every(settings.SCHEDULE_INTERVAL_SECONDS).seconds.do(job)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nBot stopped by user.")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            time.sleep(5)
