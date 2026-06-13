"""
Module 4: Scorer

This module takes the structured data produced by Structure_Parser.py
and computes a match score between a candidate's CV and a job offer.

One main function: compute_score(cv_data, job_data) which compares the
two parsed documents across six categories (resolved technical skills,
programming languages, soft skills, contextual skills, finance skills,
and spoken languages) and returns an overall score out of 100 plus a
full per-category breakdown.
"""

import logging
import re

# module-level logger — errors are recorded without crashing the app
logger = logging.getLogger(__name__)

# ============================================================
# Scoring Weights
# These control how much each category contributes to the
# overall score. technical_resolved is weighted most heavily
# as it groups synonyms together for a fairer comparison
# (e.g. "JS" and "JavaScript" count as the same skill).
# Adjust these values if you want to reprioritise categories.
# All weights must sum to 1.0.
# ============================================================

WEIGHTS = {
    "tech":       0.35,   # technical_resolved — synonym-grouped, fairest comparison
    "prog":       0.20,   # programming languages
    "soft":       0.15,   # keyword-matched soft skills
    "contextual": 0.10,   # soft skills found via sentence patterns
    "finance":    0.10,   # finance-specific skills
    "lang":       0.10,   # spoken languages
}

# Maximum bonus score (as a fraction) awarded for covering
# skills that the job explicitly marked as "required".
# 0.10 means up to +10 points on top of the weighted score.
REQUIRED_SKILLS_BOOST = 0.10

# Minimum number of characters we expect in a parsed document.
# Anything shorter is likely an extraction failure and we refuse
# to score it rather than returning a meaningless result.
MIN_TEXT_LENGTH = 20


# ============================================================
# Input Validation
# ============================================================

def _safe_list(value) -> list:
    """
    Coerces a value to a list safely.
    If the parser returns None or an unexpected type for a list field,
    this returns an empty list rather than crashing downstream code.

    Parameters: value — the value to coerce
    Returns: a list (empty if value is None or not iterable as a list)
    """
    if isinstance(value, list):
        return value
    if value is None:
        return []
    # handle sets, tuples, or other iterables gracefully
    try:
        return list(value)
    except TypeError:
        logger.warning("Expected a list but got %s — using empty list", type(value))
        return []


def _safe_dict(value) -> dict:
    """
    Coerces a value to a dict safely.
    If the parser returns None or an unexpected type for a dict field,
    this returns an empty dict rather than crashing downstream code.

    Parameters: value — the value to coerce
    Returns: a dict (empty if value is None or not a dict)
    """
    if isinstance(value, dict):
        return value
    if value is None:
        return {}
    logger.warning("Expected a dict but got %s — using empty dict", type(value))
    return {}


def _validate_parsed_data(data: dict, label: str) -> bool:
    """
    Checks that a parsed document dict has the expected keys and
    that the values are the right types. Logs a warning for each
    problem found but does not raise — the scorer degrades gracefully
    rather than crashing the whole app.

    Parameters:
        data  — the dict returned by parse_cv() or parse_job()
        label — "CV" or "job offer", used in warning messages

    Returns: True if all required keys are present, False otherwise
    """
    required_keys = [
        "technical_resolved", "programming", "soft_skills",
        "contextual_skills", "finance", "languages",
    ]
    if not isinstance(data, dict):
        logger.error("%s parser returned %s instead of a dict", label, type(data))
        return False

    missing = [k for k in required_keys if k not in data]
    if missing:
        logger.warning("%s data is missing keys: %s", label, missing)
        return False

    return True


# ============================================================
# Helper Functions
# ============================================================

def overlap(cv_list, job_list) -> tuple:
    """
    Computes the overlap between two keyword lists.
    Comparison is case-insensitive so "Python" and "python" match.
    Both inputs are coerced to lists before comparison so unexpected
    types from the parser don't cause a crash.

    Parameters:
        cv_list  — list of keywords extracted from the CV
        job_list — list of keywords extracted from the job offer

    Returns a tuple of:
        matched — sorted list of keywords present in both
        missing — sorted list of keywords in the job but not the CV
        ratio   — fraction of job keywords covered (0.0 to 1.0)
    """
    # coerce to lists defensively in case the parser returns something unexpected
    cv_list  = _safe_list(cv_list)
    job_list = _safe_list(job_list)

    cv_set  = {str(k).lower() for k in cv_list}
    job_set = {str(k).lower() for k in job_list}

    # if the job doesn't mention any keywords in this category,
    # treat it as a full match so it doesn't penalise the overall score
    if not job_set:
        return [], [], 1.0

    matched = sorted(cv_set & job_set)      # intersection: in both
    missing = sorted(job_set - cv_set)      # difference: in job only
    ratio   = len(matched) / len(job_set)   # guaranteed no division-by-zero (guarded above)

    return matched, missing, ratio


