# DS 4320 Project 2: Earnings Echo

This repository contains the materials for a data science project investigating the extent to which pre-earnings market behavior and reported financial performance explain short-term stock price reactions following earnings announcements for Magnificent 7 companies. It includes a MongoDB document database constructed from financial and market data, a pipeline that performs data extraction, feature engineering, and predictive modeling, and a press release summarizing key insights for a general audience. The repository also provides metadata detailing the structure and uncertainty of the dataset, along with documentation outlining the problem definition, domain context, and data creation process. Together, these components present a complete workflow from data acquisition and modeling to interpretation and communication of results.

**Name:** Dylan Hill

**Net ID:** mce8ep

**DOI:** <a href="https://doi.org/10.5281/zenodo.19856706"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.19856706.svg" /></a>

**Link to Press Release:** https://github.com/dylanhill7/Project-2-mce8ep/blob/main/Press-Release.md

**Link to Pipeline:** xyz

**Name of License:** MIT License

**Link to License:** https://github.com/dylanhill7/Project-2-mce8ep/blob/main/LICENSE


## Problem Definition
**Initial General Problem:** Forecasting stock prices

**Refined Specific Problem Statement:** To what extent can pre-earnings behavior and reported financial performance explain short-term stock price reactions following earnings announcements for Magnificent 7 companies?

**Project Motivation:** With a lot of headlines circulating about five of the 'Magnificent 7' companies reporting earnings this week, that got me thinking on what that meant for investors and how the financials of these companies might go on to impact their stock prices in the coming weeks. There is a lot to dissect when it comes to these earnings reports and there can be a good amount of confusion, but in the end these events generate a lot of buzz because they represent signals that can and typically do dictate future movement of price. Thus I wanted to leverage the concepts we've been learning in this class and past machine learning classes to build out a dataset with key results from earnings reports like EPS and revenue as well as statistics capturing the behavior of the stock leading up to the earnings report date. Using all of this, I believe I'll be able to extract some valuable insights as to what variables are most important to consider following these earnings reports and what exactly the timeline looks like on these fluctuations in price (whether we see them after 1 day, 3 days, etc). I want to frame this as being applicable to all big tech companies, and so given the scope of this project we will be looking at just Mag 7 companies to do that, as I feel like they are generally representative of big tech especially when you go back and look at earnings data from the last 10 years.

**Rationale for Refinement:** While forecasting stock prices is a broad and widely studied problem, it presents significant challenges due to the sheer number of factors that influence market movements, many of which are difficult to quantify or predict. To make the problem more tractable and analytically meaningful, this project narrows its focus to earnings announcements, which represent well-defined, recurring events that introduce new information into the market. By centering the analysis on these discrete events, the project can isolate the impact of specific financial disclosures—such as revenue and earnings performance—while also incorporating measurable pre-earnings market behavior like momentum and volatility. Additionally, restricting the scope to Magnificent 7 companies ensures consistency in data availability and business models while still capturing a meaningful segment of the large-cap technology sector. This refinement allows for a more structured, event-driven analysis that balances complexity with interpretability, making it possible to draw clearer conclusions about short-term stock price reactions.

**Press Release Headline:** tbd, make it once you have insights from analysis

**Link to Press Release:** https://github.com/dylanhill7/Project-2-mce8ep/blob/main/Press-Release.md


## Domain Exposition
**Terminology:**

