"""
Module 4: Scorer

This module takes the structured data produced by Structure_Parser.py
and computes a match score between a candidate's CV and a job offer.

One main function: compute_score(cv_data, job_data) which compares the
two parsed documents across four categories (technical skills, programming
languages, soft skills, and spoken languages) and returns an overall score
out of 100 plus a full per-category breakdown.
"""

# ============================================================
# Scoring Weights
# These control how much each category contributes to the
# overall score. Technical skills and programming languages
# are weighted most heavily as they are typically the hardest
# requirements to substitute in a job offer.
# Adjust these values if you want to reprioritise categories.
# ============================================================

WEIGHTS = {
    "tech": 0.45,   # technical skills  — largest share
    "prog": 0.25,   # programming languages
    "soft": 0.20,   # soft skills
    "lang": 0.10,   # spoken languages  — smallest share
}

# Maximum bonus score (as a fraction) awarded for covering
# skills that the job explicitly marked as "required".
# 0.10 means up to +10 points on top of the weighted score.
REQUIRED_SKILLS_BOOST = 0.10


# ============================================================
# Helper Functions
# ============================================================

def overlap(cv_list, job_list):
    """
    Computes the overlap between two keyword lists.
    Comparison is case-insensitive so "Python" and "python" match.

    Parameters:
        cv_list  — list of keywords extracted from the CV
        job_list — list of keywords extracted from the job offer

    Returns a tuple of:
        matched — sorted list of keywords present in both
        missing — sorted list of keywords in the job but not the CV
        ratio   — fraction of job keywords covered (0.0 to 1.0)
    """
    cv_set  = {k.lower() for k in cv_list}
    job_set = {k.lower() for k in job_list}

    # if the job doesn't mention any keywords in this category,
    # treat it as a full match so it doesn't penalise the overall score
    if not job_set:
        return [], [], 1.0

    matched = sorted(cv_set & job_set)          # intersection: in both
    missing = sorted(job_set - cv_set)          # difference: in job only
    ratio   = len(matched) / len(job_set)       # coverage fraction

    return matched, missing, ratio


# ============================================================
# Main Scoring Function
# ============================================================

def compute_score(cv_data: dict, job_data: dict) -> dict:
    """
    Computes a match score between a candidate's CV and a job offer.

    Takes the structured dictionaries produced by parse_cv() and parse_job()
    from Structure_Parser.py and returns an overall score from 0 to 100,
    along with a full breakdown by category so the UI can display details.

    Scoring method:
        1. Compute keyword overlap ratio for each of the four categories
        2. Combine them into a weighted average using WEIGHTS above
        3. Add a small bonus (up to REQUIRED_SKILLS_BOOST) if the candidate
           covers skills the job explicitly marked as required
        4. Cap the result at 100 and round to a whole number

    Parameters:
        cv_data  — output dict from Structure_Parser.parse_cv()
        job_data — output dict from Structure_Parser.parse_job()

    Returns: dict with the following keys:
        overall         — final score as an integer from 0 to 100
        tech            — dict with matched, missing, ratio for technical skills
        prog            — dict with matched, missing, ratio for programming languages
        soft            — dict with matched, missing, ratio for soft skills
        lang            — dict with matched, missing, ratio for spoken languages
        required_found  — list of required skills the candidate has
        required_total  — list of all required skills in the job offer
    """

    # ── Category overlap ──────────────────────────────────
    # run keyword overlap for each of the four skill categories
    tech_matched, tech_missing, tech_ratio = overlap(
        cv_data["technical_skills"], job_data["technical_skills"]
    )
    prog_matched, prog_missing, prog_ratio = overlap(
        cv_data["programming"], job_data["programming"]
    )
    soft_matched, soft_missing, soft_ratio = overlap(
        cv_data["soft_skills"], job_data["soft_skills"]
    )
    lang_matched, lang_missing, lang_ratio = overlap(
        list(cv_data["languages"].keys()), list(job_data["languages"].keys())
    )

    # ── Weighted average ──────────────────────────────────
    overall = (
        tech_ratio * WEIGHTS["tech"] +
        prog_ratio * WEIGHTS["prog"] +
        soft_ratio * WEIGHTS["soft"] +
        lang_ratio * WEIGHTS["lang"]
    )

    # ── Required skills boost ─────────────────────────────
    # identify which skills the job marked as "required" (vs preferred/general)
    # and check how many of them the candidate actually has
    required_total = [
        k for k, v in job_data.get("importance", {}).items()
        if v == "required"
    ]
    required_found = [
        k for k in required_total
        if k.lower() in {s.lower() for s in cv_data["technical_skills"] + cv_data["soft_skills"]}
    ]

    # scale the boost by how many required skills are covered
    # e.g. covering 3 out of 5 required skills gives a +6% boost
    if required_total:
        req_boost = (len(required_found) / len(required_total)) * REQUIRED_SKILLS_BOOST
    else:
        req_boost = 0  # no required tags found in the job offer, no boost applied

    # ── Final score ───────────────────────────────────────
    # convert from 0-1 fraction to 0-100 integer and cap at 100
    final_score = min(100, round((overall + req_boost) * 100))

    # return a structured dict so the caller can display each category separately
    return {
        "overall": final_score,
        "tech": {"matched": tech_matched, "missing": tech_missing, "ratio": tech_ratio},
        "prog": {"matched": prog_matched, "missing": prog_missing, "ratio": prog_ratio},
        "soft": {"matched": soft_matched, "missing": soft_missing, "ratio": soft_ratio},
        "lang": {"matched": lang_matched, "missing": lang_missing, "ratio": lang_ratio},
        "required_found": required_found,
        "required_total": required_total,
    }