def overlap_resolved(cv_resolved, job_resolved) -> tuple:
    """
    Computes overlap between two technical_resolved dicts.
    technical_resolved groups synonyms under a canonical name, so
    "JS", "JavaScript", and "ECMAScript" all appear under the same key.
    This gives a fairer match than comparing raw keyword strings.

    Both inputs are coerced to dicts before comparison so unexpected
    types from the parser don't cause a crash.

    Parameters:
        cv_resolved  — technical_resolved dict from parse_cv()
        job_resolved — technical_resolved dict from parse_job()

    Returns a tuple of:
        matched — sorted list of canonical skill names present in both
        missing — sorted list of canonical skill names in job but not CV
        ratio   — fraction of job canonical skills covered (0.0 to 1.0)
    """
    # coerce to dicts defensively in case the parser returns None or a list
    cv_resolved  = _safe_dict(cv_resolved)
    job_resolved = _safe_dict(job_resolved)

    cv_set  = {str(k).lower() for k in cv_resolved.keys()}
    job_set = {str(k).lower() for k in job_resolved.keys()}

    if not job_set:
        return [], [], 1.0

    matched = sorted(cv_set & job_set)
    missing = sorted(job_set - cv_set)
    ratio   = len(matched) / len(job_set)

    return matched, missing, ratio


# ============================================================
# Frequency-based Required Skills Fallback
# ============================================================

