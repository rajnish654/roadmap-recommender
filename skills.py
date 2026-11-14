"""Skills, prerequisites, and career goals used by the roadmap planner."""

SKILLS = {
    # Each skill lists its learning time, prerequisites, track, and level.
    "html": {
        "name": "HTML",
        "hours": 20,
        "needs": [],
        "track": "frontend",
        "level": "beginner",
    },
    "css": {
        "name": "CSS",
        "hours": 25,
        "needs": ["html"],
        "track": "frontend",
        "level": "beginner",
    },
    "responsive": {
        "name": "Responsive Design",
        "hours": 15,
        "needs": ["css"],
        "track": "frontend",
        "level": "beginner",
    },
    "git": {
        "name": "Git & GitHub",
        "hours": 10,
        "needs": [],
        "track": "frontend",
        "level": "beginner",
    },
    "javascript": {
        "name": "JavaScript Fundamentals",
        "hours": 50,
        "needs": ["html"],
        "track": "frontend",
        "level": "beginner",
    },
    "dom": {
        "name": "DOM & Browser APIs",
        "hours": 20,
        "needs": ["javascript"],
        "track": "frontend",
        "level": "intermediate",
    },
    "typescript": {
        "name": "TypeScript",
        "hours": 30,
        "needs": ["javascript"],
        "track": "frontend",
        "level": "intermediate",
    },
    "react": {
        "name": "Frontend Framework (React)",
        "hours": 50,
        "needs": ["javascript", "dom"],
        "track": "frontend",
        "level": "intermediate",
    },
    "frontend_proj": {
        "name": "Frontend Project",
        "hours": 30,
        "needs": ["react", "responsive", "git"],
        "track": "frontend",
        "level": "intermediate",
    },
    "http": {
        "name": "HTTP & Web Basics",
        "hours": 10,
        "needs": [],
        "track": "backend",
        "level": "beginner",
    },
    "nodejs": {
        "name": "Node.js",
        "hours": 30,
        "needs": ["javascript"],
        "track": "backend",
        "level": "intermediate",
    },
    "rest": {
        "name": "REST API Design",
        "hours": 20,
        "needs": ["http", "nodejs"],
        "track": "backend",
        "level": "intermediate",
    },
    "sql": {
        "name": "Databases (SQL)",
        "hours": 30,
        "needs": [],
        "track": "backend",
        "level": "beginner",
    },
    "backend": {
        "name": "Backend Development (Express)",
        "hours": 40,
        "needs": ["rest", "sql"],
        "track": "backend",
        "level": "intermediate",
    },
    "auth": {
        "name": "Authentication & Security",
        "hours": 20,
        "needs": ["backend"],
        "track": "backend",
        "level": "advanced",
    },
    "deploy": {
        "name": "Deployment & Cloud Basics",
        "hours": 15,
        "needs": ["git", "backend"],
        "track": "backend",
        "level": "advanced",
    },
    "fullstack_proj": {
        "name": "Full-Stack Project",
        "hours": 60,
        "needs": ["frontend_proj", "backend", "auth", "deploy"],
        "track": "backend",
        "level": "advanced",
    },
    "python": {
        "name": "Python Basics",
        "hours": 40,
        "needs": [],
        "track": "core",
        "level": "beginner",
    },
    "dsa": {
        "name": "Data Structures & Algorithms",
        "hours": 80,
        "needs": ["python"],
        "track": "core",
        "level": "intermediate",
    },
    "python_backend": {
        "name": "Backend with Python (Flask)",
        "hours": 45,
        "needs": ["python", "sql", "rest"],
        "track": "core",
        "level": "intermediate",
    },
    "math_ai": {
        "name": "Math for AI",
        "hours": 40,
        "needs": [],
        "track": "ai",
        "level": "beginner",
    },
    "numpy_pandas": {
        "name": "NumPy & Pandas",
        "hours": 30,
        "needs": ["python"],
        "track": "ai",
        "level": "beginner",
    },
    "ml": {
        "name": "Machine Learning Basics",
        "hours": 70,
        "needs": ["python", "math_ai", "numpy_pandas"],
        "track": "ai",
        "level": "intermediate",
    },
    "deep_learning": {
        "name": "Deep Learning",
        "hours": 80,
        "needs": ["ml"],
        "track": "ai",
        "level": "advanced",
    },
    "ai_proj": {
        "name": "AI/ML Project",
        "hours": 50,
        "needs": ["ml", "git"],
        "track": "ai",
        "level": "advanced",
    },
    "networking": {
        "name": "Networking Basics",
        "hours": 30,
        "needs": [],
        "track": "security",
        "level": "beginner",
    },
    "linux": {
        "name": "Linux & Command Line",
        "hours": 25,
        "needs": [],
        "track": "security",
        "level": "beginner",
    },
    "sec_basics": {
        "name": "Security Fundamentals",
        "hours": 50,
        "needs": ["networking", "linux"],
        "track": "security",
        "level": "intermediate",
    },
    "py_scripting": {
        "name": "Python for Security Scripting",
        "hours": 25,
        "needs": ["python", "networking"],
        "track": "security",
        "level": "intermediate",
    },
    "web_security": {
        "name": "Web Application Security",
        "hours": 40,
        "needs": ["sec_basics", "http"],
        "track": "security",
        "level": "advanced",
    },
    "sec_proj": {
        "name": "Security Project (CTF / Lab)",
        "hours": 40,
        "needs": ["web_security", "py_scripting", "git"],
        "track": "security",
        "level": "advanced",
    },
}

# Required skills are needed for the goal. Optional skills are added when time allows.
GOALS = {
    "Full-Stack Developer": {
        "required": ["fullstack_proj"],
        "optional": ["typescript", "dsa"],
    },
    "Frontend Developer": {
        "required": ["frontend_proj"],
        "optional": ["typescript", "dsa"],
    },
    "Backend Developer": {
        "required": ["backend", "auth", "deploy"],
        "optional": ["python_backend", "dsa"],
    },
    "AI / ML Engineer": {
        "required": ["ml", "ai_proj"],
        "optional": ["deep_learning", "dsa"],
    },
    "Cybersecurity Analyst": {
        "required": ["web_security", "sec_proj"],
        "optional": ["dsa"],
    },
}

# The planner uses this order when choosing between ready-to-learn skills.
TRACK_ORDER = ["frontend", "backend", "core", "ai", "security"]

# These values adjust the estimated study hours for each experience level.
EXPERIENCE_FACTOR = {"beginner": 1.25, "intermediate": 1.0, "advanced": 0.8}
