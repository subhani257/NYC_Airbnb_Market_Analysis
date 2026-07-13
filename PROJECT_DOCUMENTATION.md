# Project Documentation

## Reproducibility Instructions · Assumptions \& Decisions Log · Work Summary

NYC Airbnb Market Intelligence — Expernetic Data Engineer Intern Assessment
Mandatory deliverables per assignment §11.1

\---

\---

# PART A — Reproducibility Instructions

Step-by-step guide to reproduce this project from a clean machine:
environment setup, dependency installation, data acquisition, and the
exact order to run the pipeline.

## A.1 Prerequisites

|Requirement|Notes|
|-|-|
|Python|Python 3.13.14|
|pip|Comes with Python|
|\~2 GB free disk|For raw CSVs + parquet + DuckDB warehouse|
|(Optional) Docker \& Docker Compose|Only needed for the containerized Jupyter environment — see A.6|

No GPU is required. VADER sentiment analysis runs on CPU by design (§9.1
of the report explains this trade-off).

## A.2 Project folder structure

```
Data\\\_Engineering\\\_Project/
├── data/
│   ├── raw/                          
│   │   ├── listings2.csv
│   │   ├── calendar.csv
│   │   ├── reviews2.csv
│   │   └── neighbourhoods.csv
│   ├── interim/                      
│   └── airbnb\\\\\\\\\\\\\\\_warehouse.duckdb       
├── docs/
│   └── data\\\\\\\\\\\\\\\_quality\\\\\\\\\\\\\\\_report.csv       
├── notebooks/
│   ├── 01\\\\\\\\\\\\\\\_dataset\\\\\\\\\\\\\\\_exploration.ipynb
│   ├── 02\\\\\\\\\\\\\\\_data\\\\\\\\\\\\\\\_engineering.ipynb
│   ├── 03\\\\\\\\\\\\\\\_eda.ipynb
│   ├── 04\\\\\\\\\\\\\\\_statistical\\\\\\\\\\\\\\\_analysis.ipynb
│   ├── 05\\\\\\\\\\\\\\\_data\\\\\\\\\\\\\\\_science.ipynb
│   └── 06\\\\\\\\\\\\\\\_ai\\\\\\\\\\\\\\\_nlp.ipynb
├── dashboard/
│   ├── app.py
│   ├── requirements.txt
│   ├── README.md
│   └── .streamlit/config.toml
├── docker-compose.yml
├── requirements.txt                  
└── PROJECt\_DOCUMENTATION.md   / Airbnb\_NYC\_Business\_Summary 

&#x20;    
```

## A.3 Get the data —  verified

