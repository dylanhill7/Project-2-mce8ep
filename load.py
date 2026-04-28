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