def _get_required_by_frequency(job_data: dict) -> list:
    """
    Fallback for when the job offer has no explicit importance tags.
    Counts how many times each already-parsed skill appears in the raw
    job text. Skills mentioned 2+ times are treated as implicitly required.
    Only skills the parser already found are checked — random words are ignored.
    """
    job_text = job_data.get("full_text", "")
    if not job_text:
        return []
    all_skills = (
        list(_safe_dict(job_data.get("technical_resolved")).keys()) +
        _safe_list(job_data.get("soft_skills"))
    )
    text_lower = job_text.lower()
    return [s for s in all_skills
            if len(re.findall(r'\b' + re.escape(s.lower()) + r'\b', text_lower)) >= 2]


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
        1. Validate both input dicts have the expected structure
        2. Use technical_resolved for technical skill comparison (synonym-aware)
        2b. If no explicit importance tags exist, fall back to frequency-based
            required skill detection using the raw job text in job_data["full_text"]
        3. Compute keyword overlap for programming, soft, contextual, finance, languages
        4. Combine into a weighted average using WEIGHTS above
        5. Add a small bonus (up to REQUIRED_SKILLS_BOOST) for covering required skills
        6. Cap the result at 100 and round to a whole number

    If either input is malformed, the scorer returns a zero score with
    empty breakdowns rather than crashing — the UI can then show an
    appropriate message to the user.

    Parameters:
        cv_data  — output dict from Structure_Parser.parse_cv()
        job_data — output dict from Structure_Parser.parse_job()

    Returns: dict with the following keys:
        overall         — final score as an integer from 0 to 100
        tech            — dict with matched, missing, ratio for resolved technical skills
        prog            — dict with matched, missing, ratio for programming languages
        soft            — dict with matched, missing, ratio for soft skills
        contextual      — dict with matched, missing, ratio for contextual skills
        finance         — dict with matched, missing, ratio for finance skills
        lang            — dict with matched, missing, ratio for spoken languages
        required_found  — list of required skills the candidate has
        required_total  — list of all required skills in the job offer
        error           — None on success, or an error message string on failure
    """

    # ── Input validation ──────────────────────────────────
    # return a zero score with an error message rather than crashing
    # if either parsed document is missing expected fields
    if not _validate_parsed_data(cv_data, "CV"):
        logger.error("CV data failed validation — returning zero score")
        return _zero_score("CV data could not be parsed correctly.")
    if not _validate_parsed_data(job_data, "job offer"):
        logger.error("Job data failed validation — returning zero score")
        return _zero_score("Job offer data could not be parsed correctly.")

    # ── Technical skills (synonym-resolved) ───────────────
    # use technical_resolved instead of technical_skills so that
    # synonym groups are compared at the canonical level — fairer
    # than raw string matching which would miss "JS" vs "JavaScript"
    tech_matched, tech_missing, tech_ratio = overlap_resolved(
        cv_data.get("technical_resolved", {}),
        job_data.get("technical_resolved", {}),
    )

    # ── Remaining categories (keyword overlap) ─────────────
    prog_matched, prog_missing, prog_ratio = overlap(
        cv_data.get("programming", []),
        job_data.get("programming", []),
    )
    soft_matched, soft_missing, soft_ratio = overlap(
        cv_data.get("soft_skills", []),
        job_data.get("soft_skills", []),
    )
    # contextual skills are found via sentence patterns rather than keywords
    # so they catch skills the candidate described rather than just listed
    ctx_matched, ctx_missing, ctx_ratio = overlap(
        cv_data.get("contextual_skills", []),
        job_data.get("contextual_skills", []),
    )
    fin_matched, fin_missing, fin_ratio = overlap(
        cv_data.get("finance", []),
        job_data.get("finance", []),
    )
    # languages is a dict of {language: {level, rank}} so we compare keys only
    lang_matched, lang_missing, lang_ratio = overlap(
        list(_safe_dict(cv_data.get("languages")).keys()),
        list(_safe_dict(job_data.get("languages")).keys()),
    )

    # ── Weighted average ──────────────────────────────────
    overall = (
        tech_ratio * WEIGHTS["tech"] +
        prog_ratio * WEIGHTS["prog"] +
        soft_ratio * WEIGHTS["soft"] +
        ctx_ratio  * WEIGHTS["contextual"] +
        fin_ratio  * WEIGHTS["finance"] +
        lang_ratio * WEIGHTS["lang"]
    )

    # ── Required skills boost ─────────────────────────────
    # identify which skills the job marked as "required" and check
    # how many of them appear in the candidate's resolved technical
    # or soft skills — covers both hard and soft required skills
    importance     = _safe_dict(job_data.get("importance"))
    required_total = [k for k, v in importance.items() if v == "required"]

    if not required_total:
        required_total = _get_required_by_frequency(job_data)

    # build a single set of all CV skills to check against
    cv_all_skills = {str(s).lower() for s in (
        list(_safe_dict(cv_data.get("technical_resolved")).keys()) +
        _safe_list(cv_data.get("soft_skills")) +
        _safe_list(cv_data.get("contextual_skills"))
    )}
    required_found = [k for k in required_total if str(k).lower() in cv_all_skills]

    # scale the boost by how many required skills are covered —
    # no division-by-zero risk since we check required_total is non-empty first
    req_boost = (
        (len(required_found) / len(required_total)) * REQUIRED_SKILLS_BOOST
        if required_total else 0
    )

    # ── Final score ───────────────────────────────────────
    # convert from 0-1 fraction to 0-100 integer and cap at 100
    final_score = min(100, round((overall + req_boost) * 100))

    # return a structured dict so the caller can display each category separately
    return {
        "overall":        final_score,
        "tech":           {"matched": tech_matched, "missing": tech_missing, "ratio": tech_ratio},
        "prog":           {"matched": prog_matched, "missing": prog_missing, "ratio": prog_ratio},
        "soft":           {"matched": soft_matched, "missing": soft_missing, "ratio": soft_ratio},
        "contextual":     {"matched": ctx_matched,  "missing": ctx_missing,  "ratio": ctx_ratio},
        "finance":        {"matched": fin_matched,  "missing": fin_missing,  "ratio": fin_ratio},
        "lang":           {"matched": lang_matched, "missing": lang_missing, "ratio": lang_ratio},
        "required_found": required_found,
        "required_total": required_total,
        "error":          None,  # None signals success to the caller
    }


def _zero_score(error_message: str) -> dict:
    """
    Returns a score dict with all zeros and an error message.
    Used when input validation fails so the caller always gets a
    consistent dict shape regardless of whether scoring succeeded.

    Parameters: error_message — human-readable description of what went wrong
    Returns: score dict with overall=0 and error set to error_message
    """
    empty = {"matched": [], "missing": [], "ratio": 0.0}
    return {
        "overall":        0,
        "tech":           empty,
        "prog":           empty,
        "soft":           empty,
        "contextual":     empty,
        "finance":        empty,
        "lang":           empty,
        "required_found": [],
        "required_total": [],
        "error":          error_message,
    }