1. [**insideairbnb.com/get-the-data**](https://insideairbnb.com/get-the-data/) → New York City, scrape date **14 June 2026**.
2. Download the **detailed** listings file (90 columns) and **detailed** reviews file (not the summary versions) — confirmed to match the shapes cited in report §3.
3. Extract into `data/raw/`, named: `listings2.csv`, `calendar.csv`, `reviews2.csv`, `neighbourhoods.csv`.

## A.4 Set up the Python environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\\\\\\\\\\\\\\\\Scripts\\\\\\\\\\\\\\\\activate
pip install -r requirements.txt
```

A pinned `requirements.txt` (generated via `pip freeze` after a
successful full run) is included in the submission, giving exact
package versions rather than open-ended minimums.

## A.5 Run the pipeline (exact order) —  verified end-to-end

|Step|Notebook|What it does|Produces|
|-|-|-|-|
|1|`01\\\\\\\\\\\\\\\_dataset\\\\\\\\\\\\\\\_exploration.ipynb`|Loads raw CSVs, inspects schema/shape/dtypes, checks missing values and duplicate keys (§2)|Notebook output only|
|2|`02\\\\\\\\\\\\\\\_data\\\\\\\\\\\\\\\_engineering.ipynb`|Ingests raw CSVs, profiles, cleans, deduplicates (fuzzy match), standardizes, enriches/joins, builds DuckDB star schema, writes silver parquet (§3.1–3.5)|`data/interim/\\\\\\\\\\\\\\\*\\\\\\\\\\\\\\\_silver.parquet`, `data/airbnb\\\\\\\\\\\\\\\_warehouse.duckdb`, `docs/data\\\\\\\\\\\\\\\_quality\\\\\\\\\\\\\\\_report.csv`|
|3|`03\\\\\\\\\\\\\\\_eda.ipynb`|Exploratory analysis, Figures 2–14|Notebook output only|
|4|`04\\\\\\\\\\\\\\\_statistical\\\\\\\\\\\\\\\_analysis.ipynb`|Hypothesis tests H1–H5, CIs, correlation/regression, LOWESS|Notebook output only|
|5|`05\\\\\\\\\\\\\\\_data\\\\\\\\\\\\\\\_science.ipynb`|Price prediction (3 models), SHAP, K-Means clustering|Notebook output only|
|6|`06\\\\\\\\\\\\\\\_ai\\\\\\\\\\\\\\\_nlp.ipynb`|VADER sentiment analysis|Notebook output only|

Notebooks `03`–`06` depend on `data/interim/\\\\\\\\\\\\\\\*\\\\\\\\\\\\\\\_silver.parquet`, which
only exists after `02` runs successfully — run in this order. This
full sequence has been run start-to-finish (`Kernel → Restart \\\\\\\\\\\\\\\& Run All` on each) and confirmed to reproduce the numbers in the report.

## A.6 (Optional) Run notebooks inside Docker instead

```bash
docker-compose up
```

Starts a Jupyter server at `http://localhost:8888` (token:
`airbnb2026`), with `notebooks/` and `data/` mounted as volumes.

> \\\\\\\\\\\\\\\*\\\\\\\\\\\\\\\*Status: base image confirmed to start; full dependency-install
> cycle inside the container not yet verified end-to-end.\\\\\\\\\\\\\\\*\\\\\\\\\\\\\\\* The
> compose file uses the generic `jupyter/scipy-notebook` image and
> does not pre-install project-specific packages (`duckdb`,
> `rapidfuzz`, `pingouin`, `xgboost`, `shap`, `vaderSentiment`) — these
> install via the notebooks' own `!pip install` cells once inside the
> container. This is disclosed honestly in the report (§5.6, §13)
> rather than claimed as fully tested.

## A.7 Run the Streamlit dashboard —  verified

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. The sidebar's "Data source" field
auto-detects the data folder (`../data/interim`, `./data/interim`,
`../data`, `./data`, in that order); if data lives elsewhere, type the
path in or use the upload boxes provided. If `vaderSentiment` fails to
install, every page works except **Reviews \& Sentiment**, which shows
a warning instead of crashing.

## A.8 Known environment sensitivities

* `random\\\\\\\\\\\\\\\_state=42` used throughout (train/test splits, KMeans init,
bootstrap resampling) — results should match closely, though
package-version differences (scikit-learn, xgboost) can cause small
numeric drift.
* Sentiment numbers are based on `sample(50000, random\\\\\\\\\\\\\\\_state=42)` — a
sample, not the full 990,170-review corpus.
* SHAP explainer construction can be slow on first run — expected, not
a hang.

\---

\---

# PART B — Assumptions Log

