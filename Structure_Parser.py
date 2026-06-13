"""
Module 2: Parser
This module takes raw text from the CV_Upload and turns it into data (important keywords) that the scorer can compare.
Two main functions: parse_cv(text) which extracts what the candidate has and parse_job(text) which extracts what the job needs
"""

import re



# keywords

PROGRAMMING_LANGUAGES = ["python", "java", "javascript", "c#", "c++", "r", "sql", "html", "css","php", "ruby", "swift", "kotlin", "typescript", "matlab", "vba", "latex","scala", "perl", "rust", "go", "golang", "lua", "haskell", "fortran","cobol", "assembly", "bash", "shell", "powershell", "objective-c","visual basic", "vb.net", "groovy", "dart", "julia", "sas", "stata","nosql", "plsql", "t-sql", "xml", "json", "yaml", "graphql","solidity", "elixir", "clojure", "lisp", "prolog"]

CS_SKILLS = ["software development", "software engineering", "web development","frontend", "front-end", "backend", "back-end", "full stack", "fullstack","mobile development", "app development", "api", "rest api", "microservices","object oriented", "oop", "functional programming", "devops", "ci/cd","test driven", "tdd", "unit testing", "integration testing", "debugging","data analysis", "data science", "data engineering", "data mining","machine learning", "deep learning", "artificial intelligence","neural networks", "natural language processing", "nlp","computer vision", "reinforcement learning", "big data","data visualization", "data warehouse", "etl", "data pipeline","predictive modeling", "feature engineering", "a/b testing","database", "mysql", "postgresql", "mongodb", "oracle", "sql server","redis", "elasticsearch", "cassandra", "dynamodb", "sqlite", "mariadb","firebase", "neo4j", "snowflake", "databricks","aws", "amazon web services", "azure", "google cloud", "gcp","cloud computing", "serverless", "lambda", "kubernetes", "docker","terraform", "ansible", "jenkins", "linux", "unix", "windows server","networking", "tcp/ip", "dns", "load balancing", "cdn","cybersecurity", "information security", "penetration testing","encryption", "firewall", "vulnerability assessment", "soc","incident response", "compliance", "gdpr", "iso 27001","excel", "word", "powerpoint", "microsoft office", "ms office","google sheets", "google docs", "google slides", "libreoffice","figma", "sketch", "adobe", "photoshop", "illustrator","wordpress", "shopify", "salesforce", "sap", "erp", "crm","git", "github", "gitlab", "bitbucket", "jira", "confluence","slack", "trello", "asana", "notion","react", "angular", "vue", "node.js", "django", "flask", "spring","express", ".net", "laravel", "rails", "bootstrap", "tailwind","tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "scipy","matplotlib", "seaborn", "plotly", "spark", "hadoop", "kafka","airflow", "dbt", "power bi", "tableau", "looker", "qlik","agile", "scrum", "kanban", "waterfall", "lean","project management", "product management"]

FINANCE_SKILLS = ["financial analysis", "financial modeling", "financial reporting","financial statements", "financial planning", "budgeting", "forecasting","accounting", "bookkeeping", "auditing", "tax", "taxation","gaap", "ifrs", "consolidation", "reconciliation","accounts payable", "accounts receivable", "general ledger","cost accounting", "management accounting", "controlling","investment banking", "corporate finance", "private equity","venture capital", "hedge fund", "asset management","portfolio management", "wealth management", "fund management","investment management", "fund accounting", "fund administration","mergers and acquisitions", "m&a", "ipo", "due diligence","leveraged buyout", "lbo", "dcf", "discounted cash flow","valuation", "equity research", "fixed income", "derivatives","options", "futures", "bonds", "equities", "commodities","foreign exchange", "forex", "fx", "treasury","capital markets", "debt capital markets", "equity capital markets","structured finance", "securitization", "syndication","risk management", "credit risk", "market risk", "operational risk","liquidity risk", "counterparty risk", "var", "value at risk","stress testing", "basel", "compliance", "regulatory","aml", "anti-money laundering", "kyc", "know your customer","sanctions", "fraud detection", "internal controls", "sox","trading", "algorithmic trading", "quantitative trading","market making", "execution", "order management","bloomberg", "reuters", "eikon", "factset", "morningstar","pitchbook", "capital iq", "preqin","fintech", "blockchain", "cryptocurrency", "defi","payments", "digital banking", "open banking", "regtech","insurance", "underwriting", "claims", "actuarial", "reinsurance","life insurance", "property insurance", "casualty","quantitative analysis", "quantitative finance", "stochastic","monte carlo", "time series", "econometrics", "regression","real estate", "property valuation", "reit","commercial real estate", "residential real estate","esg", "sustainable finance", "impact investing","responsible investing", "sri", "carbon footprint","sustainability reporting", "gri", "tcfd","nav", "net asset value", "performance attribution","benchmark", "sharpe ratio", "alpha", "beta","investor relations", "client reporting", "factsheet","operations", "settlement", "clearing", "custody","back office", "middle office", "front office"]

MATH_SKILLS = ["mathematics", "statistics", "probability", "calculus","linear algebra", "differential equations", "numerical methods","optimization", "operations research", "discrete mathematics","combinatorics", "graph theory", "number theory", "topology","statistical modeling", "bayesian", "frequentist","hypothesis testing", "confidence interval", "p-value","regression analysis", "logistic regression", "anova","multivariate analysis", "principal component analysis", "pca","clustering", "classification", "random forest", "gradient boosting","cross validation", "bootstrapping", "resampling","time series analysis", "arima", "garch", "fourier analysis","stochastic processes", "markov chain", "game theory","simulation", "monte carlo simulation", "numerical analysis","mathematical modeling", "applied mathematics"]

PHYSICS_SKILLS = ["physics", "quantum mechanics", "thermodynamics", "electromagnetism","classical mechanics", "optics", "nuclear physics", "particle physics","solid state physics", "condensed matter", "astrophysics", "cosmology","fluid dynamics", "computational physics", "experimental physics","spectroscopy", "microscopy", "laser", "photonics", "semiconductors","nanotechnology", "materials science", "plasma physics","mechanical engineering", "electrical engineering", "civil engineering","chemical engineering", "biomedical engineering", "aerospace engineering","robotics", "automation", "control systems", "signal processing","cad", "autocad", "solidworks", "ansys", "simulink", "labview","3d printing", "additive manufacturing", "pcb design","quality assurance", "quality control", "six sigma","manufacturing", "supply chain", "logistics", "lean manufacturing","iso 9001", "gmp", "fmea"]

MEDICINE_SKILLS = ["medicine", "clinical research", "clinical trials", "clinical practice","patient care", "diagnosis", "treatment", "surgery", "anesthesia","emergency medicine", "intensive care", "primary care","internal medicine", "pediatrics", "geriatrics", "oncology","cardiology", "neurology", "dermatology", "orthopedics","psychiatry", "radiology", "pathology", "immunology","gastroenterology", "endocrinology", "nephrology", "pulmonology","ophthalmology", "urology", "obstetrics", "gynecology","pharmacology", "pharmacy", "drug development", "drug discovery","clinical pharmacology", "pharmaceutical", "gcp", "fda","regulatory affairs", "pharmacovigilance", "drug safety","biotechnology", "genomics", "proteomics", "bioinformatics","molecular biology", "cell biology", "microbiology", "virology","genetics", "gene therapy", "crispr", "pcr", "sequencing","laboratory", "lab techniques", "in vitro", "in vivo","biostatistics", "epidemiology", "public health","healthcare", "hospital", "nursing", "physiotherapy","occupational therapy", "medical devices", "medical imaging","electronic health records", "ehr", "telemedicine", "telehealth","health informatics", "hipaa"]

LAW_SKILLS = ["law", "legal", "litigation", "arbitration", "mediation","corporate law", "contract law", "commercial law", "employment law","intellectual property", "patent", "trademark", "copyright","data protection", "privacy law", "gdpr", "regulatory law","tax law", "banking law", "securities law", "competition law","antitrust", "real estate law", "environmental law","criminal law", "constitutional law", "international law","mergers acquisitions", "legal research", "legal writing","due diligence", "compliance", "governance", "paralegal","notary", "legal counsel", "in-house counsel"]

MARKETING_SKILLS = ["marketing", "digital marketing", "content marketing", "seo","sem", "social media marketing", "email marketing", "ppc","google ads", "facebook ads", "instagram", "linkedin marketing","marketing automation", "hubspot", "mailchimp", "marketo","brand management", "branding", "market research", "market analysis","customer segmentation", "target audience", "buyer persona","public relations", "pr", "copywriting", "content creation","content strategy", "storytelling", "blogging", "journalism","graphic design", "video production", "photography","influencer marketing", "affiliate marketing", "growth hacking","conversion optimization", "cro", "funnel", "lead generation","sales", "business development", "account management","key account", "client relationship", "customer success","crm", "pipeline management", "cold calling", "prospecting","b2b", "b2c", "e-commerce", "retail", "merchandising"]

CONSULTING_SKILLS = ["consulting", "management consulting", "strategy consulting","strategy", "strategic planning", "business strategy","business analysis", "process improvement", "process optimization","change management", "transformation", "restructuring","stakeholder management", "client management", "engagement management","market entry", "growth strategy", "competitive analysis","swot analysis", "porter", "pestel", "benchmarking","kpi", "okr", "balanced scorecard", "dashboard","business plan", "business case", "feasibility study","operations management", "procurement","supply chain management", "inventory management","human resources", "hr", "talent acquisition", "recruitment","performance management", "compensation", "benefits","organizational development", "training", "coaching", "mentoring"]

LANGUAGES = ["english", "french", "german", "spanish", "italian", "portuguese","chinese", "mandarin", "cantonese", "japanese", "korean","arabic", "russian", "dutch", "swedish", "norwegian", "danish","finnish", "polish", "turkish", "hindi", "bengali", "urdu","czech", "greek", "hungarian", "romanian", "thai", "vietnamese","indonesian", "malay", "tagalog", "hebrew", "persian", "farsi","ukrainian", "serbian", "croatian", "bulgarian", "slovak","slovenian", "estonian", "latvian", "lithuanian", "swahili","afrikaans", "catalan", "basque", "galician", "welsh", "irish"]

SOFT_SKILLS = ["communication", "presentation", "public speaking", "negotiation","written communication", "verbal communication", "storytelling","active listening", "facilitation", "conflict resolution","leadership", "team management", "people management", "mentoring","coaching", "delegation", "decision making", "strategic thinking","vision", "motivation", "empowerment", "accountability","teamwork", "collaboration", "cross-functional", "interpersonal","relationship building", "networking", "cultural awareness","diversity", "inclusion","problem solving", "critical thinking", "analytical","creative thinking", "innovation", "research", "troubleshooting","root cause analysis", "lateral thinking","time management", "organized", "planning", "prioritization","multitasking", "attention to detail", "detail oriented","deadline management", "self management","adaptable", "flexible", "resilient", "stress management","agility", "continuous learning", "growth mindset","open minded", "proactive", "self motivated","reliable", "dependable", "punctual", "professional","integrity", "ethical", "confidential", "discretion","customer oriented", "service oriented", "quality focused","results oriented", "goal oriented", "entrepreneurial"]

EDUCATION_LEVELS = ["bachelor", "master", "mba", "phd", "doctorate", "postdoc","bsc", "msc", "llb", "llm", "md", "bba","diploma", "certificate", "degree", "postgraduate","undergraduate", "graduate", "doctoral","cfa", "cpa", "acca", "frm", "caia", "cfp","pmp", "prince2", "itil", "aws certified", "cisco certified"]

ALL_TECHNICAL = (PROGRAMMING_LANGUAGES + CS_SKILLS + FINANCE_SKILLS +MATH_SKILLS + PHYSICS_SKILLS + MEDICINE_SKILLS +LAW_SKILLS + MARKETING_SKILLS + CONSULTING_SKILLS)

# Groups of terms that mean the same thing. When any variant is found, all are treated as a match.

SYNONYMS = {
    "microsoft office":     ["ms office", "microsoft office", "office suite", "ms-office"],
    "excel":                ["excel", "microsoft excel", "ms excel"],
    "powerpoint":           ["powerpoint", "microsoft powerpoint", "ms powerpoint", "ppt"],
    "word":                 ["word", "microsoft word", "ms word"],
    "python":               ["python", "python3", "python 3"],
    "javascript":           ["javascript", "js", "ecmascript"],
    "c++":                 ["c++", "cpp"],
    "machine learning":     ["machine learning", "ml"],
    "artificial intelligence": ["artificial intelligence", "ai"],
    "natural language processing": ["natural language processing", "nlp"],
    "data science":         ["data science", "data scientist"],
    "project management":   ["project management", "project manager", "pm"],
    "private equity":       ["private equity", "pe"],
    "venture capital":      ["venture capital", "vc"],
    "mergers and acquisitions": ["mergers and acquisitions", "m&a", "mergers & acquisitions"],
    "amazon web services":  ["amazon web services", "aws"],
    "google cloud":         ["google cloud", "gcp", "google cloud platform"],
    "continuous integration": ["continuous integration", "ci/cd", "ci cd"],
    "bachelor":             ["bachelor", "bachelors", "bachelor's"],
    "master":               ["master", "masters", "master's"],
    "teamwork":             ["teamwork", "team work", "team player"],
    "problem solving":      ["problem solving", "problem-solving"],
    "attention to detail":  ["attention to detail", "detail oriented", "detail-oriented", "eye for detail"],
    "communication":        ["communication", "communication skills"],
    "leadership":           ["leadership", "leader", "leading teams"],
    "financial modeling":   ["financial modeling", "financial modelling"],
    "accounting":           ["accounting", "accountancy"],
    "customer relationship management": ["customer relationship management", "crm"],
    "enterprise resource planning": ["enterprise resource planning", "erp"],
    "business intelligence": ["business intelligence", "bi"],
    "human resources":      ["human resources", "hr"],
    "search engine optimization": ["search engine optimization", "seo"],
    "return on investment":  ["return on investment", "roi"],
    "key performance indicator": ["key performance indicator", "kpi", "kpis"],}

# These detect skills from context even when the exact keyword doesn't appear. Each pattern maps a regex to a skill.

CONTEXTUAL_PATTERNS = {
    "leadership": [
        r"led\s+(a\s+)?\d+[\s-]person",                                 # "led a 6-person team"
        r"led\s+(a\s+)?team",                                           # "led a team"
        r"managed\s+(a\s+)?team",                                       # "managed a team"
        r"head(ed)?\s+of",                                              # "head of department"
        r"supervised\s+\d+",                                            # "supervised 10 employees"
        r"directed\s+(a\s+)?(team|group|department)",                   # "directed a group"
        r"lead(ing)?\s+(a\s+)?(team|group|project)",                    # "leading a project"
        r"in charge of",                                                # "in charge of operations"
        r"reporting\s+to\s+(the\s+)?(ceo|cfo|cto|director|vp|board)",   # "reporting to the CEO"
    ],
    "project management": [
        r"managed\s+(a\s+)?project",                                    # "managed a project"
        r"coordinated\s+(a\s+)?(project|initiative|program)",           # "coordinated a program"
        r"oversaw\s+(the\s+)?(development|implementation|launch)",      # "oversaw the development"
        r"delivered\s+(a\s+)?(project|product|solution)",               # "delivered a solution"
        r"spearheaded",                                                 # "spearheaded the initiative"
    ],
    "teamwork": [
        r"worked\s+(closely\s+)?with\s+(a\s+)?team",                    # "worked closely with a team"
        r"collaborated\s+with",                                         # "collaborated with stakeholders"
        r"cross-functional\s+(team|collaboration)",                     # "cross-functional team"
        r"worked\s+in\s+(a\s+)?rotation\s+with",                        # "worked in a rotation with"
        r"team\s+of\s+\d+",                                             # "team of 5"
        r"partnered\s+with",                                            # "partnered with engineering"
    ],
    "communication": [
        r"present(ed|ing)\s+(to|at|findings|results|recommendations)",  # "presented findings to"
        r"(wrote|drafted|authored)\s+(reports|proposals|documents)",    # "wrote reports"
        r"client[\s-]facing",                                           # "client-facing role"
        r"stakeholder\s+(engagement|communication|management)",         # "stakeholder engagement"
        r"liaised\s+with",                                              # "liaised with partners"
    ],
    "analytical": [
        r"analy[sz](ed|ing)\s+(data|financial|reports|performance)",    # "analyzed data"
        r"conducted\s+(analysis|research|review|assessment)",           # "conducted analysis"
        r"data[\s-]driven",                                             # "data-driven decisions"
        r"evaluated\s+(performance|results|outcomes|risk)",             # "evaluated performance"
        r"identified\s+(trends|patterns|opportunities|issues)",         # "identified trends"
    ],
    "organized": [
        r"organis(ed|ing)\s+(events?|meetings?|workshops?|camps?)",     # "organised events"
        r"organiz(ed|ing)\s+(events?|meetings?|workshops?|camps?)",     # "organized events" (US spelling)
        r"planned\s+(and\s+executed\s+)?(events?|projects?|campaigns?)",# "planned and executed events"
        r"scheduled\s+(meetings?|appointments?|activities)",            # "scheduled meetings"
        r"coordinated\s+(logistics|events|schedules|activities)",       # "coordinated logistics"
    ],
    "problem solving": [
        r"troubleshoot(ed|ing)?",                                       # "troubleshooting issues"
        r"resolved\s+(issues?|problems?|conflicts?|bugs?)",             # "resolved issues"
        r"debug(ged|ging)?",                                            # "debugging code"
        r"improved\s+(performance|efficiency|processes?|workflow)",     # "improved efficiency"
        r"optimiz(ed|ing)\s+(performance|processes?|operations?)",      # "optimized processes"
    ],
    "innovation": [
        r"built\s+(a\s+)?(website|app|tool|system|platform|solution)",  # "built a website"
        r"developed\s+(a\s+)?(new|novel|innovative|custom)",            # "developed a new approach"
        r"created\s+(a\s+)?(new|novel|innovative|custom)",              # "created a new tool"
        r"designed\s+(and\s+implemented\s+)?(a\s+)?(system|solution|framework)", # "designed a system"
        r"implemented\s+(a\s+)?(new|novel|innovative)?",                # "implemented a new process"
    ],
    "mentoring": [
        r"mentor(ed|ing)\s+",                                           # "mentored interns"
        r"coach(ed|ing)\s+",                                            # "coached players"
        r"train(ed|ing)\s+(new\s+)?(employees?|staff|team|members?)",   # "trained new employees"
        r"taught\s+",                                                   # "taught programming"
        r"supervised\s+(interns?|juniors?|students?|trainees?)",        # "supervised interns"
    ],
    "customer oriented": [
        r"client\s+(relationship|interaction|service|inquir)",          # "client inquiries"
        r"customer\s+(service|support|satisfaction|experience)",        # "customer service"
        r"processed\s+(client|customer)\s+(requests?|inquir)",          # "processed client requests"
        r"responded\s+to\s+(client|customer)",                          # "responded to client needs"
    ],
    "research": [
        r"research(ed|ing)?\s+(and\s+)?(analy|develop|report|public)",  # "researched and analyzed"
        r"conducted\s+research",                                        # "conducted research"
        r"published\s+(papers?|articles?|findings)",                    # "published papers"
        r"peer[\s-]review(ed)?",                                        # "peer-reviewed"
        r"literature\s+review",                                         # "literature review"
        ],}

PROFICIENCY_LEVELS = {"a1": "beginner","a2": "elementary","b1": "intermediate","b2": "upper intermediate","c1": "advanced","c2": "proficient","native": "native","mother tongue": "native","native speaker": "native","fluent": "proficient","proficient": "proficient","full working proficiency": "proficient","professional working proficiency": "advanced","advanced": "advanced","intermediate": "intermediate","upper intermediate": "upper intermediate","limited working proficiency": "intermediate","basic": "elementary","beginner": "beginner","elementary": "elementary","conversational": "intermediate","business level": "advanced","bilingual": "native",}

PROFICIENCY_RANK = {"beginner": 1,"elementary": 2,"intermediate": 3,"upper intermediate": 4,"advanced": 5,"proficient": 6,"native": 7,}

# ===========================================================
# End definition and start of the function
# Please note that we understand that it can be improved but this is going to be regarded as a possible future imporvement
# ===========================================================




# functions

def extract_language_proficiency(text):
    """
    Extracts languages along with their proficiency levels.
    Returns a dict like: {"english": {"level": "proficient", "rank": 6}, ...}
    """
    # transform all the text in lowercase and define a list to store it
    text_lower = text.lower()                                                               # put everything in lower case to avoid consistency issue
    results = {}                                                                            # store the result
    # go through a loop of previously define language and make sure that we only take into consideration the language (full word)
    for language in LANGUAGES:                                          
        pattern = r'\b' + re.escape(language) + r'\b'
        if not re.search(pattern, text_lower):
            continue
    # found the language - now look for proficiency nearby
    # check both before and after the language mention
        match = re.search(pattern, text_lower)
        if match:
            # text before the language (up to previous delimiter)
            before_text = text_lower[max(0, match.start() - 60):match.start()]
            for delimiter in [",", ";", "\n"]:
                if delimiter in before_text:
                    before_text = before_text[before_text.rindex(delimiter) + 1:]

            # text after the language (up to next delimiter)
            after_text = text_lower[match.end():match.end() + 80]
            for delimiter in [",", ";", "\n"]:
                if delimiter in after_text:
                    after_text = after_text[:after_text.index(delimiter)]

            surrounding = before_text + " " + after_text
            # find proficency level
            best_level = None
            best_rank = 0
            # loops through all the level of proficiency
            for level_text, level_name in PROFICIENCY_LEVELS.items():
                if level_text in surrounding:
                    rank = PROFICIENCY_RANK.get(level_name, 0)
                    if rank > best_rank:
                        best_rank = rank
                        best_level = level_name
            # return the level except if cannot find one return 0
            if best_level:
                results[language] = {"level": best_level, "rank": best_rank}
            else:
                results[language] = {"level": "mentioned", "rank": 0}

    return results

# define the number of year of experience

def extract_experience_requirements(text):
    """
    Extracts years of experience mentioned in text. Returns 
    """
    text_lower = text.lower()
    results = []

    # Patterns for experience requirements
    patterns = [
        r'(\d+)\+?\s*years?\s*(of\s+)?(experience|expertise|work)',     # "3+ years of experience"
        r'(\d+)\+?\s*years?\s*in\s+[\w\s]+',                            # "3 years in finance"
        r'minimum\s+(\d+)\s*years?',                                    # "minimum 3 years"
        r'at\s+least\s+(\d+)\s*years?',                                 # "at least 2 years"
        r'(\d+)\s*-\s*(\d+)\s*years?\s*(of\s+)?(experience|work)',      # "2-3 years of experience"
    ]
    # loops through the pattern to identify potential experience formulation
    for pattern in patterns:
        for match in re.finditer(pattern, text_lower):
            full_match = match.group(0)
            years = int(match.group(1))
            # Avoid matching unrealistic numbers (like years in dates)
            if 0 < years <= 30:
                results.append({
                    "years": years,
                    "context": full_match.strip()
                })

    return results



# Detectino of important words
# Sections where keywords matter most (for the job offer)

REQUIRED_SECTIONS = ["requirements", "qualifications", "required qualifications","minimum qualifications", "what we are looking for","your profile", "what you bring", "must have"]

PREFERRED_SECTIONS = ["preferred qualifications", "nice to have", "bonus skills","desired skills", "advantageous", "plus"]

RESPONSIBILITY_SECTIONS = ["responsibilities", "key responsibilities", "duties","your tasks", "your role", "what you will do","job description", "role description"]

# split the CV into different part
def detect_sections(text):
    """
    Splits text into sections based on common headers.
    Returns dict with section names as keys and text content as values.
    """
    section_headers = ["education", "work experience", "experience", "employment","professional experience", "career history","skills", "technical skills", "core competencies", "competencies", "additional information", "personal information","languages", "certifications", "certificates","projects", "publications", "awards", "honors","extra-curricular", "extracurricular", "activities","volunteering", "volunteer experience", "community involvement","interests", "hobbies", "references","professional summary", "summary", "profile", "objective","requirements", "qualifications", "required qualifications","preferred qualifications", "minimum qualifications","responsibilities", "key responsibilities", "duties","what we offer", "benefits", "perks", "compensation","about us", "about the company", "company overview","job description", "role description", "position overview","your profile", "your tasks", "your role","what you bring", "what we are looking for","nice to have", "bonus skills", "desired skills","how to apply", "application process"]
    # the code split each part into by its line
    lines = text.split("\n")
    sections = {}
    current_section = "header"
    current_content = []
    # remove spacing and put everything in lower case (cleaning)
    for line in lines:
        line_lower = line.strip().lower()
        # check if the line is a header and save the following in a content so we have (title - text for each entry)
        is_header = False
        for header in section_headers:
            if line_lower == header or line_lower.startswith(header + ":") or line_lower.startswith(header + " -"):
                is_header = True
                # save the text before starting a new section
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                # start the new section
                current_section = header
                current_content = []
                break
        # if not a header it adds the line to the content of the section
        if not is_header:
            current_content.append(line)
    # save the last section
    if current_content:
        sections[current_section] = "\n".join(current_content)

    return sections


def tag_keyword_importance(keyword, sections):
    """
    Tags a keyword with its importance based on which section it appears in and returns a single keyword that are important
    """
    # clean the keyword and use the structure to match the keyword as a full structure
    for section_name, section_text in sections.items():
        text_lower = section_text.lower()
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        # check for the keyword in the text and put it in one of the other class (either required, preferred or responsiblity (depending  on the job offer))
        if re.search(pattern, text_lower):
            if section_name in REQUIRED_SECTIONS:
                return "required"
            elif section_name in PREFERRED_SECTIONS:
                return "preferred"
            elif section_name in RESPONSIBILITY_SECTIONS:
                return "responsibility"
    # if keyword in none of the part above then it only return
    return "general"          

# Retrun a list of the key words

def find_keywords(text, keyword_list):
    """
    Searches text for keywords using word boundary matching and returns list of found keywords.
    """
    # cleaning the text
    text_lower = text.lower()
    found = []
    # goes through all the keyword in the list and identify it using the pattern of the unique word and addit is to a new list
    for keyword in keyword_list:
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(keyword.lower()) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, text_lower):
            if keyword not in found:
                found.append(keyword)
    return found