| Term                     | Type   | Definition |
|--------------------------|--------|------------|
| Earnings Announcement     | Jargon | The quarterly release of a company’s financial results, including metrics like revenue and earnings per share, which often trigger significant stock price movement. |
| Earnings Surprise         | Jargon | The difference between a company’s reported earnings and analysts’ expectations, often used to gauge market reaction. |
| Magnificent 7             | Jargon | A group of seven large-cap U.S. technology companies (Apple, Microsoft, Amazon, Alphabet, Meta, Nvidia, Tesla) known for their market dominance and influence on indices. |
| Efficient Market Hypothesis | Jargon | The theory that asset prices reflect all available information, implying that earnings announcements should be quickly incorporated into stock prices. |
| Market Reaction Window    | Jargon | The period immediately following an event (e.g., earnings release) during which stock price changes are analyzed. |
| Earnings Per Share (EPS)  | KPI    | A company’s net income divided by its number of outstanding shares; a key measure of profitability used by investors. |
| Revenue Growth (QoQ/YoY)  | KPI    | The percentage change in a company’s revenue compared to the previous quarter (QoQ) or the same quarter in the prior year (YoY). |
| Momentum (10d/30d)        | KPI    | The percentage change in a stock’s price over a recent time window (e.g., 10 or 30 trading days), indicating short-term trend direction. |
| Volatility (10d/30d)      | KPI    | The standard deviation of daily stock returns over a given period, measuring how much the price fluctuates. |
| Post-Earnings Return      | KPI    | The percentage change in a stock’s price over a specified horizon (e.g., 1, 3, 5, or 10 days) after an earnings announcement. |

**Domain Explanation:** This project operates within the domain of financial markets and equity research, specifically focusing on how publicly traded companies’ earnings announcements influence short-term stock price behavior. In modern financial markets, quarterly earnings reports serve as one of the most significant and widely anticipated information releases, providing investors with updated insights into a firm’s financial performance through metrics such as revenue, earnings per share (EPS), and profitability. These announcements are closely monitored because they often contain both new information and signals relative to prior expectations, which can lead to rapid price adjustments in the market. This project centers on the “Magnificent 7” technology companies, whose size and influence make them particularly impactful on broader market movements. By combining firm-level financial data with pre-earnings market indicators such as momentum and volatility, the analysis sits at the intersection of financial statement analysis, market microstructure, and quantitative trading. Ultimately, the project seeks to understand whether patterns in financial performance and recent market behavior can systematically explain or predict stock price reactions in the days following earnings announcements, contributing to the broader question of market efficiency.

**Background Reading Folder:** https://myuva-my.sharepoint.com/:f:/g/personal/mce8ep_virginia_edu/IgCmRCaeLXvUQJVKyphGrekFAVASy_sTK2VrTBmTd7plxMc?e=dlBrxv

**Summary of Readings:** 

| Title | Description | Link |
|------|-------------|------|
| Uncertainty Risk Resolution Before Earnings Announcements | This paper examines how stock returns are generated in the period leading up to earnings announcements, finding that a large portion of returns occur before the announcement due to the resolution of uncertainty. It highlights the importance of pre-announcement behavior and information flow in explaining price movements. | https://www.pbcsf.tsinghua.edu.cn/PDF/yifabiao1.pdf |
| Market and Analyst Reactions to Earnings News: An Efficiency Comparison | This study compares how quickly financial analysts and the stock market react to earnings announcements, finding that markets incorporate information more efficiently and rapidly than analysts, who tend to adjust more gradually. | https://www.anderson.ucla.edu/documents/areas/fac/accounting/drift503.pdf |
| Revenue Surprises and Stock Returns | This paper investigates how revenue surprises, in addition to earnings surprises, impact stock returns. It shows that revenue provides incremental information about future performance and that markets may underreact to this information. | https://pages.stern.nyu.edu/~jlivnat/JAE%20submission.pdf |
| Earnings Announcements are Full of Surprises | This study introduces the concept of Earnings Announcement Returns (EAR) and shows that stock price reactions to earnings contain broader information beyond EPS, including sales and forward-looking signals. It also documents persistent return patterns following announcements. | https://www.anderson.ucla.edu/documents/areas/fac/finance/ear.pdf |
| Digital Insiders and Informed Trading Before Earnings Announcements | This paper explores how private information leakage and cybersecurity risks can lead to informed trading before earnings announcements, showing that some information may be incorporated into prices prior to public release. | https://www.iimb.ac.in/sites/default/files/inline-files/Digital-Trading-Before%20Earnings-Announcements.pdf |