|#|Assumption|Why it was necessary|Where it matters|
|-|-|-|-|
|1|12 fully-missing columns dropped, not imputed|A 100%-missing column has no statistical basis for imputation|Report §3.2; notebook `02`|
|2|`host\\\\\\\\\\\\\\\_tenure\\\\\\\\\\\\\\\_years\\\\\\\\\\\\\\\_est` approximated from each host's earliest first-review date|`host\\\\\\\\\\\\\\\_since` is 100% missing; first review is the closest available proxy|Understates tenure for hosts with zero reviews — flagged in §5.3, §13|
|3|`maximum\\\\\\\\\\\\\\\_nights = 2,147,483,647` treated as a 32-bit integer overflow sentinel, nulled|Known scraper artifact, not a real value|Affects 5,210 calendar rows, up to 26 listings rows (§3.2)|
|4|Dominant `calendar\\\\\\\\\\\\\\\_minimum\\\\\\\\\\\\\\\_nights = 30` (22.45% of rows) treated as a genuine long-stay segment, not an outlier|Manual inspection showed this is a real host configuration pattern|Left in, discussed as a market signal (§6.5)|
|5|10,656 fuzzy-matched near-duplicates treated as likely legitimate distinct units, not auto-removed|Multi-unit buildings commonly have templated naming|Flagged as candidates only, not deleted (§3.2)|
|6|`price` treated as listed asking rate, not confirmed transaction price|No booking/payment data available from Inside Airbnb|All occupancy/revenue figures are estimates (§13)|
|7|296 calendar / 239 review "orphan" rows treated as scrape-timing artifacts, not pipeline defects|Listings can be delisted between scrapes of different files|Documented, not "fixed" (§3.1)|
|8|Sentiment analysis run on a 50,000-review random sample, not the full 990,170|Kept runtime tractable on CPU-only hardware|All sentiment stats are sample-based (§9.1)|

\---

\---

# PART C — Engineering \& Analytical Decisions Log

### Decision 1 — Warehouse engine: DuckDB vs. SQLite vs. PostgreSQL

**Chose:** DuckDB. **Why:** fast Parquet/pandas interop, columnar
performance for the 11M-row calendar table, no server process needed.
**Trade-off accepted:** less suited to concurrent multi-user production
workloads than PostgreSQL — acceptable for a single-analyst assignment.

### Decision 2 — Statistical test family

**Chose:** non-parametric tests (Mann-Whitney U, Kruskal-Wallis)
throughout. **Why:** Shapiro-Wilk rejected normality in every group
(p < 10⁻⁵⁴ in the worst case). **Trade-off accepted:** somewhat less
statistical power than parametric equivalents, but methodologically
correct given the data.

### Decision 3 — Sentiment model: VADER vs. transformer

**Chose:** VADER. **Why:** runs on CPU in minutes with no model
download, adequate for short informal review text. **Trade-off
accepted:** English-tuned lexicon likely under-scores non-English
reviews — disclosed, not hidden (§9.1, §13).

### Decision 4 — Price prediction model families

**Chose:** Linear Regression (baseline), Random Forest, XGBoost.
**Trade-off accepted:** XGBoost run with default hyperparameters, so it
underperformed Random Forest here — a tuning gap, not an inherent
weakness (§8.1, §14).

### Decision 5 — Cluster count (k) selection

**Chose:** silhouette score as primary criterion (peaked at k=5) since
the elbow curve was ambiguous. **Trade-off accepted:** k=5 is
supported, not the only defensible choice.

### Decision 6 — Feature leakage exclusions

**Chose:** excluded `estimated\\\\\\\\\\\\\\\_revenue`, `price\\\\\\\\\\\\\\\_per\\\\\\\\\\\\\\\_bedroom`,
`price\\\\\\\\\\\\\\\_quote\\\\\\\\\\\\\\\_total\\\\\\\\\\\\\\\_price`, `price\\\\\\\\\\\\\\\_quote\\\\\\\\\\\\\\\_price\\\\\\\\\\\\\\\_per\\\\\\\\\\\\\\\_night` (r = 0.522 to
1.000 with target) before modeling. **Why:** all are mathematically
derived from price; leaving them in would inflate accuracy artificially.

### Decision 7 — Scope: single city vs. multi-city

**Chose:** New York City only, in depth. **Why:** assignment's own
Design Philosophy explicitly values single-city depth over multi-city
breadth within a one-week window. **Trade-off accepted:** no
cross-city comparative insight — an explicit scope boundary, not a
late-discovered gap.

*(Add any further project-specific decisions not captured above.)*

\---

\---

# PART D — Summary: Completed Work