def find_contextual_skills(text):
    """
    Detects skills from context using patterns and returns list of skills from the text.
    """
    text_lower = text.lower()
    found = []
    # locate the skills be using the pattern define above
    for skill, patterns in CONTEXTUAL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                # we only check for each skill once
                if skill not in found:
                    found.append(skill)
                break                                                   # one match is enough for this skill

    return found


def resolve_synonyms(keywords):
    """
    Groups synonyms together so that "MS Office" and "Microsoft Office"are treated as the same skill and the function will return the variants found.
    """
    resolved = {}
    # loops over the synomyms and check for the different variant 
    for canonical, variants in SYNONYMS.items():
        found_variants = []
        for keyword in keywords:
            # deal with difference in term of high/lowcase
            if keyword.lower() in [v.lower() for v in variants]:
                found_variants.append(keyword)
        if found_variants:
            resolved[canonical] = found_variants

    # Also include keywords that aren't in any synonym group
    all_synonym_variants = []
    # the list of all the synoyme for all the synoyme group
    for variants in SYNONYMS.values():
        all_synonym_variants.extend([v.lower() for v in variants])
    # deal with the word that are not linked to a list of synoym and add them to resolve at the end (avoid losing them  them)
    for keyword in keywords:
        if keyword.lower() not in all_synonym_variants:
            resolved[keyword] = [keyword]

    return resolved