## Data Creation
**Provenance (Data Acquisition Process):** The dataset for this project was constructed by integrating financial statement data from the U.S. Securities and Exchange Commission (SEC) with market and earnings data from Yahoo Finance using Python-based data pipelines. Firm-level financial data—including revenue, net income, and operating income—were retrieved through the SEC’s Company Facts API, which provides standardized XBRL filings directly from corporate 10-Q and 10-K reports. These filings were programmatically accessed using each company’s Central Index Key (CIK), parsed into structured DataFrames, and cleaned to isolate true quarterly observations. Because fourth-quarter (Q4) values are not always explicitly reported in 10-K filings, they were derived by subtracting the sum of Q1–Q3 values from annual totals, ensuring a consistent quarterly dataset across firms and time. The dataset was then restricted to the most recent 44 quarters per firm to maintain consistency across all companies.

Complementing the financial data, earnings announcement dates and analyst expectations (e.g., estimated and reported EPS) were collected using the yfinance library, which sources data from Yahoo Finance. Historical stock price data were also retrieved through the same interface, enabling the construction of pre-earnings market features such as momentum and volatility, as well as post-earnings return outcomes across multiple time horizons (1, 3, 5, and 10 trading days). All datasets were aligned by matching SEC filing dates to the nearest earnings announcement dates within a defined tolerance window, and timestamps were normalized to ensure consistency across sources. The final dataset was structured as a document-oriented collection and stored in a MongoDB database, where each document represents a firm-quarter observation paired with a specific return horizon. This process resulted in over 1,200 documents, each combining financial performance metrics, pre-earnings market indicators, and post-earnings price reactions, forming the foundation for subsequent analysis.

**Supplementary Code:**

| File Name | Description | Link |
|-----------|-------------|------|
| load.py | Main data ingestion and processing pipeline. This script retrieves financial statement data from the SEC API and earnings/price data from Yahoo Finance, engineers features (e.g., growth rates, momentum, volatility), aligns datasets by earnings dates, and loads the final structured documents into a MongoDB database. | https://github.com/dylanhill7/Project-2-mce8ep/blob/main/load.py |

**Critical Decision Rationale:** Several critical design decisions were made during the data construction process, each involving trade-offs that could introduce or mitigate uncertainty. First, the decision to rely on SEC XBRL filings as the primary source for financial data ensured high reliability and consistency, but required judgment in handling incomplete reporting structures—most notably the derivation of fourth-quarter (Q4) values by subtracting Q1–Q3 totals from annual figures. While this approach standardizes the dataset, it introduces potential error if prior quarters contain restatements or inconsistencies. Additionally, aligning SEC filing dates with Yahoo Finance earnings announcement dates required the use of a nearest-date merge with a defined tolerance window. This choice balances the need to match corresponding events while acknowledging that filing dates and announcement dates do not always coincide perfectly, which may introduce slight temporal misalignment.

Further judgment was required in feature engineering, particularly in selecting pre-earnings market indicators such as momentum and volatility and defining appropriate lookback windows (e.g., 10-day and 30-day periods). These windows reflect common practices in financial analysis but may not capture all relevant dynamics for every firm or time period. Similarly, the construction of post-earnings returns across multiple horizons (1, 3, 5, and 10 days) reflects a trade-off between capturing immediate reactions and short-term drift, while potentially missing longer-term effects. Finally, filtering out observations with insufficient trading data (e.g., fewer than 30 prior days of price history) ensures data quality but reduces sample size. Collectively, these decisions aim to create a consistent and analyzable dataset while carefully managing the inherent uncertainty present in financial data integration and feature construction.

**Bias Identification:** Bias could be introduced in the data collection process through several key design choices made when assembling and filtering the dataset. First, the project focuses exclusively on the “Magnificent 7” companies, which introduces selection bias by restricting the sample to large-cap, highly liquid technology firms that are not representative of the broader equity market. These firms tend to have more analyst coverage, more predictable earnings cycles, and stronger investor attention, meaning the patterns observed in this dataset may not generalize to smaller or less-followed companies. Additionally, the dataset is limited to the most recent 44 quarters of data, which improves consistency across firms but may introduce temporal bias by emphasizing more recent market conditions, particularly those shaped by post-2020 macroeconomic dynamics such as low interest rates, inflation, and increased retail trading activity.

