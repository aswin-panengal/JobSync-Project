# JobSync - AI-Powered Resume and Job Matching Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.x-darkgreen?logo=django)
![spaCy](https://img.shields.io/badge/spaCy-3.x-09a3d5?logo=spacy)

JobSync addresses the inefficiencies of traditional job searching. This intelligent web application automates and optimizes the process by parsing a user's resume, extracting key skills, and matching them with relevant, real-time job listings from the JSearch API.

## 🚀 Key Features

* **User Authentication:** Secure sign-up, sign-in, and profile management.
* **Smart Resume Parsing:** Upload a PDF resume, and the system automatically extracts raw text using PyMuPDF.
* **AI Skill Extraction:** Leverages **spaCy's** NLP capabilities to identify and extract technical and professional skills from the resume text based on a predefined skill database (`skills_db.json`).
* **Personalized Preferences:** Users can set their interested domain, preferred location, experience level, and employment type.
* **Real-Time Job Matching:** Queries the JSearch API in real-time using a combination of the user's domain, extracted skills, and preferences to find the best-matched jobs.
* **Clean Results:** Displays job listings on a clean, responsive results page built with Tailwind CSS.

## 🛠️ Technology Stack

* **Backend:** Python, Django
* **NLP:** spaCy, PyMuPDF
* **Frontend:** HTML, Tailwind CSS
* **Database:** SQLite3 (for development)
* **API:** JSearch (via RapidAPI)

## ⚙️ Setup and Installation

Follow these steps to get a local copy up and running.

### Prerequisites

* [Python 3.10+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads)
* A [RapidAPI](https://rapidapi.com/hub) account to get a **JSearch API Key**.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/aswin-panengal/JobSync-Project.git](https://github.com/aswin-panengal/JobSync-Project.git)
    cd JobSync-Project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    (Ensure you have created a `requirements.txt` file first by running `pip freeze > requirements.txt`)
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the spaCy model:**
    ```bash
    python -m spacy download en_core_web_sm
    ```

5.  **Configure Your API Key:**
    * Open the `jobsync/settings.py` file.
    * Find the section for the API key (you may need to add it).
    * Add your JSearch API key:
        ```python
        RAPIDAPI_KEY = "your_actual_api_key_here" 
        ```

6.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

8.  Open your browser and go to `http://127.0.0.1:8000/`

## Usage

1.  **Register:** Create a new account.
2.  **Set Preferences:** Go to your profile and set your job preferences (domain, location, etc.).
3.  **Upload Resume:** Upload your resume in PDF format.
4.  **Search Jobs:** The system will parse your resume, extract your skills, and automatically fetch jobs that match your complete profile.
5.  **View Results:** Browse the matched job listings on the results page.

## 📈 Future Enhancements

* Implement advanced NLP (NER) for contextual skill recognition.
* Integrate multiple job source APIs (LinkedIn, Indeed).
* Add advanced filtering (salary range, date posted).
* Implement user features like saved jobs and application tracking.
* Deploy to a production environment (e.g., Vercel, Railway).