# Combining function for parser return

def parse_cv(text):
    """
    Takes the CV text and extracts all the important keywords (skills, languages, education, sections).
    Returns a dict with all the structured data ready to be compared by the scorer.
    """
    # split the CV into section 
    sections = detect_sections(text)
    # Keyword matching where we scan through CV to identify category of words
    programming = find_keywords(text, PROGRAMMING_LANGUAGES)
    technical = find_keywords(text, ALL_TECHNICAL)
    soft = find_keywords(text, SOFT_SKILLS)
    languages = extract_language_proficiency(text)
    education = find_keywords(text, EDUCATION_LEVELS)
    finance = find_keywords(text, FINANCE_SKILLS)
    # find the skills that weren't written as keywords (using pattern and sentence construction)
    contextual = find_contextual_skills(text)
    # Merge contextual soft skills with keyword soft skills
    for skill in contextual:
        if skill in [s.lower() for s in SOFT_SKILLS] and skill not in soft:
            soft.append(skill)
    # Resolve grouping of synonyms for technical skills 
    technical_resolved = resolve_synonyms(technical)
    # grouping and return
    result = {"programming": programming,"technical_skills": technical,"technical_resolved": technical_resolved,  "soft_skills": soft,"contextual_skills": contextual,"languages": languages,"education": education,"finance": finance,"sections": sections,"full_text": text}
    return result