Further bias may arise from the process of aligning SEC filing data with earnings announcement dates obtained from Yahoo Finance. Because these dates do not always perfectly coincide, a nearest-date matching approach with a tolerance window is used, which could introduce slight misalignment between financial disclosures and the corresponding market reactions. The exclusion of observations with insufficient historical price data (e.g., fewer than 30 prior trading days) may also introduce bias by disproportionately removing earlier time periods or atypical market conditions. Finally, reliance on publicly available financial and market data means that the dataset reflects only information that has been formally reported or widely disseminated, potentially overlooking informal or private information flows that may influence trading behavior prior to earnings announcements. While these choices were made to ensure data quality and feasibility, they may influence which firms, time periods, and market dynamics are ultimately represented in the analysis.

**Bias Mitigation:** Bias in the dataset can be mitigated and quantified through several analytical and modeling steps. First, the impact of focusing exclusively on the Magnificent 7 companies can be assessed by comparing summary statistics (e.g., average post-earnings returns, volatility, and earnings surprise distributions) across firms within the dataset to evaluate whether results are being driven disproportionately by a subset of companies. Model robustness can also be evaluated using cross-validation, where performance metrics such as mean squared error or classification accuracy (depending on the modeling approach) are averaged across multiple folds. The variance across these folds provides a measure of how sensitive the model is to different training samples, helping quantify uncertainty in predictive performance.

Additionally, potential misalignment between SEC filing dates and earnings announcement dates can be examined by analyzing the distribution of time differences between matched events; if large deviations are observed, sensitivity analyses can be performed by adjusting the merge tolerance window and observing changes in model results. To address biases introduced by scale differences across firms (e.g., absolute revenue or income levels), the inclusion of percentage-based features such as growth rates and margins helps normalize financial performance and improve comparability. Furthermore, prediction uncertainty can be communicated through continuous outputs (e.g., predicted returns or probabilities) rather than discrete classifications, providing a more nuanced view of expected outcomes. Finally, results can be contextualized by analyzing performance across different time horizons (1, 3, 5, and 10 days), which helps identify whether observed relationships are consistent or sensitive to the chosen evaluation window. Together, these approaches help both identify and quantify potential sources of bias and uncertainty, improving the reliability and interpretability of the analysis.


## Metadata
**Implicit Schema:** To maintain consistency in the document database despite the use of an implicit schema, a set of structural conventions was established for how each document is constructed. Each document represents a single firm–quarter–return horizon observation and is identified by a combination of fields including ticker, earnings_date, fiscal_year, fiscal_period, and return_horizon. Rather than embedding multiple observations within a single document, the dataset is flattened so that each document contains both financial data and market features for a specific earnings event and evaluation window. Core financial fields—such as actual_revenue, actual_net_income, and actual_operating_income—are stored as numeric values (integers or floats), along with engineered features including quarter-over-quarter and year-over-year differences and percentage growth rates. Market-based features, such as momentum, volatility, and post-earnings return, are also stored as floating-point numbers.

Date fields, including earnings_date and filing_date, are stored in a standardized ISO string format (YYYY-MM-DD) to ensure consistency across documents and compatibility with MongoDB queries. Missing or unavailable values are explicitly represented as null to preserve schema integrity without forcing imputation at the data storage stage. Additionally, all documents follow a consistent naming convention for fields (e.g., suffixes such as _qoq, _yoy, and _pct) to clearly distinguish between different types of engineered features. These guidelines ensure that, while MongoDB allows flexible document structures, each record adheres to a predictable and uniform format that supports efficient querying, aggregation, and downstream machine learning analysis.

**Data Summary:**

| Collection Name | Document Description | Number of Documents | Embedded Data | Time Coverage |
|---|---|---|---|---|
| earnings_reactions | One document per firm–quarter–return horizon observation, containing financial performance, engineered growth features, pre-earnings market indicators, and post-earnings returns | 1,218 | ticker, earnings_date, filing_date, fiscal_year, fiscal_period, actual_eps, estimated_eps, eps_surprise_pct, actual_revenue, revenue_diff_qoq, revenue_diff_yoy, revenue_growth_qoq_pct, revenue_growth_yoy_pct, actual_net_income, net_income_diff_qoq, net_income_diff_yoy, net_income_growth_qoq_pct, net_income_growth_yoy_pct, actual_operating_income, operating_income_diff_qoq, operating_income_diff_yoy, operating_income_growth_qoq_pct, operating_income_growth_yoy_pct, net_income_margin, momentum_10d, momentum_30d, volatility_10d, volatility_30d, return_horizon, post_earnings_return | ~2015–2026 |

