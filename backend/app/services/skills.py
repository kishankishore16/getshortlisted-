"""Skill normalization and taxonomy service.

Provides canonical skill name resolution and fuzzy matching to handle
the many variations people use when listing technical skills on resumes
and job descriptions.
"""

from difflib import SequenceMatcher

# Mapping of common skill name variations to their canonical form.
# Keys are lowercase variations; values are the canonical name.
SKILL_SYNONYMS: dict[str, str] = {
    # Programming Languages
    "js": "JavaScript",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c-sharp": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "rb": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "r": "R",
    "scala": "Scala",
    "perl": "Perl",
    "dart": "Dart",
    "lua": "Lua",
    "matlab": "MATLAB",
    "shell": "Shell Scripting",
    "bash": "Shell Scripting",
    "sh": "Shell Scripting",
    "powershell": "PowerShell",
    # Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "next": "Next.js",
    "nuxt": "Nuxt.js",
    "nuxtjs": "Nuxt.js",
    "svelte": "Svelte",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "sass": "SASS/SCSS",
    "scss": "SASS/SCSS",
    "less": "Less",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "jquery": "jQuery",
    "webpack": "Webpack",
    "vite": "Vite",
    # Backend
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    "ror": "Ruby on Rails",
    "laravel": "Laravel",
    "nestjs": "NestJS",
    "nest.js": "NestJS",
    "dotnet": ".NET",
    ".net": ".NET",
    "asp.net": "ASP.NET",
    # Databases
    "sql": "SQL",
    "mysql": "MySQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "pg": "PostgreSQL",
    "sqlite": "SQLite",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "es": "Elasticsearch",
    "dynamodb": "DynamoDB",
    "dynamo": "DynamoDB",
    "cassandra": "Cassandra",
    "neo4j": "Neo4j",
    "oracle": "Oracle DB",
    "mssql": "MS SQL Server",
    "sql server": "MS SQL Server",
    "mariadb": "MariaDB",
    "firebase": "Firebase",
    "firestore": "Firestore",
    "supabase": "Supabase",
    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "circleci": "CircleCI",
    "heroku": "Heroku",
    "vercel": "Vercel",
    "netlify": "Netlify",
    "nginx": "Nginx",
    "apache": "Apache",
    "linux": "Linux",
    "ubuntu": "Ubuntu",
    # AI/ML
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "keras": "Keras",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "matplotlib": "Matplotlib",
    "opencv": "OpenCV",
    "huggingface": "Hugging Face",
    "transformers": "Transformers",
    "llm": "Large Language Models",
    "langchain": "LangChain",
    "rag": "RAG",
    # Data
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "hadoop": "Hadoop",
    "kafka": "Apache Kafka",
    "apache kafka": "Apache Kafka",
    "airflow": "Apache Airflow",
    "apache airflow": "Apache Airflow",
    "tableau": "Tableau",
    "powerbi": "Power BI",
    "power bi": "Power BI",
    "looker": "Looker",
    "etl": "ETL",
    "data engineering": "Data Engineering",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    # Tools & Misc
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    "jira": "Jira",
    "confluence": "Confluence",
    "slack": "Slack",
    "figma": "Figma",
    "postman": "Postman",
    "swagger": "Swagger/OpenAPI",
    "openapi": "Swagger/OpenAPI",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "rest": "REST API",
    "rest api": "REST API",
    "restful": "REST API",
    "websocket": "WebSocket",
    "websockets": "WebSocket",
    "rabbitmq": "RabbitMQ",
    "celery": "Celery",
    "socket.io": "Socket.IO",
    # Testing
    "jest": "Jest",
    "mocha": "Mocha",
    "pytest": "pytest",
    "junit": "JUnit",
    "selenium": "Selenium",
    "cypress": "Cypress",
    "playwright": "Playwright",
    "unit testing": "Unit Testing",
    "tdd": "Test-Driven Development",
    # Mobile
    "react native": "React Native",
    "flutter": "Flutter",
    "android": "Android",
    "ios": "iOS",
    "swiftui": "SwiftUI",
    # Methodologies
    "agile": "Agile",
    "scrum": "Scrum",
    "kanban": "Kanban",
    "oop": "Object-Oriented Programming",
    "object oriented": "Object-Oriented Programming",
    "design patterns": "Design Patterns",
    "microservices": "Microservices",
    "system design": "System Design",
    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures & Algorithms",
}


def normalize_skill(skill: str) -> str:
    """Normalize a skill name to its canonical form.

    Looks up the lowercased skill string in the synonyms dictionary.
    If no match is found, returns the original string with title casing.

    Args:
        skill: The raw skill name string.

    Returns:
        The canonical skill name.
    """
    key = skill.strip().lower()
    if key in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[key]
    return skill.strip()


def fuzzy_match_skills(skill1: str, skill2: str) -> float:
    """Compute a fuzzy similarity score between two skill names.

    First attempts canonical normalization — if both normalize to the
    same string, returns 1.0. Otherwise uses SequenceMatcher on the
    lowercased strings for a 0-1 similarity score.

    Args:
        skill1: First skill name.
        skill2: Second skill name.

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    norm1 = normalize_skill(skill1).lower()
    norm2 = normalize_skill(skill2).lower()

    if norm1 == norm2:
        return 1.0

    return SequenceMatcher(None, norm1, norm2).ratio()
