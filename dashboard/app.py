"""
NYC Airbnb Market Intelligence Dashboard
==========================================
Built for the Expernetic Data Engineer Intern take-home assignment.

WHAT THIS FILE IS
------------------
This is a single-file Streamlit app. Streamlit turns a plain Python script
into a web app: every widget (st.selectbox, st.slider, etc.) you see below
renders as a control in the browser, and Streamlit re-runs this whole script
top-to-bottom every time someone interacts with a widget. That's it - there's
no separate frontend/backend to wire up.

Two ideas that make this fast despite re-running constantly:
  - @st.cache_data   -> caches the RETURN VALUE of a function (e.g. a loaded
                         DataFrame). If the inputs haven't changed, Streamlit
                         skips re-running the function and reuses the cached
                         result.
  - @st.cache_resource -> same idea, but for things that aren't plain data
                         (e.g. a trained ML model).

HOW TO RUN
----------
    pip install -r requirements.txt
    streamlit run app.py

See README.md for full setup instructions and where to put your data files.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# PAGE CONFIG - must be the first Streamlit command in the script
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="NYC Airbnb Market Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# A little bit of custom CSS to make the default Streamlit look less "default".
st.markdown("""
<style>
    .stMetric {
        background-color: rgba(28, 131, 225, 0.06);
        border: 1px solid rgba(28, 131, 225, 0.15);
        border-radius: 10px;
        padding: 12px 16px 6px 16px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; }
    h1, h2, h3 { font-weight: 700; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = "plotly_white"
ACCENT = "#1C83E1"


# ==============================================================================
# 1. DATA LOADING
# ==============================================================================
# Your notebooks write cleaned/enriched files to ../data/interim/ (relative to
# the notebooks folder). This app defaults to looking for a sibling "data"
# folder, but you can point it anywhere in the sidebar, or upload files
# directly if you're demoing this somewhere the raw files aren't available.

DEFAULT_CANDIDATE_DIRS = [
    "../data/interim",
    "./data/interim",
    "../data",
    "./data",
]


def _first_existing_dir(candidates):
    for c in candidates:
        if Path(c).exists():
            return c
    return candidates[0]


@st.cache_data(show_spinner="Loading listings data...")
def load_listings(data_dir: str):
    for fname in ["listings_final2_silver.parquet", "listings_silver.parquet"]:
        path = Path(data_dir) / fname
        if path.exists():
            df = pd.read_parquet(path)
            return df
    return None


@st.cache_data(show_spinner="Loading calendar data...")
def load_calendar(data_dir: str):
    path = Path(data_dir) / "calendar_silver.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
    return None


@st.cache_data(show_spinner="Loading reviews data...")
def load_reviews(data_dir: str):
    path = Path(data_dir) / "reviews_silver.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
    return None


def load_from_upload(uploaded_file):
    if uploaded_file is None:
        return None
    if uploaded_file.name.endswith(".parquet"):
        return pd.read_parquet(uploaded_file)
    return pd.read_csv(uploaded_file)


# ----------------------------------------------------------------------------
# Small helpers used throughout the app
# ----------------------------------------------------------------------------
def has_cols(df, cols):
    return all(c in df.columns for c in cols)


def fmt_money(x, decimals=0):
    if pd.isna(x):
        return "N/A"
    return f"${x:,.{decimals}f}"


def derive_host_segment(df):
    """Recreate the host-portfolio segmentation from notebook 03 (§4.4)."""
    host_scale = df.groupby("host_id")["id"].transform("count") if "id" in df.columns \
        else df.groupby("host_id")["host_id"].transform("count")

    def seg(n):
        if n == 1:
            return "Single listing"
        elif n <= 5:
            return "Small (2-5)"
        elif n <= 20:
            return "Medium (6-20)"
        else:
            return "Large/commercial (20+)"

    out = df.copy()
    out["host_scale"] = host_scale
    out["host_segment"] = out["host_scale"].apply(seg)
    return out


# ==============================================================================
# 2. SIDEBAR - data source + global filters + navigation
# ==============================================================================
st.sidebar.title("🏙️ Airbnb Intelligence")
st.sidebar.caption("Expernetic Technical Assessment · Data Engineer Intern")

with st.sidebar.expander("📁 Data source", expanded=False):
    default_dir = _first_existing_dir(DEFAULT_CANDIDATE_DIRS)
    data_dir = st.text_input(
        "Path to interim data folder",
        value=default_dir,
        help="Folder containing listings_final2_silver.parquet, "
             "calendar_silver.parquet, reviews_silver.parquet",
    )
    st.caption("Can't find your files? Upload them here instead:")
    up_listings = st.file_uploader("listings parquet/csv", type=["parquet", "csv"], key="up_l")
    up_calendar = st.file_uploader("calendar parquet/csv", type=["parquet", "csv"], key="up_c")
    up_reviews = st.file_uploader("reviews parquet/csv", type=["parquet", "csv"], key="up_r")

listings_raw = load_from_upload(up_listings) if up_listings else load_listings(data_dir)
calendar_raw = load_from_upload(up_calendar) if up_calendar else load_calendar(data_dir)
reviews_raw = load_from_upload(up_reviews) if up_reviews else load_reviews(data_dir)

if listings_raw is None:
    st.error(
        "Couldn't find `listings_final2_silver.parquet`. Set the correct folder "
        "path in the sidebar under **Data source**, or upload the file directly."
    )
    st.info(
        "Expected location (relative to this app, matching your notebooks): "
        "`../data/interim/listings_final2_silver.parquet`"
    )
    st.stop()

listings = derive_host_segment(listings_raw) if "host_id" in listings_raw.columns else listings_raw.copy()

# ---- Global filters -----------------------------------------------------
st.sidebar.markdown("### 🔎 Filters")

boroughs = sorted(listings["neighbourhood_group_cleansed"].dropna().unique()) \
    if "neighbourhood_group_cleansed" in listings.columns else []
sel_boroughs = st.sidebar.multiselect("Borough", boroughs, default=boroughs)

room_types = sorted(listings["room_type"].dropna().unique()) if "room_type" in listings.columns else []
sel_room_types = st.sidebar.multiselect("Room type", room_types, default=room_types)

if "price" in listings.columns:
    price_ceiling = int(np.nanpercentile(listings["price"], 99))
    price_range = st.sidebar.slider(
        "Price range ($/night)", 0, max(price_ceiling, 50), (0, price_ceiling)
    )
else:
    price_range = None

mask = pd.Series(True, index=listings.index)
if sel_boroughs:
    mask &= listings["neighbourhood_group_cleansed"].isin(sel_boroughs)
if sel_room_types:
    mask &= listings["room_type"].isin(sel_room_types)
if price_range:
    mask &= listings["price"].between(price_range[0], price_range[1]) | listings["price"].isna()

df = listings[mask].copy()

st.sidebar.caption(f"Showing **{len(df):,}** of **{len(listings):,}** listings")

st.sidebar.markdown("### 🧭 Navigate")
page = st.sidebar.radio(
    "Section",
    [
        "📊 Overview",
        "🗺️ Geographic Explorer",
        "💰 Pricing & Market",
        "🏠 Host Analysis",
        "📈 Statistical Insights",
        "🤖 Price Predictor",
        "🎯 Listing Segments",
        "💬 Reviews & Sentiment",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption("Built with Streamlit · Data: Inside Airbnb (NYC)")


# ==============================================================================
# 3. PAGES
# ==============================================================================

# ------------------------------------------------------------------ OVERVIEW
if page == "📊 Overview":
    st.title("📊 Market Overview")
    st.caption("A high-level snapshot of the current filtered market.")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Listings", f"{len(df):,}")
    c2.metric("Median price", fmt_money(df["price"].median()) if "price" in df else "N/A")
    if "occupancy_rate" in df.columns:
        c3.metric("Avg. occupancy", f"{df['occupancy_rate'].mean()*100:.1f}%")
    if "review_scores_rating" in df.columns:
        c4.metric("Avg. rating", f"{df['review_scores_rating'].mean():.2f} / 5")
    if "estimated_revenue" in df.columns:
        c5.metric("Total est. revenue", fmt_money(df["estimated_revenue"].sum()))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Price distribution")
        cap = df["price"].quantile(0.98) if "price" in df.columns else None
        fig = px.histogram(
            df[df["price"] <= cap] if cap else df, x="price", nbins=60,
            template=PLOTLY_TEMPLATE, color_discrete_sequence=[ACCENT],
        )
        fig.update_layout(bargap=0.05, height=380, xaxis_title="Price ($/night)", yaxis_title="Listings")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Room type mix")
        if "room_type" in df.columns:
            counts = df["room_type"].value_counts().reset_index()
            counts.columns = ["room_type", "count"]
            fig = px.pie(counts, names="room_type", values="count", hole=0.5,
                         template=PLOTLY_TEMPLATE)
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Listings by borough")
        if "neighbourhood_group_cleansed" in df.columns:
            bc = df["neighbourhood_group_cleansed"].value_counts().reset_index()
            bc.columns = ["borough", "count"]
            fig = px.bar(bc, x="borough", y="count", template=PLOTLY_TEMPLATE,
                         color="count", color_continuous_scale="Blues")
            fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Median price by borough")
        if has_cols(df, ["neighbourhood_group_cleansed", "price"]):
            bp = df.groupby("neighbourhood_group_cleansed")["price"].median().sort_values(ascending=False).reset_index()
            fig = px.bar(bp, x="neighbourhood_group_cleansed", y="price", template=PLOTLY_TEMPLATE,
                         color="price", color_continuous_scale="Oranges")
            fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False,
                               xaxis_title="", yaxis_title="Median price ($)")
            st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------- GEOGRAPHIC
elif page == "🗺️ Geographic Explorer":
    st.title("🗺️ Geographic Explorer")
    st.caption("Spatial distribution of price, ratings, and room types across the city.")

    if not has_cols(df, ["latitude", "longitude"]):
        st.warning("No latitude/longitude columns found in this dataset.")
    else:
        color_by = st.radio("Color map by", ["price", "review_scores_rating", "room_type"],
                             horizontal=True)
        plot_df = df.dropna(subset=["latitude", "longitude"]).copy()
        if len(plot_df) > 15000:
            plot_df = plot_df.sample(15000, random_state=42)

        if color_by == "price" and "price" in plot_df.columns:
            cap = plot_df["price"].quantile(0.95)
            plot_df["price_capped"] = plot_df["price"].clip(upper=cap)
            fig = px.scatter_mapbox(
                plot_df, lat="latitude", lon="longitude", color="price_capped",
                color_continuous_scale="Viridis", zoom=10, height=600,
                hover_data={"price": True, "room_type": True} if "room_type" in plot_df.columns else None,
            )
        elif color_by == "review_scores_rating" and color_by in plot_df.columns:
            fig = px.scatter_mapbox(
                plot_df, lat="latitude", lon="longitude", color="review_scores_rating",
                color_continuous_scale="RdYlGn", range_color=(3.5, 5.0), zoom=10, height=600,
            )
        else:
            fig = px.scatter_mapbox(
                plot_df, lat="latitude", lon="longitude", color="room_type", zoom=10, height=600,
            )
        fig.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Top neighbourhoods by listing volume")
    if has_cols(df, ["neighbourhood_cleansed", "neighbourhood_group_cleansed"]):
        nb = df.groupby(["neighbourhood_group_cleansed", "neighbourhood_cleansed"]).agg(
            listings=("neighbourhood_cleansed", "count"),
            median_price=("price", "median"),
            avg_rating=("review_scores_rating", "mean") if "review_scores_rating" in df.columns else ("neighbourhood_cleansed", "count"),
        ).reset_index().sort_values("listings", ascending=False).head(15)
        st.dataframe(nb, use_container_width=True, hide_index=True)


# --------------------------------------------------------------- PRICING
elif page == "💰 Pricing & Market":
    st.title("💰 Pricing & Market Analysis")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Price by room type")
        if has_cols(df, ["room_type", "price"]):
            fig = px.box(df, x="room_type", y="price", template=PLOTLY_TEMPLATE, color="room_type")
            fig.update_layout(showlegend=False, yaxis_range=[0, df["price"].quantile(0.95)])
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Price by property type")
        if has_cols(df, ["property_type_group", "price"]):
            fig = px.box(df, x="property_type_group", y="price", template=PLOTLY_TEMPLATE,
                         color="property_type_group")
            fig.update_layout(showlegend=False, yaxis_range=[0, df["price"].quantile(0.95)])
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("What drives price? (correlation matrix)")
    numeric_candidates = [
        "price", "accommodates", "bedrooms", "bathrooms", "minimum_nights",
        "availability_365", "number_of_reviews", "review_scores_rating",
        "occupancy_rate", "host_tenure_years_est", "review_frequency_per_month",
    ]
    numeric_cols = [c for c in numeric_candidates if c in df.columns]
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                         template=PLOTLY_TEMPLATE, aspect="auto")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        if "price" in corr.columns:
            top_driver = corr["price"].drop("price").abs().idxmax()
            st.info(f"💡 **{top_driver}** has the strongest linear relationship with price "
                    f"(r = {corr['price'][top_driver]:.2f}) in the current filtered selection.")

    st.divider()
    st.subheader("Price vs. distance from city centre")
    if has_cols(df, ["latitude", "longitude", "price"]):
        center_lat, center_lon = 40.7549, -73.9840
        tmp = df.dropna(subset=["latitude", "longitude", "price"]).copy()
        tmp["dist_from_center_km"] = np.sqrt(
            (tmp["latitude"] - center_lat) ** 2 + (tmp["longitude"] - center_lon) ** 2
        ) * 111
        if len(tmp) > 8000:
            tmp = tmp.sample(8000, random_state=42)
        fig = px.scatter(tmp, x="dist_from_center_km", y="price", opacity=0.3,
                          template=PLOTLY_TEMPLATE, trendline="lowess",
                          labels={"dist_from_center_km": "Distance from city centre (km)"})
        fig.update_layout(yaxis_range=[0, tmp["price"].quantile(0.95)])
        st.plotly_chart(fig, use_container_width=True)
        corr_val = tmp[["dist_from_center_km", "price"]].corr().iloc[0, 1]
        direction = "decreases" if corr_val < 0 else "increases"
        st.caption(f"Correlation: {corr_val:.3f} — price tends to {direction} moving away from the centre. "
                   "**Business read:** this quantifies the location premium and can anchor a "
                   "distance-based pricing recommendation for hosts.")


# ---------------------------------------------------------------- HOSTS
elif page == "🏠 Host Analysis":
    st.title("🏠 Host & Supply-Side Analysis")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Host portfolio segments")
        seg_order = ["Single listing", "Small (2-5)", "Medium (6-20)", "Large/commercial (20+)"]
        seg = df.groupby("host_segment").agg(
            listings=("host_segment", "count"),
            unique_hosts=("host_id", "nunique"),
            median_price=("price", "median") if "price" in df.columns else ("host_segment", "count"),
        ).reindex(seg_order).dropna(how="all").reset_index()
        st.dataframe(seg, use_container_width=True, hide_index=True)

        fig = px.bar(seg, x="host_segment", y="listings", template=PLOTLY_TEMPLATE,
                     category_orders={"host_segment": seg_order}, color="host_segment")
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Market concentration")
        host_counts = df.groupby("host_id").size().sort_values(ascending=False)
        cum_listings_pct = (host_counts.cumsum() / host_counts.sum() * 100)
        cum_hosts_pct = (np.arange(1, len(host_counts) + 1) / len(host_counts) * 100)
        lorenz = pd.DataFrame({"cum_hosts_pct": cum_hosts_pct, "cum_listings_pct": cum_listings_pct.values})
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=lorenz["cum_hosts_pct"], y=lorenz["cum_listings_pct"],
                                  mode="lines", name="Actual", line=dict(color=ACCENT, width=3)))
        fig.add_trace(go.Scatter(x=[0, 100], y=[0, 100], mode="lines", name="Perfect equality",
                                  line=dict(color="lightgray", dash="dash")))
        fig.update_layout(template=PLOTLY_TEMPLATE, height=350,
                           xaxis_title="Cumulative % of hosts", yaxis_title="Cumulative % of listings")
        st.plotly_chart(fig, use_container_width=True)

        hosts_for_50pct = (cum_listings_pct <= 50).sum()
        pct_of_hosts = hosts_for_50pct / len(host_counts) * 100
        st.info(f"💡 Just **{pct_of_hosts:.1f}%** of hosts ({hosts_for_50pct:,} hosts) control "
                f"**50%** of all listings in the current selection — a strong signal of "
                f"commercial/professional supply concentration.")

    st.divider()
    if "host_is_superhost" in df.columns:
        st.subheader("Superhost vs. non-superhost performance")
        agg_dict = {"listings": ("host_is_superhost", "count")}
        if "price" in df.columns:
            agg_dict["median_price"] = ("price", "median")
        if "occupancy_rate" in df.columns:
            agg_dict["avg_occupancy"] = ("occupancy_rate", "mean")
        if "review_scores_rating" in df.columns:
            agg_dict["avg_rating"] = ("review_scores_rating", "mean")
        sh = df.groupby("host_is_superhost").agg(**agg_dict).reset_index()
        sh["host_is_superhost"] = sh["host_is_superhost"].map({"t": "Superhost", "f": "Non-superhost", True: "Superhost", False: "Non-superhost"}).fillna(sh["host_is_superhost"])
        st.dataframe(sh, use_container_width=True, hide_index=True)