**Data Dictionary:**

| Feature Name | Data Type | Description | Example |
|---|---|---|---|
| _id | ObjectId | Unique MongoDB identifier for each document | 69f115b9ee6ceafd7dc2a03a |
| ticker | String | Stock ticker symbol identifying the company | AAPL |
| earnings_date | Date (ISO string) | Date of the earnings announcement | 2015-04-27 |
| filing_date | Date (ISO string) | Date the company filed its financial report with the SEC | 2015-04-28 |
| fiscal_year | Integer | Fiscal year corresponding to the earnings report | 2015 |
| fiscal_period | String | Fiscal quarter (Q1, Q2, Q3, Q4) | Q2 |
| actual_eps | Float | Reported earnings per share from the earnings announcement | 0.58 |
| estimated_eps | Float | Analyst consensus estimate for earnings per share | 0.54 |
| eps_surprise_pct | Float | Percentage difference between actual and estimated EPS | 7.93 |
| actual_revenue | Float | Total reported revenue for the quarter (USD) | 58010000000 |
| revenue_diff_qoq | Float | Absolute change in revenue compared to the previous quarter | -16589000000 |
| revenue_diff_yoy | Float | Absolute change in revenue compared to the same quarter last year | 12364000000 |
| revenue_growth_qoq_pct | Float | Percentage change in revenue quarter-over-quarter | -0.2224 |
| revenue_growth_yoy_pct | Float | Percentage change in revenue year-over-year | 0.2709 |
| actual_net_income | Float | Net income reported for the quarter (USD) | 13569000000 |
| net_income_diff_qoq | Float | Absolute change in net income compared to the previous quarter | -4455000000 |
| net_income_diff_yoy | Float | Absolute change in net income compared to the same quarter last year | 3346000000 |
| net_income_growth_qoq_pct | Float | Percentage change in net income quarter-over-quarter | -0.2472 |
| net_income_growth_yoy_pct | Float | Percentage change in net income year-over-year | 0.3273 |
| actual_operating_income | Float | Operating income reported for the quarter (USD) | 18278000000 |
| operating_income_diff_qoq | Float | Absolute change in operating income compared to the previous quarter | -5968000000 |
| operating_income_diff_yoy | Float | Absolute change in operating income compared to the same quarter last year | 4685000000 |
| operating_income_growth_qoq_pct | Float | Percentage change in operating income quarter-over-quarter | -0.2461 |
| operating_income_growth_yoy_pct | Float | Percentage change in operating income year-over-year | 0.3447 |
| net_income_margin | Float | Net income divided by revenue, representing profitability | 0.2339 |
| momentum_10d | Float | Stock return over the 10 trading days prior to earnings | 0.0270 |
| momentum_30d | Float | Stock return over the 30 trading days prior to earnings | 0.0541 |
| volatility_10d | Float | Standard deviation of daily returns over the past 10 trading days | 0.0102 |
| volatility_30d | Float | Standard deviation of daily returns over the past 30 trading days | 0.0118 |
| return_horizon | Integer | Number of trading days after earnings used to measure return | 1 |
| post_earnings_return | Float | Stock return over the specified horizon following earnings | 0.0021 |

**Uncertainty Quantification (For Numerical Features):**

