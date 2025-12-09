import os

# ----------- CONFIG -------------
ROLES = [
    "software engineer intern",
    "software developer intern",
    "backend developer intern",
    "frontend developer intern",
    "full stack developer intern",
    "java developer intern",
    "nodejs developer intern",
    "react developer intern",
    "spring developer intern",
    "graduate engineer trainee",
    "entry level software engineer",
    "fresher software developer",
]

LOCATION = "India"
MAX_PAGES = 5

# Only show jobs posted within last X minutes (4.5 hours = 270 minutes)
MAX_JOB_AGE_MINUTES = 270

# Experience level filters
EXPERIENCE_FILTERS = [
    "intern",
    "fresher", 
    "junior",
    "entry level",
    "0-1 year",
    "0-2 year",
    "graduate",
]

# Keywords to exclude (jobs you can't apply to)
EXCLUDE_KEYWORDS = [
    "senior",
    "lead",
    "manager",
    "architect",
    "5+ years",
    "3+ years",
    "experienced",
    "principal",
]

# Blacklisted companies (known for fake jobs, unpaid work, or scams)
BLACKLISTED_COMPANIES = [
    "Trinet Technologies",
    "Techwave Solutions",
    "Unified Mentor",
    "Younity",
    "Codsoft",
    "Cognifyz Technologies",
    "Tripple One Solutions",
    "IMUN",
    "International Model United Nations",
    "Technohack",
    "Bharat Intern",
    "CodersCave",
    "CodeClause",
    "Oasis Infobyte",
    "LetsGrowMore",
    "UM IT Solutions",
    "Wake Up Whistle",
    "Uplers",
    "Right Hire Consulting Services",
]

# Categorization rules (Order matters: Specific -> Generic)
CATEGORY_RULES = {
    "Testing & QA": ["testing", "qa ", "quality assurance", "test engineer", "automation", "manual testing", "sdet"],
    "MERN Stack": ["mern"],
    "MEAN Stack": ["mean"],
    "Java Developer": ["java", "spring", "j2ee", "hibernate"],
    "Python Developer": ["python", "django", "flask", "fastapi", "pandas"],
    "Data Science & AI": ["data scientist", "data analyst", "machine learning", "ai ", "artificial intelligence", "nlp", "computer vision", "deep learning"],
    "DevOps & Cloud": ["devops", "aws", "azure", "cloud", "docker", "kubernetes", "jenkins", "ci/cd", "terraform"],
    "Mobile Developer": ["android", "ios", "flutter", "react native", "swift", "kotlin", "mobile app"],
    "UI/UX Design": ["ui/ux", "product design", "figma", "adobe xd", "user interface", "user experience"],
    "Frontend Developer": ["frontend", "react", "angular", "vue", "javascript", "typescript", "html", "css", "web designer", "web developer"],
    "Backend Developer": ["backend", "node", "php", "ruby", "golang", "c#", ".net", "sql", "database", "mysql", "postgresql", "mongodb"],
    "Full Stack": ["full stack", "fullstack"],
    "Intern / Fresher": ["intern", "fresher", "trainee", "graduate", "entry level", "apprentice"],
}

# Persistent storage paths
BASE_DIR = os.getcwd()
JOBS_STORAGE_FILE = os.path.join(BASE_DIR, "data", "jobs_history.json")
FRONTEND_DATA_FILE = os.path.join(BASE_DIR, "frontend", "jobs_data.js")

JOBS_RETENTION_HOURS = 5

SCHEDULE_INTERVAL_SECONDS = 20
