# NYC Airbnb Market Intelligence Dashboard

An interactive Streamlit dashboard built on top of the data pipeline from
`01_dataset_exploration.ipynb` → `06_ai_nlp.ipynb`. It's meant as the
**"Interactive Dashboard"** optional deliverable for the Expernetic
Data Engineer Intern assignment (§11.2).

It reads your gold-layer files (`listings_final2_silver.parquet`,
`calendar_silver.parquet`, `reviews_silver.parquet`) and gives you 8
interactive sections: Overview, Geographic Explorer, Pricing & Market,
Host Analysis, Statistical Insights (live hypothesis tests), a Price
Predictor (trains a Random Forest on the spot), Listing Segments
(K-Means clustering), and Reviews & Sentiment (VADER).

---

## 1. What is Streamlit, in 30 seconds

Streamlit turns a plain Python script into a web app. You write normal
Python; anywhere you call `st.something(...)` (a button, a slider, a
chart), that becomes a visual element in the browser. Every time someone
clicks a widget, Streamlit **re-runs the whole script top to bottom** —
that's the entire mental model. `app.py` is the whole app; there's no
separate frontend/backend to build.

You don't need to know anything else to run this.

---

## 2. Folder setup

Your notebooks load data with relative paths like `../data/interim/...`,
which means they expect a structure like this:

```
your_project/
├── data/
│   ├── raw/
│   └── interim/
│       ├── listings_final2_silver.parquet
│       ├── calendar_silver.parquet
│       ├── reviews_silver.parquet
│       └── neighbourhoods_silver.parquet
├── notebooks/
│   ├── 01_dataset_exploration.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_statistical_analysis.ipynb
│   ├── 05_data_science.ipynb
│   └── 06_ai_nlp.ipynb
└── dashboard/              <- put this folder here
    ├── app.py
    ├── requirements.txt
    ├── README.md
    └── .streamlit/config.toml
```

Drop this whole `dashboard/` folder as a **sibling** of `data/` and
`notebooks/` and the default path (`../data/interim`) will just work.

**If your data lives somewhere else**, you don't need to move anything —
just type the correct folder path into the "Data source" box in the
sidebar once the app is running, or use the file-upload boxes there
instead.

---

## 3. Install & run

Open a terminal in the `dashboard/` folder and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) and
should also open it automatically in your browser. Leave the terminal
running — closing it stops the app. To stop it manually, press `Ctrl+C`
in the terminal.

To restart after making changes: just save `app.py` — Streamlit will
show a "Rerun" prompt in the browser, or you can enable "Always rerun"
in the top-right menu.

### If `pip install` fails on `vaderSentiment`
It's only needed for the "Reviews & Sentiment" page. Every other page
works fine without it — you'll just see a friendly warning on that one
page instead of a crash.

---

## 4. Using the app

- **Sidebar → Data source**: confirm/change the folder path, or upload
  parquet/CSV files directly.
- **Sidebar → Filters**: borough, room type, and price range apply to
  every page except the Price Predictor and Listing Segments pages
  (those train on the full dataset for statistical validity, but the
  Predictor lets you pick any combination of inputs).
- **Sidebar → Navigate**: switch between the 8 sections.
- Every chart is interactive (Plotly) — hover for tooltips, drag to
  zoom, double-click to reset.

---

## 5. Deploying it so others can see it (optional, high-value)

The assignment mentions "deployed or locally runnable" — a local demo is
completely fine, but if you want a shareable link:

1. Push this `dashboard/` folder (plus a copy of the small parquet
   files, or a data-download step) to a public GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with
   GitHub, and point it at your repo + `app.py`.
3. It gives you a free public URL in a couple of minutes.

If your data files are too large to commit to GitHub (the reviews file
especially), consider hosting a smaller sample, or documenting in your
report that the app is designed to run locally against the full dataset.

---

## 6. Where this fits in your report

Reference it in **§11.2 Optional Deliverables** and **§8 Open Innovation
Challenge** of your report, and drop 2–3 screenshots (Overview, Geographic
Explorer, and Price Predictor tend to look best) into the **Visualizations**
section (§12, item 10) with captions. Mention it briefly in your
**Reflection** (§12, item 15) as evidence of "thinking like a product
builder, not just a task executor" — the assignment explicitly rewards that.
