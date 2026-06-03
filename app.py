"""
Module for the Streamlit UI:

CV Job Matcher — Web Interface
This module replaces the terminal-based main.py with a browser-based interface.
It orchestrates the same pipeline as main.py but through a Streamlit web app:

1. User uploads their CV (PDF, DOCX, or TXT)
2. User provides a job offer (URL, paste, or file upload)
3. Both documents are parsed using CV_Upload.py and Structure_Parser.py
4. A match score is computed and results are displayed with a full breakdown
"""

import streamlit as st
import tempfile
import os

# import the existing pipeline modules so we reuse the same logic as main.py
from CV_Upload import extract_text, extract_from_url, clean_text
from Structure_Parser import parse_cv, parse_job
from scorer import compute_score

# ============================================================
# Page Configuration
# Streamlit requires set_page_config to be the very first
# st call in the script, before any other rendering
# ============================================================

st.set_page_config(
    page_title="CV Job Matcher",
    page_icon="🎯",
    layout="wide",                      # use the full browser width
    initial_sidebar_state="collapsed",  # hide the sidebar by default
)

# ============================================================
# Custom CSS
# Injected as raw HTML so we can apply fonts, colours, and
# component overrides that Streamlit's theming system doesn't
# expose directly. All class names are prefixed to avoid
# clashing with Streamlit's internal styles.
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* Apply monospace body font across all Streamlit elements */
html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
}

/* Use the display font for all headings */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
}

/* Dark background for the whole app */
.stApp {
    background-color: #0e0e0e;
    color: #e8e3d8;
}