# -------------------------------------------------------- STATS INSIGHTS
elif page == "📈 Statistical Insights":
    st.title("📈 Statistical Insights")
    st.caption("Hypothesis tests recomputed live against the current filtered selection "
               "(mirrors §5.1 of the assignment report).")

    from scipy import stats as sstats

    def rank_biserial(u, n1, n2):
        return 1 - (2 * u) / (n1 * n2)

    tests_run = 0

    # H1: Entire-home vs private room price
    if has_cols(df, ["room_type", "price"]):
        entire = df.loc[df["room_type"] == "Entire home/apt", "price"].dropna()
        private = df.loc[df["room_type"] == "Private room", "price"].dropna()
        if len(entire) > 5 and len(private) > 5:
            u, p = sstats.mannwhitneyu(entire, private, alternative="greater")
            eff = rank_biserial(u, len(entire), len(private))
            with st.container(border=True):
                st.markdown("**H1 — Entire-home listings command higher prices than private rooms**")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Median (entire)", fmt_money(entire.median()))
                c2.metric("Median (private)", fmt_money(private.median()))
                c3.metric("p-value", f"{p:.4g}")
                c4.metric("Effect size (r)", f"{eff:.3f}")
                verdict = "✅ Statistically significant" if p < 0.05 else "❌ Not significant"
                st.caption(f"Mann-Whitney U test · {verdict} at α=0.05. "
                           "**Business read:** confirms room type is a primary price lever for revenue strategy.")
            tests_run += 1

    # H2: Superhost review scores
    if has_cols(df, ["host_is_superhost", "review_scores_rating"]):
        sh = df.loc[df["host_is_superhost"].isin(["t", True]), "review_scores_rating"].dropna()
        nsh = df.loc[df["host_is_superhost"].isin(["f", False]), "review_scores_rating"].dropna()
        if len(sh) > 5 and len(nsh) > 5:
            u, p = sstats.mannwhitneyu(sh, nsh, alternative="greater")
            eff = rank_biserial(u, len(sh), len(nsh))
            with st.container(border=True):
                st.markdown("**H2 — Superhosts achieve higher review scores**")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Median (superhost)", f"{sh.median():.2f}")
                c2.metric("Median (non-superhost)", f"{nsh.median():.2f}")
                c3.metric("p-value", f"{p:.4g}")
                c4.metric("Effect size (r)", f"{eff:.3f}")
                verdict = "✅ Statistically significant" if p < 0.05 else "❌ Not significant"
                st.caption(f"Mann-Whitney U test · {verdict} at α=0.05. "
                           "**Business read:** supports promoting/incentivizing the Superhost program.")
            tests_run += 1

    # H4: ANOVA / Kruskal-Wallis across boroughs
    if has_cols(df, ["neighbourhood_group_cleansed", "price"]):
        groups = [g.dropna() for _, g in df.groupby("neighbourhood_group_cleansed")["price"]]
        groups = [g for g in groups if len(g) > 5]
        if len(groups) >= 2:
            h, p = sstats.kruskal(*groups)
            n_total = sum(len(g) for g in groups)
            k = len(groups)
            eps_sq = (h - k + 1) / (n_total - k) if n_total > k else np.nan
            with st.container(border=True):
                st.markdown("**H4 — Neighbourhood (borough) average prices differ significantly**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Kruskal-Wallis H", f"{h:.1f}")
                c2.metric("p-value", f"{p:.4g}")
                c3.metric("Effect size (ε²)", f"{eps_sq:.3f}" if not np.isnan(eps_sq) else "N/A")
                verdict = "✅ Statistically significant" if p < 0.05 else "❌ Not significant"
                st.caption(f"Kruskal-Wallis H-test · {verdict} at α=0.05. "
                           "**Business read:** location-based pricing tiers are statistically justified.")
            tests_run += 1

    # H5: Weekend vs weekday booking rate (needs calendar)
    if calendar_raw is not None and has_cols(calendar_raw, ["date", "available"]):
        cal = calendar_raw.copy()
        if "listing_id" in cal.columns and "id" in df.columns:
            cal = cal[cal["listing_id"].isin(df["id"])]
        cal["is_weekend"] = cal["date"].dt.dayofweek.isin([5, 6])
        cal["is_booked"] = cal["available"].astype(str).str.lower() == "f"
        wknd = cal.loc[cal["is_weekend"], "is_booked"]
        wkdy = cal.loc[~cal["is_weekend"], "is_booked"]
        if len(wknd) > 30 and len(wkdy) > 30:
            from statsmodels.stats.proportion import proportions_ztest
            count = [wknd.sum(), wkdy.sum()]
            nobs = [len(wknd), len(wkdy)]
            z, p = proportions_ztest(count, nobs)
            with st.container(border=True):
                st.markdown("**H5 — Weekend vs. weekday booking rates differ significantly**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Weekend booked rate", f"{wknd.mean()*100:.1f}%")
                c2.metric("Weekday booked rate", f"{wkdy.mean()*100:.1f}%")
                c3.metric("p-value", f"{p:.4g}")
                verdict = "✅ Statistically significant" if p < 0.05 else "❌ Not significant"
                st.caption(f"Two-proportion z-test · {verdict} at α=0.05. "
                           "**Business read:** informs whether weekend pricing premiums are warranted.")
            tests_run += 1
    else:
        st.caption("ℹ️ Load calendar data (sidebar) to see the weekend vs. weekday booking test (H5).")

    if tests_run == 0:
        st.warning("Not enough data in the current filter selection to run these tests. Try widening your filters.")


