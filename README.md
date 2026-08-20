# NYC Airbnb Market Intelligence

**Expernetic (Pvt) Ltd — Data Engineer Intern Technical Assessment**
Candidate: Subhani Dulshini · SLIIT, BSc (Hons) Information Technology, Data Science
[GitHub](https://github.com/subhani257) · [LinkedIn](https://linkedin.com/in/subhani-dulshini)

An end-to-end data engineering and analytics project on the Inside Airbnb
New York City dataset: raw data ingestion, cleaning, a DuckDB star schema,
exploratory and statistical analysis, machine learning (price prediction,
clustering), NLP sentiment analysis on guest reviews, and an interactive
Streamlit dashboard.

**Single-city scope (NYC) chosen deliberately for analytical depth over
multi-city breadth** — see the report §2.2 for the full reasoning.

---

## 📄 Start here

| If you want to... | Go to |
|---|---|
| Read the full findings, methodology, and business recommendations | `Airbnb_Market_Intelligence_Report.pdf` |
| Set up the project and run it yourself | `PROJECT_DOCUMENTATION.md` → Part A |
| See what was assumed, decided, completed, and left out | `PROJECT_DOCUMENTATION.md` → Parts B–E |
| Try the interactive dashboard without running notebooks | `dashboard/README.md` |

---

## 📁 Project structure

```
.
├── data/
│   ├── raw/                          
│   ├── interim/                      
│   └── airbnb_warehouse.duckdb       
├── docs/
│   └── data_quality_report.csv       
├── notebooks/
│   ├── 01_dataset_exploration.ipynb  # Dataset Familiarization
│   ├── 02_data_engineering.ipynb     # Ingestion, cleaning, star schema, pipeline
│   ├── 03_eda.ipynb                  # Exploratory Data Analysis
│   ├── 04_statistical_analysis.ipynb # Statistical Analysis (H1–H5)
│   ├── 05_data_science.ipynb         # Price prediction + clustering
│   └── 06_ai_nlp.ipynb               # VADER sentiment analysis
├── dashboard/
│   ├── app.py                        # Streamlit app — 8 interactive sections
│   ├── requirements.txt
│   ├── README.md                     # dashboard-specific setup guide
│   └── .streamlit/config.toml
├── docker-compose.yml                # containerized Jupyter environment
├── requirements.txt                  # pinned dependencies for notebooks (pip freeze)
├── PROJECT_DOCUMENTATION.md          # reproducibility + assumptions/decisions + work summary
├── Airbnb_Market_Intelligence_Report.pdf
└── README.md                         # this file
```

> **Note:** raw data files are **not committed** to this repository
> (Inside Airbnb's detailed listings/reviews files are large and are
> public data, not project IP). See "Getting the data" below.

---

## 🚀 Quickstart

```bash
# 1. Set up environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Get the data (see below), then run notebooks in order
#    01 → 02 → 03 → 04 → 05 → 06

# 3. Try the dashboard
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

Full step-by-step instructions, including exact package list and
verification checklist, are in **`PROJECT_DOCUMENTATION.md` → Part A**.

## 📥 Getting the data

1. [insideairbnb.com/get-the-data](https://insideairbnb.com/get-the-data/) → **New York City**, scrape date **14 June 2026**.
2. Download the **detailed** listings and **detailed** reviews files (not the summary versions).
3. Place them in `data/raw/` as `listings2.csv`, `calendar.csv`, `reviews2.csv`, `neighbourhoods.csv`.

## 🐳 Running with Docker (alternative to local setup)

```bash
docker-compose up
```

Starts a Jupyter environment at `localhost:8888` (token: `airbnb2026`).
Note: base image only — project dependencies still install via each
notebook's own `!pip install` cells. See `PROJECT_DOCUMENTATION.md` →
Part A.6 for details.

---

## 🔑 Key findings (see report for full detail)

- Price is driven primarily by capacity and location, not review score (r = 0.041 with rating).
- Manhattan listings cost more than double the Bronx median ($240.56 vs. $106.39/night, p < 0.001).
- 13.79% of hosts control 50% of all listings — a professionalized, not purely peer-to-peer, market.
- Random Forest predicts price with R² = 0.564, outperforming Linear Regression and XGBoost (default params).
- K-Means (k=5) surfaces a 28-listing ultra-luxury segment averaging $4,967/night.
- Review sentiment correlates only moderately with star ratings (r = 0.270) — text and stars capture different signals.

## 🖥️ Dashboard

The Streamlit dashboard (`dashboard/app.py`) provides 8 live sections:
Overview, Geographic Explorer, Pricing & Market, Host Analysis,
Statistical Insights (live hypothesis tests), Price Predictor (trains
live), Listing Segments (K-Means), and Reviews & Sentiment.

## 🤖 AI usage disclosure

AI tools (Claude, ChatGPT, GitHub Copilot) were used throughout this
project for code assistance, dashboard generation, and report/documentation
drafting — always reviewed and validated against actual notebook output
before inclusion. Full disclosure, including a documented instance of
catching and correcting an AI-fabricated result, is in the report's
Appendix A.

## 📋 Deliverables checklist (per assignment §11.1)

- [x] Source code (`notebooks/`, `dashboard/`)
- [x] Reproducibility instructions (`PROJECT_DOCUMENTATION.md` Part A)
- [x] Professional PDF report (`Airbnb_Market_Intelligence_Report.pdf`)
- [x] Assumptions & Decisions Log (`PROJECT_DOCUMENTATION.md` Parts B–C)
- [x] Summary of completed / incomplete work (`PROJECT_DOCUMENTATION.md` Parts D–E)
- [x] AI Usage Disclosure (report Appendix A)
- [x] Interactive dashboard (`dashboard/`)
- [x] Docker Compose (`docker-compose.yml`)

---

*Confidential — candidate submission for Expernetic (Pvt) Ltd's Data Engineer Intern Talent Assessment Program.*