| Feature Name | Source of Uncertainty | Quantification of Uncertainty |
|---|---|---|
| fiscal_year | Derived from SEC filings; may differ from calendar year depending on firm-specific fiscal calendars. | No numerical uncertainty, but categorical misinterpretation risk if fiscal vs calendar alignment is misunderstood. |
| actual_eps | Retrieved from Yahoo Finance earnings data; subject to rounding and vendor aggregation differences. | Typically small, within ±0.01–0.05 EPS due to rounding or reporting differences across sources. |
| estimated_eps | Analyst consensus estimate aggregated by Yahoo Finance; varies across analysts and timing of updates. | Uncertainty can be several percentage points depending on dispersion of analyst forecasts; often ±1–5% of EPS. |
| eps_surprise_pct | Derived from actual and estimated EPS; inherits uncertainty from both inputs. | Propagated uncertainty typically ±1–5 percentage points depending on estimate dispersion and rounding. |
| actual_revenue | Pulled from SEC XBRL filings; may include restatements or differences in reporting tags across firms. | Generally low uncertainty (financial statements are audited), but potential restatement risk; ±0–1% typical. |
| revenue_diff_qoq | Derived from consecutive quarterly revenue values; sensitive to reporting consistency and restatements. | Uncertainty compounds from both quarters; typically ±0–2% of the difference value. |
| revenue_diff_yoy | Derived from revenue compared to same quarter prior year; subject to restatements and structural changes. | Similar to QoQ but more stable; uncertainty typically ±0–2% depending on reporting consistency. |
| revenue_growth_qoq_pct | Computed as percentage change; sensitive to denominator size and extreme values in small quarters. | Higher relative uncertainty when base revenue is small; typically ±1–3 percentage points. |
| revenue_growth_yoy_pct | Derived from YoY revenue change; smoother than QoQ but still affected by reporting changes. | Typically ±1–2 percentage points, lower than QoQ due to reduced seasonality effects. |
| actual_net_income | Retrieved from SEC filings; includes accounting adjustments and potential restatements. | Low measurement error but higher conceptual variability; ±0–2% typical due to accounting treatments. |
| net_income_diff_qoq | Derived from consecutive quarters; highly sensitive to accounting adjustments and one-time items. | Can exhibit large variability; uncertainty often ±2–5% of the difference due to earnings volatility. |
| net_income_diff_yoy | Year-over-year difference; less noisy than QoQ but still affected by non-recurring items. | Typically ±2–4% uncertainty due to accounting adjustments and macroeconomic factors. |
| net_income_growth_qoq_pct | Percentage change in net income; sensitive to small denominators and earnings volatility. | High relative uncertainty when earnings are low; often ±3–6 percentage points. |
| net_income_growth_yoy_pct | YoY percentage change; smoother than QoQ but still influenced by firm-specific events. | Typically ±2–5 percentage points depending on earnings stability. |
| actual_operating_income | Derived from SEC filings; less affected by non-operating items but still subject to reporting variation. | Generally low uncertainty; ±0–2% typical depending on classification differences. |
| operating_income_diff_qoq | Derived metric; influenced by operational variability and reporting adjustments. | Typically ±2–4% of the difference value. |
| operating_income_diff_yoy | Year-over-year difference; more stable but still affected by firm-specific changes. | Typically ±2–3% uncertainty. |
| operating_income_growth_qoq_pct | Percentage change QoQ; sensitive to operational fluctuations and denominator size. | Typically ±2–5 percentage points depending on volatility. |
| operating_income_growth_yoy_pct | YoY percentage change; smoother but still subject to business cycle effects. | Typically ±2–4 percentage points. |
| net_income_margin | Ratio of net income to revenue; combines uncertainty from both inputs. | Propagated uncertainty typically ±1–3 percentage points depending on variability in both components. |
| momentum_10d | Calculated from historical price data; dependent on price accuracy and sampling window. | Price data uncertainty is minimal (<±0.1%), but temporal sampling can introduce ±1–3% variation depending on short-term volatility. |
| momentum_30d | Similar to 10-day momentum but over a longer window; smoother but still sample-dependent. | Typically ±1–2% due to temporal sampling effects. |
| volatility_10d | Standard deviation of daily returns; sensitive to short-term price fluctuations and sample size. | Estimation uncertainty can be ±5–15% due to small sample window (10 days). |
| volatility_30d | Standard deviation over longer window; more stable than 10-day volatility. | Typically ±3–10% estimation uncertainty. |
| return_horizon | User-defined integer representing evaluation window (1, 3, 5, 10 days). | No measurement uncertainty, but modeling sensitivity exists depending on horizon choice. |
| post_earnings_return | Calculated from price data after earnings; dependent on price accuracy and timing alignment. | Price measurement error is small (<±0.1%), but event timing and market noise can introduce ±1–5% variability in observed returns. |
