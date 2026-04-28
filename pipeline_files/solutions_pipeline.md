# load.py

```
import os
import time
import logging
from datetime import timedelta

import requests
import pandas as pd
import yfinance as yf
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv


# --------------------------------------------------
# Setup
# --------------------------------------------------

load_dotenv()

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/load.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

MAG7 = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "AMZN": "0001018724",
    "GOOGL": "0001652044",
    "META": "0001326801",
    "NVDA": "0001045810",
    "TSLA": "0001318605",
}

RETURN_HORIZONS = [1, 3, 5, 10]
NUM_QUARTERS = 44


# --------------------------------------------------
# MongoDB connection
# --------------------------------------------------

def get_mongo_collection():
    """Connects to MongoDB Atlas and returns the target collection."""
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB")
    collection_name = os.getenv("MONGO_COLLECTION")

    if not mongo_uri:
        raise ValueError("MONGO_URI is missing from .env file")

    client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
    db = client[db_name]
    return db[collection_name]


# --------------------------------------------------
# SEC financial statement data
# --------------------------------------------------

def get_sec_company_facts(cik):
    """Pulls company facts JSON from the SEC API for a given CIK."""
    user_agent = os.getenv("SEC_USER_AGENT", "Dylan Hill dylan@example.com")

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {"User-Agent": user_agent}

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    time.sleep(0.2)

    return response.json()


def get_clean_quarterly_metric(data, tags, output_col_name):
    """Extracts clean quarterly values for one financial metric from SEC XBRL facts."""
    all_facts = []

    for tag in tags:
        if tag in data["facts"]["us-gaap"]:
            facts = data["facts"]["us-gaap"][tag]["units"]["USD"]
            temp = pd.DataFrame(facts)
            temp["tag_used"] = tag
            all_facts.append(temp)

    if not all_facts:
        logging.warning(f"No data found for {output_col_name}")
        return pd.DataFrame()

    df = pd.concat(all_facts, ignore_index=True)
    df = df[df["form"].isin(["10-Q", "10-K"])].copy()

    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    df["filed"] = pd.to_datetime(df["filed"])
    df["duration_days"] = (df["end"] - df["start"]).dt.days
    df["filing_lag_days"] = (df["filed"] - df["end"]).dt.days

    df = df.rename(columns={
        "fy": "fiscal_year",
        "fp": "fiscal_period",
        "val": output_col_name,
        "end": "period_end_date",
        "filed": "filing_date"
    })

    quarterly_10q = df[
        (df["form"] == "10-Q") &
        (df["fiscal_period"].isin(["Q1", "Q2", "Q3"])) &
        (df["duration_days"].between(70, 110)) &
        (df["filing_lag_days"].between(0, 80))
    ].copy()

    quarterly_10q = quarterly_10q.sort_values("filing_date").drop_duplicates(
        subset=["fiscal_year", "fiscal_period"],
        keep="last"
    )

    annual_10k = df[
        (df["form"] == "10-K") &
        (df["fiscal_period"] == "FY") &
        (df["duration_days"].between(330, 380)) &
        (df["filing_lag_days"].between(0, 120))
    ].copy()

    annual_10k = annual_10k.sort_values("filing_date").drop_duplicates(
        subset=["fiscal_year"],
        keep="last"
    )

    q4_records = []

    for year in annual_10k["fiscal_year"].unique():
        q1_q3 = quarterly_10q[
            (quarterly_10q["fiscal_year"] == year) &
            (quarterly_10q["fiscal_period"].isin(["Q1", "Q2", "Q3"]))
        ]

        if len(q1_q3) == 3:
            fy_row = annual_10k[annual_10k["fiscal_year"] == year].iloc[0]
            q4_value = fy_row[output_col_name] - q1_q3[output_col_name].sum()

            q4_records.append({
                "fiscal_year": year,
                "fiscal_period": "Q4",
                "period_end_date": fy_row["period_end_date"],
                "filing_date": fy_row["filing_date"],
                output_col_name: q4_value,
            })

    q4_df = pd.DataFrame(q4_records)

    clean = pd.concat([
        quarterly_10q[[
            "fiscal_year",
            "fiscal_period",
            "period_end_date",
            "filing_date",
            output_col_name
        ]],
        q4_df
    ], ignore_index=True)

    return clean.sort_values(
        "filing_date",
        ascending=False
    ).reset_index(drop=True)


def get_financials_for_ticker(cik):
    """Builds quarterly financial metrics for one company."""
    data = get_sec_company_facts(cik)

    revenue = get_clean_quarterly_metric(
        data,
        [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet"
        ],
        "actual_revenue"
    )

    net_income = get_clean_quarterly_metric(
        data,
        ["NetIncomeLoss"],
        "actual_net_income"
    )

    operating_income = get_clean_quarterly_metric(
        data,
        ["OperatingIncomeLoss"],
        "actual_operating_income"
    )

    financials = revenue.copy()

    for metric_df, col in [
        (net_income, "actual_net_income"),
        (operating_income, "actual_operating_income")
    ]:
        if not metric_df.empty:
            financials = financials.merge(
                metric_df[["fiscal_year", "fiscal_period", col]],
                on=["fiscal_year", "fiscal_period"],
                how="left"
            )

    financials = financials.sort_values(["fiscal_year", "fiscal_period"])

    # Absolute quarter-over-quarter and year-over-year changes
    financials["revenue_diff_qoq"] = financials["actual_revenue"].diff()
    financials["revenue_diff_yoy"] = financials["actual_revenue"].diff(4)

    financials["net_income_diff_qoq"] = financials["actual_net_income"].diff()
    financials["net_income_diff_yoy"] = financials["actual_net_income"].diff(4)

    financials["operating_income_diff_qoq"] = financials["actual_operating_income"].diff()
    financials["operating_income_diff_yoy"] = financials["actual_operating_income"].diff(4)

    # Percentage quarter-over-quarter and year-over-year changes
    financials["revenue_growth_qoq_pct"] = financials["actual_revenue"].pct_change()
    financials["revenue_growth_yoy_pct"] = financials["actual_revenue"].pct_change(4)

    financials["net_income_growth_qoq_pct"] = financials["actual_net_income"].pct_change()
    financials["net_income_growth_yoy_pct"] = financials["actual_net_income"].pct_change(4)

    financials["operating_income_growth_qoq_pct"] = financials["actual_operating_income"].pct_change()
    financials["operating_income_growth_yoy_pct"] = financials["actual_operating_income"].pct_change(4)

    # Profitability ratio
    financials["net_income_margin"] = (
        financials["actual_net_income"] / financials["actual_revenue"]
    )

    financials = financials.sort_values(
        "filing_date",
        ascending=False
    ).head(NUM_QUARTERS)

    return financials.reset_index(drop=True)


# --------------------------------------------------
# Yahoo Finance earnings and price data
# --------------------------------------------------

def get_earnings_dates(ticker_symbol):
    """Pulls historical earnings dates and EPS fields from Yahoo Finance."""
    ticker = yf.Ticker(ticker_symbol)

    earnings = ticker.get_earnings_dates(limit=60).reset_index()

    earnings = earnings.rename(columns={earnings.columns[0]: "earnings_date"})
    earnings["earnings_date"] = pd.to_datetime(
        earnings["earnings_date"]
    ).dt.tz_localize(None)

    earnings = earnings.dropna(subset=["Reported EPS"])
    earnings = earnings[earnings["earnings_date"] <= pd.Timestamp.today()]
    earnings = earnings.sort_values("earnings_date").reset_index(drop=True)

    return earnings


def get_price_history(ticker_symbol, start_date, end_date):
    """Pulls daily stock price history from Yahoo Finance."""
    prices = yf.download(
        ticker_symbol,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False
    )

    if isinstance(prices.columns, pd.MultiIndex):
        prices.columns = prices.columns.get_level_values(0)

    prices = prices.reset_index()

    prices["Date"] = pd.to_datetime(prices["Date"]).dt.tz_localize(None)
    prices["daily_return"] = prices["Adj Close"].pct_change()

    return prices


def get_price_features(prices, earnings_date, horizon):
    """Calculates momentum, volatility, and post-earnings return for one event."""
    prior = prices[prices["Date"] < earnings_date].copy()
    after = prices[prices["Date"] > earnings_date].copy()

    if len(prior) < 30 or len(after) < horizon:
        return None

    price_t_minus_1 = float(prior.iloc[-1]["Adj Close"])
    price_t_minus_10 = float(prior.iloc[-10]["Adj Close"])
    price_t_minus_30 = float(prior.iloc[-30]["Adj Close"])
    price_t_plus_h = float(after.iloc[horizon - 1]["Adj Close"])

    return {
        "momentum_10d": float((price_t_minus_1 / price_t_minus_10) - 1),
        "momentum_30d": float((price_t_minus_1 / price_t_minus_30) - 1),
        "volatility_10d": float(prior.iloc[-10:]["daily_return"].std()),
        "volatility_30d": float(prior.iloc[-30:]["daily_return"].std()),
        "return_horizon": int(horizon),
        "post_earnings_return": float((price_t_plus_h / price_t_minus_1) - 1),
    }


# --------------------------------------------------
# Document creation
# --------------------------------------------------

def build_documents_for_ticker(ticker_symbol, cik):
    """Creates MongoDB-ready documents for one ticker."""
    logging.info(f"Building documents for {ticker_symbol}")

    financials = get_financials_for_ticker(cik)
    earnings = get_earnings_dates(ticker_symbol)

    print(f"\n--- {ticker_symbol} ---")
    print("Financial rows before merge:", len(financials))
    print("Earnings rows:", len(earnings))

    if financials.empty or earnings.empty:
        logging.warning(f"Missing financials or earnings for {ticker_symbol}")
        return []

    financials = financials.sort_values("filing_date")
    earnings = earnings.sort_values("earnings_date")

    earnings["earnings_date"] = earnings["earnings_date"].dt.normalize()
    financials["filing_date"] = pd.to_datetime(financials["filing_date"]).dt.normalize()

    financials = pd.merge_asof(
        financials,
        earnings,
        left_on="filing_date",
        right_on="earnings_date",
        direction="nearest",
        tolerance=pd.Timedelta(days=30)
    )

    financials = financials.dropna(subset=["earnings_date"])

    print("Rows after merge:", len(financials))
    logging.info(f"{ticker_symbol}: rows after earnings merge = {len(financials)}")

    if financials.empty:
        logging.warning(f"No matched earnings/financial rows for {ticker_symbol}")
        return []

    start_date = financials["earnings_date"].min() - timedelta(days=90)
    end_date = financials["earnings_date"].max() + timedelta(days=30)

    prices = get_price_history(ticker_symbol, start_date, end_date)

    documents = []

    for _, row in financials.iterrows():
        for horizon in RETURN_HORIZONS:
            price_features = get_price_features(
                prices,
                row["earnings_date"],
                horizon
            )

            if price_features is None:
                continue

            doc = {
                "ticker": ticker_symbol,
                "earnings_date": row["earnings_date"].strftime("%Y-%m-%d"),
                "filing_date": row["filing_date"].strftime("%Y-%m-%d"),
                "fiscal_year": int(row["fiscal_year"]),
                "fiscal_period": row["fiscal_period"],

                "actual_eps": row.get("Reported EPS", None),
                "estimated_eps": row.get("EPS Estimate", None),
                "eps_surprise_pct": row.get("Surprise(%)", None),

                "actual_revenue": row.get("actual_revenue", None),
                "revenue_diff_qoq": row.get("revenue_diff_qoq", None),
                "revenue_diff_yoy": row.get("revenue_diff_yoy", None),
                "revenue_growth_qoq_pct": row.get("revenue_growth_qoq_pct", None),
                "revenue_growth_yoy_pct": row.get("revenue_growth_yoy_pct", None),

                "actual_net_income": row.get("actual_net_income", None),
                "net_income_diff_qoq": row.get("net_income_diff_qoq", None),
                "net_income_diff_yoy": row.get("net_income_diff_yoy", None),
                "net_income_growth_qoq_pct": row.get("net_income_growth_qoq_pct", None),
                "net_income_growth_yoy_pct": row.get("net_income_growth_yoy_pct", None),

                "actual_operating_income": row.get("actual_operating_income", None),
                "operating_income_diff_qoq": row.get("operating_income_diff_qoq", None),
                "operating_income_diff_yoy": row.get("operating_income_diff_yoy", None),
                "operating_income_growth_qoq_pct": row.get("operating_income_growth_qoq_pct", None),
                "operating_income_growth_yoy_pct": row.get("operating_income_growth_yoy_pct", None),

                "net_income_margin": row.get("net_income_margin", None),
            }

            doc.update(price_features)
            documents.append(doc)

    logging.info(f"{ticker_symbol}: created {len(documents)} documents")
    print("Documents created:", len(documents))

    return documents


# --------------------------------------------------
# Main load process
# --------------------------------------------------

def main():
    """Builds all documents and inserts them into MongoDB."""
    collection = get_mongo_collection()

    all_documents = []

    for ticker_symbol, cik in MAG7.items():
        try:
            docs = build_documents_for_ticker(ticker_symbol, cik)
            all_documents.extend(docs)

        except Exception as e:
            print(f"Error processing {ticker_symbol}: {e}")
            logging.exception(f"Error processing {ticker_symbol}: {e}")

    if not all_documents:
        raise RuntimeError("No documents were created.")

    collection.delete_many({})
    collection.insert_many(all_documents)

    logging.info(f"Inserted {len(all_documents)} total documents into MongoDB")
    print(f"Inserted {len(all_documents)} documents into MongoDB.")

    if len(all_documents) >= 1000:
        print("Dataset scale requirement met: 1000+ documents.")
    else:
        print("Warning: dataset has fewer than 1000 documents.")


if __name__ == "__main__":
    main()
```

