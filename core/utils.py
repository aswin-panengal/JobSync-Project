# core/utils.py

import fitz  # PyMuPDF
import spacy
import requests
import json
import os
from spacy.matcher import Matcher
from django.conf import settings

# --- NLP Setup ---
def load_skills(json_path):
    """Loads skills from the JSON database."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [skill.lower() for skill in data['skills']] # Return lowercase skills
    except FileNotFoundError:
        print(f"ERROR: Skills file not found at {json_path}")
        return []
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from {json_path}")
        return []

def build_skill_matcher(nlp_model, skill_list):
    """Builds the spaCy Matcher."""
    if not nlp_model:
        print("ERROR: Cannot build matcher, NLP model not loaded.")
        return None
    matcher = Matcher(nlp_model.vocab)
    for skill in skill_list:
        pattern_parts = skill.split()
        pattern = [{'LOWER': part} for part in pattern_parts]
        # Allow optional hyphen between words for multi-word skills
        matcher.add(skill.upper(), [pattern]) # Use skill as ID
    return matcher

# Load NLP model and skills ONCE when the server starts
print("Loading NLP model...")
NLP = None
try:
    NLP = spacy.load("en_core_web_sm")
    print("NLP model loaded successfully.")
except OSError:
    print("ERROR: spaCy model 'en_core_web_sm' not found. Run 'python -m spacy download en_core_web_sm'")

SKILLS_FILE_PATH = os.path.join(settings.BASE_DIR, 'skills_db.json')
SKILL_LIST = load_skills(SKILLS_FILE_PATH) if NLP else []
SKILL_MATCHER = build_skill_matcher(NLP, SKILL_LIST) if NLP and SKILL_LIST else None
if NLP and SKILL_LIST:
    print(f"Loaded {len(SKILL_LIST)} skills for matching.")
elif not NLP:
     print("Skipping skill loading due to NLP model error.")
else:
     print("NLP model loaded, but failed to load skills from JSON.")


# --- Service Functions ---
def extract_text_from_pdf(pdf_file_path):
    """Opens a PDF and returns its text content."""
    if not os.path.exists(pdf_file_path):
         print(f"ERROR: PDF file not found at {pdf_file_path}")
         return ""
    try:
        doc = fitz.open(pdf_file_path)
        full_text = "".join(page.get_text("text") for page in doc)
        doc.close()
        return full_text
    except Exception as e:
        print(f"ERROR opening or reading PDF {pdf_file_path}: {e}")
        return ""

def extract_skills(text):
    """Processes text with spaCy Matcher to find skills."""
    if not NLP or not SKILL_MATCHER:
        print("ERROR: NLP model or matcher not loaded. Cannot extract skills.")
        return []
    if not text:
         return []

    try:
        doc = NLP(text.lower())
        matches = SKILL_MATCHER(doc)
        skill_lookup = {skill.upper(): skill for skill in SKILL_LIST}
        found_skills_ids = {match_id for match_id, start, end in matches}
        found_skills = set()
        for skill_id_hash in found_skills_ids:
             if skill_id_hash in NLP.vocab.strings:
                 skill_id_str = NLP.vocab.strings[skill_id_hash]
                 if skill_id_str in skill_lookup:
                      found_skills.add(skill_lookup[skill_id_str])
        return sorted([skill.title() for skill in found_skills]) # Return Title Case
    except Exception as e:
         print(f"ERROR during spaCy skill matching: {e}")
         return []


def fetch_jobs_api(skills_list, location, interested_domain=None, salary=None, experience=None, employment_types=None):
    """
    Fetches jobs from JSearch API using domain OR top skill, location, and specific filters.
    """
    # Prepare Base Query (Domain or Top Skill)
    base_query = ""
    if interested_domain and str(interested_domain).strip():
        base_query = str(interested_domain).strip()
    elif skills_list:
        top_skill = next((str(skill).strip() for skill in skills_list if skill), None)
        if top_skill: base_query = top_skill

    if not base_query:
         print("fetch_jobs_api: No domain or skills for query.")
         return []

    # Prepare Location Query
    location_query = str(location).strip() if location and location.lower() not in ['india', 'anywhere'] else "India"
    final_query = f"{base_query} in {location_query}"

    # Prepare API URL and Querystring with Filters
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = { "query": final_query, "num_pages": "1", "country": "in" }
    if employment_types: querystring['employment_types'] = employment_types
    if experience and experience != 'Any': querystring['job_requirements'] = experience

    # API Key Check
    api_key = getattr(settings, 'RAPIDAPI_KEY', None)
    if not api_key:
        print("ERROR: RAPIDAPI_KEY not found in settings.py")
        return []

    # Headers
    headers = { "X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}

    # Make API Request
    print(f"Fetching jobs with query: {querystring.get('query')} and filters: { {k:v for k,v in querystring.items() if k != 'query'} }") # Concise log
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        response.raise_for_status()
        data = response.json()
        jobs_data = data.get('data', [])
        print(f"API returned {len(jobs_data)} jobs.") # Log result count
        return jobs_data
    except requests.exceptions.Timeout: print("ERROR: API request timed out."); return []
    except requests.exceptions.HTTPError as http_err: print(f"ERROR: API HTTP error: {http_err} - Status: {response.status_code}"); return []
    except requests.exceptions.RequestException as e: print(f"ERROR: API request failed: {e}"); return []
    except json.JSONDecodeError: print("ERROR: Could not decode API JSON response."); return []
    except Exception as e: print(f"ERROR: Unexpected error in API call: {e}"); return []