# -------------------------------------------------------- PRICE PREDICTOR
elif page == "🤖 Price Predictor":
    st.title("🤖 Price Predictor")
    st.caption("A Random Forest model trained live on the filtered listings — mirrors §6.1 of the assignment. "
               "Adjust listing attributes below and see the estimated nightly price.")

    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, r2_score

    feature_cols = [
        "accommodates", "bedrooms", "bathrooms", "minimum_nights", "availability_365",
        "review_scores_rating", "number_of_reviews", "room_type", "property_type_group",
        "neighbourhood_group_cleansed", "host_is_superhost", "host_tenure_years_est",
    ]
    available_features = [c for c in feature_cols if c in listings.columns]
    missing_features = [c for c in feature_cols if c not in listings.columns]

    @st.cache_resource(show_spinner="Training price prediction model...")
    def train_price_model(data_hash, feature_set):
        ml_df = listings[feature_set + ["price"]].dropna()
        cat_cols = [c for c in ["room_type", "property_type_group",
                                 "neighbourhood_group_cleansed", "host_is_superhost"] if c in feature_set]
        ml_encoded = pd.get_dummies(ml_df, columns=cat_cols, drop_first=True)
        X = ml_encoded.drop(columns=["price"])
        y = ml_encoded["price"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        return model, list(X.columns), mae, r2

    if len(available_features) < 4:
        st.warning(f"Not enough feature columns available to train a model. Missing: {missing_features}")
    else:
        if missing_features:
            st.caption(f"ℹ️ Training without unavailable columns: {missing_features}")

        model, model_columns, mae, r2 = train_price_model(len(listings), tuple(available_features))

        c1, c2 = st.columns(2)
        c1.metric("Model MAE (test set)", fmt_money(mae))
        c2.metric("Model R²", f"{r2:.3f}")
        st.caption("Trained on Random Forest (200 trees, max depth 10) using an 80/20 train/test split — "
                   "same configuration as the notebook experiment.")

        st.divider()
        st.subheader("Try it: estimate a listing's price")

        input_row = {}
        cols = st.columns(3)
        i = 0
        for feat in available_features:
            col = cols[i % 3]
            i += 1
            if feat in ["room_type", "property_type_group", "neighbourhood_group_cleansed"]:
                options = sorted(listings[feat].dropna().unique())
                input_row[feat] = col.selectbox(feat.replace("_", " ").title(), options)
            elif feat == "host_is_superhost":
                choice = col.selectbox("Superhost?", ["No", "Yes"])
                input_row[feat] = "t" if choice == "Yes" else "f"
            else:
                series = listings[feat].dropna()
                default = float(series.median())
                lo, hi = float(series.quantile(0.01)), float(series.quantile(0.99))
                input_row[feat] = col.slider(feat.replace("_", " ").title(), min_value=float(min(lo, default)),
                                              max_value=float(max(hi, default) + 1), value=default)

        if st.button("Predict price", type="primary"):
            input_df = pd.DataFrame([input_row])
            cat_cols = [c for c in ["room_type", "property_type_group",
                                     "neighbourhood_group_cleansed", "host_is_superhost"] if c in available_features]
            input_encoded = pd.get_dummies(input_df, columns=cat_cols, drop_first=True)
            input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)
            pred = model.predict(input_encoded)[0]
            st.success(f"### Estimated price: {fmt_money(pred, 0)} / night")
            st.caption(f"± ~{fmt_money(mae, 0)} typical error based on hold-out validation.")

        st.divider()
        st.subheader("What drives this model's predictions?")
        importances = pd.Series(model.feature_importances_, index=model_columns).sort_values(ascending=False).head(12)
        fig = px.bar(importances[::-1], orientation="h", template=PLOTLY_TEMPLATE,
                     labels={"value": "Importance", "index": ""}, color=importances[::-1],
                     color_continuous_scale="Blues")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=420)
        st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------- LISTING SEGMENTS