/* Constrain the content width and add vertical breathing room */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* Hero banner at the top of the page */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero h1 {
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: #e8e3d8;
    margin-bottom: 0.3rem;
}
.hero .accent { color: #c8f55a; } /* lime green highlight on the word "Job" */
.hero p {
    color: #888;
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Small uppercase label shown above each step section */
.step-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #c8f55a;
    margin-bottom: 0.3rem;
}

/* Thin horizontal rule used between sections */
.divider {
    border: none;
    border-top: 1px solid #222;
    margin: 2rem 0;
}

/* Skill tag pills — shared base style */
.tag-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 0.4rem; }
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 3px;
    font-size: 0.72rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.04em;
}
/* Each category gets its own colour scheme */
.tag-tech  { background:#1a2a0a; color:#c8f55a; border:1px solid #3a5a1a; } /* green  — technical */
.tag-soft  { background:#0a1a2a; color:#5ac8f5; border:1px solid #1a3a5a; } /* blue   — soft skills */
.tag-prog  { background:#2a0a1a; color:#f55ac8; border:1px solid #5a1a3a; } /* pink   — programming languages */
.tag-lang  { background:#1a1a0a; color:#f5c85a; border:1px solid #5a4a1a; } /* amber  — languages */
.tag-req   { background:#2a1a0a; color:#f5855a; border:1px solid #5a3a1a; } /* orange — required skills */
.tag-pref  { background:#0a2a1a; color:#5af5c8; border:1px solid #1a5a3a; } /* teal   — preferred skills */

/* Large score display box shown after analysis */
.score-box {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 1.5rem 2rem;
    text-align: center;
}
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    color: #c8f55a;
}
.score-label {
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #666;
    margin-top: 0.4rem;
}

/* Each row in the matched/missing skill list */
.match-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    border-bottom: 1px solid #1a1a1a;
    font-size: 0.8rem;
}
/* Small coloured dot to the left of each skill name */
.match-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.dot-match   { background:#c8f55a; } /* lime  — skill found in CV */
.dot-missing { background:#444; }    /* grey  — skill missing from CV */

/* Override Streamlit's default button appearance */
.stButton > button {
    background: #c8f55a !important;
    color: #0e0e0e !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.6rem 2rem !important;
    width: 100%;
}
.stButton > button:hover {
    background: #d8ff6a !important;
}

/* Style the file upload drop zone */
[data-testid="stFileUploader"] {
    background: #141414;
    border: 1px dashed #333;
    border-radius: 6px;
    padding: 0.5rem;
}

/* Style multi-line text input areas */
textarea {
    background: #141414 !important;
    color: #e8e3d8 !important;
    border: 1px solid #333 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* Style single-line text inputs (URL field) */
input[type="text"] {
    background: #141414 !important;
    color: #e8e3d8 !important;
    border: 1px solid #333 !important;
    font-family: 'DM Mono', monospace !important;
}

/* Slightly shrink the radio button labels */
[data-testid="stRadio"] label { font-size: 0.85rem; }

/* Style the collapsible expander panels */
[data-testid="stExpander"] {
    background: #141414;
    border: 1px solid #222 !important;
    border-radius: 4px;
}

/* Style the metric cards in the score breakdown */
[data-testid="stMetric"] {
    background: #141414;
    border: 1px solid #222;
    border-radius: 4px;
    padding: 0.8rem 1rem;
}

/* Shrink the default font size in info/warning/error alerts */
.stAlert { font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# Helper Functions
# ============================================================

def save_upload_to_temp(uploaded_file) -> str:
    """
    Streamlit's UploadedFile is an in-memory buffer, not a file on disk.
    CV_Upload.extract_text() needs a real file path, so we write the
    buffer to a temporary file and return its path.
    The caller is responsible for deleting the temp file afterwards.

    Parameters: uploaded_file — the Streamlit UploadedFile object
    Returns: path to the temporary file on disk
    """
    # preserve the original extension so extract_text() can detect the format
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())  # write the buffer to disk
        return tmp.name                  # return the path for the caller to use


def render_tags(items, css_class):
    """
    Renders a list of skill keywords as coloured pill tags in the UI.
    Each category has its own CSS class (tag-tech, tag-soft, etc.) which
    controls the background/border colour defined in the CSS block above.

    Parameters:
        items     — list of skill strings to display
        css_class — CSS class name string (e.g. "tag-tech")
    """
    if not items:
        # show a muted placeholder so the layout doesn't collapse
        st.markdown("<span style='color:#555;font-size:0.8rem'>None found</span>", unsafe_allow_html=True)
        return
    # build all tags as a single HTML string to avoid one st.markdown() call per tag
    html = "<div class='tag-wrap'>" + "".join(
        f"<span class='tag {css_class}'>{item}</span>" for item in sorted(items)
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_match_list(matched, missing):
    """
    Renders a side-by-side list of matched and missing skills.
    Matched skills show a green dot; missing skills show a grey dot
    and a muted text colour so the gap is immediately obvious.

    Parameters:
        matched — list of skill strings found in both CV and job offer
        missing — list of skill strings in the job offer but not in the CV
    """
    html = ""
    # matched skills first so the positive result appears at the top
    for item in sorted(matched):
        html += f"<div class='match-row'><div class='match-dot dot-match'></div>{item}</div>"
    # missing skills below, greyed out
    for item in sorted(missing):
        html += f"<div class='match-row'><div class='match-dot dot-missing'></div><span style='color:#555'>{item}</span></div>"
    if html:
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("<span style='color:#555;font-size:0.8rem'>No overlap to show</span>", unsafe_allow_html=True)


# ============================================================
# Session State Initialisation
# Streamlit reruns the entire script on every user interaction,
# so we store results in st.session_state to persist them across
# reruns without re-running the parsing pipeline each time.
# ============================================================

for key in ("cv_text", "job_text", "cv_data", "job_data", "score"):
    if key not in st.session_state:
        st.session_state[key] = None  # initialise each key to None on first load


# ============================================================
# Hero Banner
# ============================================================

st.markdown("""
<div class="hero">
  <h1>CV <span class="accent">Job</span> Matcher</h1>
  <p>Upload your CV · Provide a job offer · Get your match score</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ============================================================
# Step 1 & Step 2 — Inputs
# Laid out side by side so both inputs are visible at once
# without the user needing to scroll
# ============================================================

col1, col2 = st.columns(2, gap="large")

# ── Step 1: CV Upload ──────────────────────────────────────
with col1:
    st.markdown("<div class='step-label'>Step 01 — Your CV</div>", unsafe_allow_html=True)

    # accept PDF, DOCX, and TXT — the same formats handled by CV_Upload.extract_text()
    cv_file = st.file_uploader(
        "Upload your CV",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",  # hide the default label since step-label covers it
    )

    if cv_file:
        try:
            # write to a temp file so extract_text() can open it by path
            tmp_path = save_upload_to_temp(cv_file)
            cv_text  = extract_text(tmp_path)
            os.unlink(tmp_path)  # clean up the temp file immediately after reading

            # store extracted text in session state so it survives Streamlit reruns
            st.session_state.cv_text = cv_text
            st.success(f"✓ {cv_file.name}  ·  {len(cv_text):,} chars")
        except Exception as e:
            st.error(f"Could not read CV: {e}")
            st.session_state.cv_text = None  # reset on error so stale data isn't used

# ── Step 2: Job Offer Input ────────────────────────────────
with col2:
    st.markdown("<div class='step-label'>Step 02 — Job Offer</div>", unsafe_allow_html=True)

    # mirror the cascading input approach from main.py: URL first, then paste, then file
    job_input_method = st.radio(
        "Job input method",
        ["URL", "Paste text", "Upload file"],
        horizontal=True,
        label_visibility="collapsed",
    )

    job_text = None  # will be set by whichever input method succeeds

    if job_input_method == "URL":
        url = st.text_input("Job offer URL", placeholder="https://...")
        if url:
            with st.spinner("Fetching page…"):
                # extract_from_url() tries requests first, then falls back to Selenium
                job_text = extract_from_url(url)
            if job_text:
                st.success(f"✓ Fetched  ·  {len(job_text):,} chars")
            else:
                st.error("Could not extract text from that URL.")

    elif job_input_method == "Paste text":
        pasted = st.text_area("Paste job description here", height=180, placeholder="Paste the full job description…")
        if pasted.strip():
            # run the same clean_text() that the terminal version applies to pasted input
            job_text = clean_text(pasted)
            st.success(f"✓ {len(job_text):,} chars captured")

    else:
        # file upload — same logic as the CV upload above
        job_file = st.file_uploader(
            "Upload job description",
            type=["pdf", "docx", "txt"],
            key="job_file",  # unique key needed because Streamlit only allows one uploader per key
            label_visibility="collapsed",
        )
        if job_file:
            try:
                tmp_path = save_upload_to_temp(job_file)
                job_text = extract_text(tmp_path)
                os.unlink(tmp_path)  # clean up temp file
                st.success(f"✓ {job_file.name}  ·  {len(job_text):,} chars")
            except Exception as e:
                st.error(f"Could not read file: {e}")

    # persist the job text in session state regardless of which method was used
    if job_text:
        st.session_state.job_text = job_text


# ============================================================
# Analyse Button
# Centred in a narrow middle column so it doesn't stretch
# edge-to-edge across the full page width
# ============================================================

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

_, btn_col, _ = st.columns([2, 1, 2])  # flanking empty columns to centre the button
with btn_col:
    analyse = st.button("Analyse Match →")

if analyse:
    # validate that both inputs are ready before running the pipeline
    if not st.session_state.cv_text:
        st.warning("Please upload your CV first.")
    elif not st.session_state.job_text:
        st.warning("Please provide the job offer first.")
    else:
        with st.spinner("Parsing documents…"):
            # run the same parsing functions used by main.py
            cv_data  = parse_cv(st.session_state.cv_text)
            job_data = parse_job(st.session_state.job_text)
            score    = compute_score(cv_data, job_data)

        # store results in session state so they persist after the button press reruns the script
        st.session_state.cv_data  = cv_data
        st.session_state.job_data = job_data
        st.session_state.score    = score


# ============================================================
# Step 3 — Results
# Only renders once session_state.score has been populated
# (i.e. after the user clicks Analyse Match)
# ============================================================

if st.session_state.score:
    # pull all three results objects out of session state for cleaner code below
    score    = st.session_state.score
    cv_data  = st.session_state.cv_data
    job_data = st.session_state.job_data

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='step-label'>Step 03 — Results</div>", unsafe_allow_html=True)

    # ── Overall score + per-category metric cards ──────────
    score_col, metrics_col = st.columns([1, 2], gap="large")

    with score_col:
        # convert the numeric score into a simple text grade for quick readability
        grade = "Excellent" if score["overall"] >= 75 else "Good" if score["overall"] >= 50 else "Needs Work"
        st.markdown(f"""
        <div class='score-box'>
          <div class='score-number'>{score["overall"]}</div>
          <div class='score-label'>/ 100 &nbsp;·&nbsp; {grade}</div>
        </div>
        """, unsafe_allow_html=True)

    with metrics_col:
        # show a percentage card for each of the four categories
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Technical",    f"{score['tech']['ratio']*100:.0f}%")
        m2.metric("Programming",  f"{score['prog']['ratio']*100:.0f}%")
        m3.metric("Soft Skills",  f"{score['soft']['ratio']*100:.0f}%")
        m4.metric("Languages",    f"{score['lang']['ratio']*100:.0f}%")

        # only show the required-skills line if the job offer had any required tags
        if score["required_total"]:
            req_pct = round(len(score["required_found"]) / len(score["required_total"]) * 100)
            st.markdown(
                f"<div style='font-size:0.8rem;color:#888;margin-top:0.8rem'>"
                f"Required skills covered: <span style='color:#c8f55a'>{req_pct}%</span> "
                f"({len(score['required_found'])} / {len(score['required_total'])})</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Detailed skill breakdown tabs ──────────────────────
    # Each tab shows CV skills vs. job skills side by side,
    # then a matched/missing breakdown below
    tab1, tab2, tab3, tab4 = st.tabs(["Technical Skills", "Programming", "Soft Skills", "Languages"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Your CV**")
            render_tags(cv_data["technical_skills"], "tag-tech")
        with c2:
            st.markdown("**Job Requires**")
            render_tags(job_data["technical_skills"], "tag-tech")
        st.markdown("**Match breakdown** — <span style='color:#c8f55a'>●</span> matched &nbsp; <span style='color:#444'>●</span> missing from CV", unsafe_allow_html=True)
        render_match_list(score["tech"]["matched"], score["tech"]["missing"])

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Your CV**")
            render_tags(cv_data["programming"], "tag-prog")
        with c2:
            st.markdown("**Job Requires**")
            render_tags(job_data["programming"], "tag-prog")
        st.markdown("**Match breakdown**", unsafe_allow_html=True)
        render_match_list(score["prog"]["matched"], score["prog"]["missing"])

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Your CV**")
            render_tags(cv_data["soft_skills"], "tag-soft")
        with c2:
            st.markdown("**Job Requires**")
            render_tags(job_data["soft_skills"], "tag-soft")
        st.markdown("**Match breakdown**", unsafe_allow_html=True)
        render_match_list(score["soft"]["matched"], score["soft"]["missing"])

    with tab4:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Your CV**")
            # include the proficiency level in the tag text (e.g. "french (advanced)")
            lang_items = [f"{lang} ({info['level']})" for lang, info in cv_data["languages"].items()]
            render_tags(lang_items, "tag-lang")
        with c2:
            st.markdown("**Job Requires**")
            lang_items_job = [f"{lang} ({info['level']})" for lang, info in job_data["languages"].items()]
            render_tags(lang_items_job, "tag-lang")
        st.markdown("**Match breakdown**", unsafe_allow_html=True)
        # strip the proficiency level for the plain comparison (just language names)
        render_match_list(score["lang"]["matched"], score["lang"]["missing"])

    # ── Skill importance tags (collapsible) ────────────────
    # Only shown when the parser found importance tags in the job offer
    # (i.e. skills in required/preferred/responsibility sections)
    if job_data.get("importance"):
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        with st.expander("Skill importance tags from job offer"):
            # split skills by importance level so the user can see what's required vs. nice-to-have
            req  = [k for k, v in job_data["importance"].items() if v == "required"]
            pref = [k for k, v in job_data["importance"].items() if v == "preferred"]
            resp = [k for k, v in job_data["importance"].items() if v == "responsibility"]
            if req:
                st.markdown("**Required**")
                render_tags(req, "tag-req")
            if pref:
                st.markdown("**Preferred**")
                render_tags(pref, "tag-pref")
            if resp:
                st.markdown("**Responsibilities**")
                render_tags(resp, "tag-tech")

    # ── Experience requirements (collapsible) ──────────────
    # Shows the exact phrases extracted by extract_experience_requirements()
    # so the user can see the original context for each year requirement
    if job_data.get("experience_required"):
        with st.expander("Experience requirements in job offer"):
            for exp in job_data["experience_required"]:
                st.markdown(f"- **{exp['years']} year(s)** — _{exp['context']}_")

    # ── Reset button ───────────────────────────────────────
    # Clears all session state and reruns the script from the top,
    # returning the user to the empty input state
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    if st.button("← Start over"):
        for key in ("cv_text", "job_text", "cv_data", "job_data", "score"):
            st.session_state[key] = None
        st.rerun()
