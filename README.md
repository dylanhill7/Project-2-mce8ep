# DS 4320 Project 2: Earnings Echo

This repository contains the materials for a data science project investigating the extent to which pre-earnings market behavior and reported financial performance explain short-term stock price reactions following earnings announcements for Magnificent 7 companies. It includes a MongoDB document database constructed from financial and market data, a pipeline that performs data extraction, feature engineering, and predictive modeling, and a press release summarizing key insights for a general audience. The repository also provides metadata detailing the structure and uncertainty of the dataset, along with documentation outlining the problem definition, domain context, and data creation process. Together, these components present a complete workflow from data acquisition and modeling to interpretation and communication of results.

**Name:** Dylan Hill

**Net ID:** mce8ep

**DOI:** <a href="https://doi.org/10.5281/zenodo.19856706"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.19856706.svg" /></a>

**Link to Press Release:** abc

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
**Provenance (Data Acquisition Process):**

**Supplementary Code:**

**Critical Decision Rationale:**

**Bias Identification:**

**Bias Mitigation:**


## Metadata
**Implicit Schema:**

**Data Summary:**

**Data Dictionary:**

**Uncertainty Quantification (For Numerical Features):**
