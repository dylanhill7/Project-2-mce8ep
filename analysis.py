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