import re
from backend.config import settings

def parse_posted_time(time_text):
    """Parse 'Posted X minutes ago' into minutes."""
    if not time_text:
        return None

    time_text = time_text.strip().lower()

    # Examples: "5 minutes ago", "1 hour ago", "2 days ago", "Just now"
    if "just now" in time_text or "reposted" in time_text or "seconds ago" in time_text:
        return 0

    # Match pattern like "X minutes/hours/days/weeks ago"
    match = re.search(r"(\d+)\s+(minute|hour|day|week|month)", time_text)
    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "minute":
        return value
    if unit == "hour":
        return value * 60
    if unit == "day":
        return value * 1440  # 24 * 60
    if unit == "week":
        return value * 10080 # 7 * 24 * 60
    if unit == "month":
        return value * 43200 # 30 * 24 * 60

    return None

def detect_category(title):
    title_lower = title.lower()
    for category, keywords in settings.CATEGORY_RULES.items():
        if any(k in title_lower for k in keywords):
            return category
    return "Others"

def is_fresher_friendly(title, description=""):
    """Check if job is suitable for freshers/recent graduates."""
    text = (title + " " + description).lower()
    
    # Must contain at least one fresher-friendly keyword
    has_fresher_keyword = any(keyword in text for keyword in settings.EXPERIENCE_FILTERS)
    
    # Must NOT contain exclusion keywords
    has_exclusion = any(keyword in text for keyword in settings.EXCLUDE_KEYWORDS)
    
    return has_fresher_keyword and not has_exclusion