elif page == "🎯 Listing Segments":
    st.title("🎯 Listing Segments (Clustering)")
    st.caption("K-Means clustering (k=5) on price/size/performance features — mirrors §6.3 of the assignment.")

    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans

    cluster_features = ["price", "accommodates", "bedrooms", "bathrooms",
                         "occupancy_rate", "review_scores_rating", "availability_365"]
    available_cf = [c for c in cluster_features if c in listings.columns]

    if len(available_cf) < 4:
        st.warning("Not enough numeric columns available for clustering.")
    else:
        k = st.slider("Number of clusters (k)", 2, 8, 5)

        @st.cache_data(show_spinner="Fitting clusters...")
        def fit_clusters(feature_set, k):
            cdf = listings[feature_set].dropna()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(cdf)
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            cdf = cdf.copy()
            cdf["cluster"] = km.fit_predict(X_scaled)
            return cdf

        cdf = fit_clusters(tuple(available_cf), k)

        agg_dict = {c: (c, "mean") for c in available_cf}
        profile = cdf.groupby("cluster").agg(n=("cluster", "count"), **agg_dict).reset_index()
        profile = profile.round(2)
        st.subheader("Cluster profiles")
        st.dataframe(profile, use_container_width=True, hide_index=True)

        st.subheader("Visualize clusters")
        xax = st.selectbox("X axis", available_cf, index=available_cf.index("price") if "price" in available_cf else 0)
        yax = st.selectbox("Y axis", available_cf,
                            index=available_cf.index("occupancy_rate") if "occupancy_rate" in available_cf else 1)
        plot_df = cdf.copy()
        if len(plot_df) > 10000:
            plot_df = plot_df.sample(10000, random_state=42)
        fig = px.scatter(plot_df, x=xax, y=yax, color=plot_df["cluster"].astype(str),
                          template=PLOTLY_TEMPLATE, opacity=0.5,
                          labels={"color": "Cluster"})
        st.plotly_chart(fig, use_container_width=True)

        st.info("💡 **Business read:** each cluster represents a distinct market segment (e.g., "
                "budget/high-occupancy vs. premium/low-occupancy) — useful for targeted host "
                "coaching, dynamic pricing tiers, or investor guidance on which segment to enter.")