def parse_job(text):
    """
    Parses job offer text and extracts requirements.
    """
    # define the different part of the CV
    sections = detect_sections(text)
    # Match the different important concept of the CV
    programming = find_keywords(text, PROGRAMMING_LANGUAGES)
    technical = find_keywords(text, ALL_TECHNICAL)
    soft = find_keywords(text, SOFT_SKILLS)
    languages = extract_language_proficiency(text)
    education = find_keywords(text, EDUCATION_LEVELS)
    finance = find_keywords(text, FINANCE_SKILLS)
    # contextual skill detection and sentence pattern
    contextual = find_contextual_skills(text)
    for skill in contextual:
        if skill in [s.lower() for s in SOFT_SKILLS] and skill not in soft:
            soft.append(skill)
    # identify synonyms
    technical_resolved = resolve_synonyms(technical)
    # define importance (required, prefeered, responsibility) of each technical skill present in the job description 
    importance = {}
    for keyword in technical:
        importance[keyword] = tag_keyword_importance(keyword, sections)
    # same but for importance of each soft skill
    for keyword in soft:
        importance[keyword] = tag_keyword_importance(keyword, sections)
    # make sure it fits the experience requirements from the job description (2+ year of experience)
    experience = extract_experience_requirements(text)
    # grouping and return
    result = {"programming": programming,"technical_skills": technical,"technical_resolved": technical_resolved,"soft_skills": soft,"contextual_skills": contextual,"languages": languages,"education": education,"finance": finance,"importance": importance,"experience_required": experience,"sections": sections,"full_text": text}
    return result