# analysis.py

```
import os
import logging

import certifi
import pandas as pd
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from pymongo import MongoClient

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


# --------------------------------------------------
# Setup
# --------------------------------------------------

load_dotenv()

os.makedirs("logs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

logging.basicConfig(
    filename="logs/analysis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# --------------------------------------------------
# MongoDB connection
# --------------------------------------------------

def get_mongo_collection():
    """Connects to MongoDB Atlas and returns the project collection."""
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB")
    collection_name = os.getenv("MONGO_COLLECTION")

    if not mongo_uri:
        raise ValueError("MONGO_URI is missing from .env file")

    client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
    db = client[db_name]
    return db[collection_name]


# --------------------------------------------------
# Data loading and preparation
# --------------------------------------------------

def load_data_from_mongo():
    """Queries MongoDB documents and converts them into a pandas DataFrame."""
    collection = get_mongo_collection()

    records = list(collection.find({}))

    if not records:
        raise RuntimeError("No documents found in MongoDB collection.")

    df = pd.DataFrame(records)

    if "_id" in df.columns:
        df = df.drop(columns=["_id"])

    logging.info(f"Loaded {len(df)} rows from MongoDB")

    return df


def prepare_model_data(df):
    """Cleans dataframe and prepares numeric predictors for modeling."""
    df = df.copy()

    df["earnings_date"] = pd.to_datetime(df["earnings_date"])
    df["filing_date"] = pd.to_datetime(df["filing_date"])

    numeric_features = [
        "actual_eps",
        "estimated_eps",
        "eps_surprise_pct",

        "actual_revenue",
        "revenue_diff_qoq",
        "revenue_diff_yoy",
        "revenue_growth_qoq_pct",
        "revenue_growth_yoy_pct",

        "actual_net_income",
        "net_income_diff_qoq",
        "net_income_diff_yoy",
        "net_income_growth_qoq_pct",
        "net_income_growth_yoy_pct",

        "actual_operating_income",
        "operating_income_diff_qoq",
        "operating_income_diff_yoy",
        "operating_income_growth_qoq_pct",
        "operating_income_growth_yoy_pct",

        "net_income_margin",
        "momentum_10d",
        "momentum_30d",
        "volatility_10d",
        "volatility_30d",
    ]

    target = "post_earnings_return"

    model_df = df[
        ["ticker", "earnings_date", "fiscal_year", "fiscal_period", "return_horizon"]
        + numeric_features
        + [target]
    ].copy()

    for col in numeric_features + [target]:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    model_df = model_df.replace([float("inf"), float("-inf")], pd.NA)
    model_df = model_df.dropna(subset=numeric_features + [target])

    logging.info(f"Prepared modeling dataframe with {len(model_df)} usable rows")

    return model_df, numeric_features, target


# --------------------------------------------------
# Modeling
# --------------------------------------------------

def train_gradient_boosting_by_horizon(model_df, features, target):
    """
    Trains one Gradient Boosting Regressor per return horizon.

    This helps determine which post-earnings window is most explainable
    using pre-earnings behavior and reported financial performance.
    """
    results = []
    feature_importance_frames = []

    horizons = sorted(model_df["return_horizon"].unique())

    for horizon in horizons:
        horizon_df = model_df[model_df["return_horizon"] == horizon].copy()

        X = horizon_df[features]
        y = horizon_df[target]

        if len(horizon_df) < 50:
            logging.warning(f"Skipping horizon {horizon}: insufficient rows")
            continue

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=42
        )

        model = GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.03,
            max_depth=3,
            random_state=42
        )

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
        r2 = r2_score(y_test, y_pred)

        results.append({
            "return_horizon": horizon,
            "n_observations": len(horizon_df),
            "mae": mae,
            "rmse": rmse,
            "r2": r2
        })

        importance_df = pd.DataFrame({
            "feature": features,
            "importance": model.feature_importances_,
            "return_horizon": horizon
        }).sort_values("importance", ascending=False)

        feature_importance_frames.append(importance_df)

        logging.info(
            f"Horizon {horizon}: MAE={mae:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}"
        )

    results_df = pd.DataFrame(results)
    feature_importance_df = pd.concat(feature_importance_frames, ignore_index=True)

    return results_df, feature_importance_df


# --------------------------------------------------
# Visualizations
# --------------------------------------------------

def plot_model_performance(results_df):
    """Creates a bar chart comparing R-squared by return horizon."""
    plt.figure(figsize=(8, 5))

    plt.bar(
        results_df["return_horizon"].astype(str),
        results_df["r2"]
    )

    plt.axhline(0, linewidth=1)

    plt.title("Gradient Boosting Model Performance by Return Horizon")
    plt.xlabel("Post-Earnings Return Horizon (Trading Days)")
    plt.ylabel("Test R-Squared")
    plt.tight_layout()

    output_path = "outputs/model_performance_by_horizon.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    logging.info(f"Saved model performance chart to {output_path}")


def plot_top_features(feature_importance_df, best_horizon, top_n=10):
    """Creates a bar chart of the most important predictors for the best horizon."""
    top_features = (
        feature_importance_df[
            feature_importance_df["return_horizon"] == best_horizon
        ]
        .sort_values("importance", ascending=False)
        .head(top_n)
        .sort_values("importance", ascending=True)
    )

    plt.figure(figsize=(9, 6))

    plt.barh(
        top_features["feature"],
        top_features["importance"]
    )

    plt.title(f"Top Predictors of {best_horizon}-Day Post-Earnings Returns")
    plt.xlabel("Gradient Boosting Feature Importance")
    plt.ylabel("Feature")
    plt.tight_layout()

    output_path = f"outputs/top_features_{best_horizon}d_horizon.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    logging.info(f"Saved feature importance chart to {output_path}")


# --------------------------------------------------
# Main analysis pipeline
# --------------------------------------------------

def main():
    """Runs the full analysis pipeline."""
    df = load_data_from_mongo()

    print("Raw MongoDB dataframe shape:", df.shape)
    print("Columns:")
    print(df.columns.tolist())

    model_df, features, target = prepare_model_data(df)

    print("\nPrepared modeling dataframe shape:", model_df.shape)
    print("\nRows by return horizon:")
    print(model_df["return_horizon"].value_counts().sort_index())

    results_df, feature_importance_df = train_gradient_boosting_by_horizon(
        model_df,
        features,
        target
    )

    results_df = results_df.sort_values("return_horizon")
    feature_importance_df = feature_importance_df.sort_values(
        ["return_horizon", "importance"],
        ascending=[True, False]
    )

    results_df.to_csv("outputs/model_results_by_horizon.csv", index=False)
    feature_importance_df.to_csv("outputs/feature_importance_by_horizon.csv", index=False)

    print("\nModel Results by Horizon:")
    print(results_df)

    best_horizon = results_df.sort_values("r2", ascending=False).iloc[0]["return_horizon"]

    print(f"\nBest horizon based on test R-squared: {int(best_horizon)} trading day(s)")

    print("\nTop 10 Predictors for Best Horizon:")
    print(
        feature_importance_df[
            feature_importance_df["return_horizon"] == best_horizon
        ].head(10)
    )

    plot_model_performance(results_df)
    plot_top_features(feature_importance_df, best_horizon)

    print("\nAnalysis complete.")
    print("Saved outputs:")
    print("- outputs/model_results_by_horizon.csv")
    print("- outputs/feature_importance_by_horizon.csv")
    print("- outputs/model_performance_by_horizon.png")
    print(f"- outputs/top_features_{int(best_horizon)}d_horizon.png")


if __name__ == "__main__":
    main()
```