|Area|Status|Standard achieved|
|-|-|-|
|Dataset Familiarization (§2, Mandatory)|Complete|Full schema docs, entity relationships, business context, limitations|
|Data Engineering Challenges (§3.1–3.5, Recommended)|Complete|Ingestion, profiling, cleaning, enrichment, star schema, automated pipeline with logging + metadata|
|Exploratory Data Analysis (§4, Recommended)|Complete|Summary stats, geographic, temporal, host, and demand-side analysis, all with business interpretation|
|Statistical Analysis (§5.1–5.3, Recommended)|Complete|All 5 hypotheses tested with assumption checks, effect sizes, bootstrap CIs, regression + VIF + LOWESS|
|Price Prediction (§6.1, Optional)|Complete|3 models compared, cross-validated metrics, SHAP, residual analysis|
|Host \& Listing Segmentation (§6.3, Optional)|Complete|K-Means with elbow + silhouette validation, 5 profiled segments|
|NLP Sentiment Analysis (§7.1, partial)|Complete|VADER on 50K-review sample, correlated with ratings, limitations disclosed|
|Advanced \& Cloud-Native Topics (§3.6, Optional)|Design-level|Architecture, partitioning, CDC strategy at design level; docker-compose.yml provided, base image confirmed to run, full in-container dependency install not yet verified|
|Open Innovation Dashboard (§8, Optional)|Complete|8-section Streamlit dashboard, live filters, live price predictor, live cluster explorer|

\---

\---

# PART E — Summary: Incomplete Work

Honest disclosure of what wasn't attempted, and why — distinguishing
time pressure from genuine skill/knowledge gaps and other real
constraints, per the assignment's own emphasis on honest prioritization
(rubric: 15 points).

|Item|Reason(s)|
|-|-|
|**Demand \& Availability Forecasting (§6.2)**|**Time + knowledge.** Deprioritized within the one-week window in favor of the core pipeline → stats → ML → NLP chain. Also a genuine skill gap: no prior hands-on experience with Prophet or SARIMA, so doing this properly (rather than a shallow first attempt) would have needed learning time on top of implementation time.|
|**Model Generalization \& Bias testing beyond residual analysis (§6.4)**|**Knowledge + time.** A rigorous fairness/bias audit requires familiarity with fairness metrics (e.g. demographic parity, equalized odds) that wasn't confidently in hand; attempting it shallowly risked producing a misleading "audit" that looked more authoritative than it was, which felt worse than being upfront about not doing it.|
|**LLM-Powered Insight Generation / RAG / Q\&A interface (§7.2)**|**Time + knowledge.** No prior hands-on RAG/vector-store implementation experience; building one properly (chunking strategy, retrieval evaluation, prompt design) was judged to need more learning and iteration time than remained after prioritizing the dashboard and sentiment analysis.|
|**Recommendation \& Discovery Systems (§7.3)**|**Time + knowledge.** Collaborative/content-based filtering wasn't an area of prior practical experience; scoped out in favor of finishing fewer things well.|
|**Generative AI \& Agentic Experimentation (§7.4)**|**Time + strategic choice.** Deliberately traded off against the Streamlit dashboard, which was judged to better demonstrate product-building thinking with the skills already in hand, rather than attempting an agentic workflow shallowly.|
|**Topic Modeling / NER on reviews (§7.1 remainder)**|**Time + knowledge.** LDA/NMF/BERTopic and NER tooling (spaCy) weren't areas of prior hands-on use; sentiment analysis alone was prioritized for depth over spreading effort across multiple unfamiliar NLP techniques.|
|**Multi-City Comparisons (§5.4, §12)**|**Scope decision, not a gap.** Single-city depth was chosen deliberately per the assignment's own Design Philosophy — not something skipped due to time or skill.|
|**XGBoost hyperparameter tuning (§8.1)**|**Time only.** Default parameters used; this is a known, well-understood next step (GridSearch/Optuna), not a knowledge gap — simply not reached in the available time.|
|**Docker Compose full end-to-end verification (§3.6)**|**Time only.** The compose file itself was written and the base image confirmed to start; the full in-container dependency-install-and-run cycle wasn't tested before this submission. This is a quick, well-understood fix, not a skill gap.|
|**Cloud-native deployment (§5.6)**|**Access + scope.** No Azure subscription/budget was available for this assessment, and the assignment explicitly scopes cloud deployment as optional/design-level for a single-analyst, one-week submission — addressed as a reasoned design proposal instead.|

\---

