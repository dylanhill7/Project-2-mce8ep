## Analysis Rationale

The analysis process was designed to evaluate how well pre-earnings market behavior and reported financial performance can explain short-term 
stock price reactions following earnings announcements. A Gradient Boosting Regressor was selected as the primary modeling approach because it is 
capable of capturing non-linear relationships and interactions between features, which are common in financial data and are not well handled by 
simple linear models. The analysis was conducted separately across multiple post-earnings return horizons (1, 3, 5, and 10 trading days) to assess
how predictive relationships evolve over time, rather than assuming a single fixed reaction window. Feature selection focused on both firm 
fundamentals (e.g., revenue, net income, and their growth rates) and market-based indicators (e.g., momentum and volatility), reflecting the 
hypothesis that both financial performance and investor sentiment contribute to price movements. A train-test split was used to evaluate 
out-of-sample performance, with metrics such as R-squared, mean absolute error, and root mean squared error used to assess model fit and predictive
accuracy. Additionally, feature importance scores from the gradient boosting model were used to identify which variables contribute most to 
explaining variation in post-earnings returns. Overall, this approach balances model flexibility, interpretability, and robustness, allowing for a 
comprehensive evaluation of the project’s central research question.


## Visualization Rationale

The visualization strategy was designed to clearly communicate both model performance and the relative importance of predictors in a way that is 
accessible to a broad audience. A bar chart was used to display model performance (R-squared) across different post-earnings return horizons (1, 3, 
5, and 10 days) because it allows for straightforward comparison across discrete categories and highlights how explanatory power changes over time. 
Including a horizontal reference line at zero further aids interpretation by making it immediately clear when the model performs worse than a naive 
baseline. For feature importance, a horizontal bar chart was chosen to display the top predictors identified by the gradient boosting model, as this 
format improves readability for longer feature names and emphasizes the ranking of variables. The number of features displayed was limited to the top 
ten to avoid visual clutter and focus attention on the most impactful drivers of stock price movement. All visualizations were formatted with clear 
axis labels, descriptive titles, and sufficient spacing to ensure they are publication quality and easily interpretable. Together, these design 
choices prioritize clarity, comparability, and effective communication of the key insights derived from the analysis.
