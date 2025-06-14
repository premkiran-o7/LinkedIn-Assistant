# LinkedIn-Assistant

An intelligent LinkedIn profile optimization tool that analyzes LinkedIn profiles, suggests improvements, recommends skills and certifications, performs skill gap analysis, and generates personalized career roadmaps — all powered by cutting-edge LLMs and LangGraph.

## 📊 Features
✅ LinkedIn profile scraping via Apify

✅ Modular state machine using LangGraph

✅ Intent-based routing for dynamic queries

✅ Personalized job description generation

✅ Skill suggestion and certification recommendation

✅ Career path planning

✅ Profile audits and gap analysis

✅ Streamlit-based interactive chat interface

---

# 🔄 Steps to Rerun the LinkedIn Career Coach App

## 1️⃣ Clone the repository (if fresh)

```bash
git clone <your-repo-url>
cd LinkedIn-Assistant
```

---

## 2️⃣ Create virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)
```

---

## 3️⃣ Install dependencies

> If you have `requirements.txt`:

```bash
pip install -r requirements.txt
```

> Or if you're using `pyproject.toml`:

```bash
pip install .
```

---

## 4️⃣ Set environment variables

### Option 1: Create `.env` file (for local run)

```env
GROQ_API_KEY=your_groq_api_key
APIFY_TOKEN=your_apify_token
```

> Also ensure `cookies.json` file is present in root directory with valid LinkedIn cookies.

### Option 2: (For Streamlit Cloud deployment)

* Go to **Settings → Secrets Manager**
* Paste contents of `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_groq_api_key"
APIFY_TOKEN = "your_apify_token"
cookie = 'paste_full_cookie_json_here'
```

---

## 5️⃣ Run Streamlit app

```bash
streamlit run main.py
```

---

✅ That’s all — this will fully rerun your app.

---