# -------------------------------------------------------- REVIEWS/SENTIMENT
elif page == "💬 Reviews & Sentiment":
    st.title("💬 Reviews & Sentiment")
    st.caption("VADER sentiment analysis on guest review text, correlated with numerical ratings — "
               "mirrors §7.1 of the assignment.")

    if reviews_raw is None:
        st.warning("Reviews data not loaded. Add `reviews_silver.parquet` via the sidebar Data source panel.")
    else:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            vader_available = True
        except ImportError:
            vader_available = False
            st.error("`vaderSentiment` isn't installed. Run: `pip install vaderSentiment`")

        if vader_available:
            sample_size = st.slider("Sample size (larger = slower, more accurate)", 2000, 50000, 15000, step=1000)

            @st.cache_data(show_spinner="Running sentiment analysis on a sample of reviews...")
            def run_sentiment(n):
                analyzer = SentimentIntensityAnalyzer()
                sample = reviews_raw.dropna(subset=["comments"]).sample(
                    min(n, len(reviews_raw)), random_state=42
                ).copy()
                sample["sentiment"] = sample["comments"].apply(
                    lambda t: analyzer.polarity_scores(str(t))["compound"]
                )
                return sample

            sample_reviews = run_sentiment(sample_size)

            c1, c2, c3 = st.columns(3)
            c1.metric("Reviews analyzed", f"{len(sample_reviews):,}")
            c2.metric("Avg. sentiment", f"{sample_reviews['sentiment'].mean():.3f}")
            c3.metric("% positive (>0.5)", f"{(sample_reviews['sentiment'] > 0.5).mean()*100:.1f}%")

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Sentiment distribution")
                fig = px.histogram(sample_reviews, x="sentiment", nbins=40, template=PLOTLY_TEMPLATE,
                                    color_discrete_sequence=[ACCENT])
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Sentiment vs. numerical rating")
                if has_cols(listings, ["id", "review_scores_rating"]):
                    sent_by_listing = sample_reviews.groupby("listing_id")["sentiment"].mean().reset_index()
                    sent_by_listing.columns = ["id", "avg_sentiment"]
                    merged = listings[["id", "review_scores_rating"]].merge(sent_by_listing, on="id", how="inner")
                    if len(merged) > 3:
                        corr = merged[["avg_sentiment", "review_scores_rating"]].corr().iloc[0, 1]
                        fig = px.scatter(merged, x="avg_sentiment", y="review_scores_rating",
                                          template=PLOTLY_TEMPLATE, opacity=0.4, trendline="ols")
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption(f"Correlation: **{corr:.3f}** — text sentiment and star ratings only "
                                   "partially agree, meaning review text captures nuance the numeric "
                                   "score misses.")

            st.divider()
            st.subheader("Reviews where text sentiment disagrees with a high star rating")
            if has_cols(listings, ["id", "review_scores_rating"]):
                merged_text = sample_reviews.merge(
                    listings[["id", "review_scores_rating"]], left_on="listing_id", right_on="id"
                )
                mismatch = merged_text[
                    (merged_text["sentiment"] < 0.3) & (merged_text["review_scores_rating"] >= 4.8)
                ][["comments", "sentiment", "review_scores_rating"]]
                st.caption(f"Found **{len(mismatch):,}** such reviews in this sample — often short, "
                           "neutral-toned, non-English, or purely factual comments rather than negative ones.")
                st.dataframe(mismatch.head(10), use_container_width=True, hide_index=True)
