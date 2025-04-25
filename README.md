# CREDIT AND DEBIT CARD FRAUD DETECTION

# INTRODUCTION

In 2024 alone, 62 million Americans were victims of fraudulent charges on their credit or debit cards, with unauthorized purchases exceeding $6.2 billion annually (Cruz, 2025). Additionally, nearly one in three Americans report being a victim of online financial fraud or cybercrime (Newall & Deeney, 2023). With credit and debit cards now accounting for 60% of all payments (a figure that continues to rise), and with the shift toward a cashless society, opportunities for fraud will only increase (Cruz, 2025). As such, detecting fraud early and practicing card safety are more important than ever. 

Hence, the primary purpose of this project is to develop a machine learning model to accurately classify credit and debit card transactions as fraudulent or legitimate. In order to do so, this project uses a comprehensive financial transactions dataset which contains transaction records, customer information, card data, and fraudulence labels from a banking institution, spanning across the 2010s decade (Kaggle, 2024). 

Beyond building the model, this project also aims to investigate the influence of several factors on fraud risk by addressing the following questions:

1. Which state is most impacted by fraud

2. How are debit/credit card fraud rates related to income level?

3. Are men or women most impacted by fraud?

# PROJECT WORKFLOW

Below are the general steps followed in this project workflow:

1. Gathered data from Kaggle
   
    - An overview of this data is provided below in the "raw data overview" section

2. Cleaned/transformed data using Pandas

   - Details/code necessary for this step are provided in the "notebooks/01_etl.ipynb" file

3. Created SQL schema (DDL script) to load cleaned data into

   - Details/code necessary for this step are provided in the "sql/schema.sql", and "sql/ERD_diagram.png" files

4. Loaded cleaned data into SQL database

   - Details/code necessary for step are provided in the "notebooks/01_etl.ipynb", "sql/materialized_view.sql", "sql/schema.sql", and "sql/view.sql" files

5. Joined SQL tables together and saved all joined data to csv

   - Details/code necessary for this step are provided in the "notebooks/01_etl.ipynb" file

6. Developed ML models (along with EDA for the models) using csv created in previous step

   - Details/code necessary for this step are provided in the "notebooks/02_model.ipynb" and "fraud_detection_pipeline.joblib" files

7. Created dashboard using data from the SQL database

   - Details/code necessary for this step are provided in the "dashboard.py"


# CONCLUSIONS

The following are the main conclusions that were reach from both the machine learning and the questions of interest:

ML Results:

Best Performing Model:

Logistic Regression + SMOTE

Results:
Recall (Fraud): 60% — 149 out of 248 frauds correctly identified


Precision (Fraud): ~0.03% — Very high false positive rate (~463k false alarms)


PR AUC: 0.0005 — Very low due to poor fraud precision


Interpretation:

SMOTE improved recall — the model is better at catching fraud compared to LR w/out SMOTE


But precision dropped dramatically — flagged too many non-fraud cases as fraud


The model is not ready for production but demonstrates how class imbalance impacts model performance


This is a strong proof of concept for detecting rare events like fraud

Questions Results:

1. Which state is most impacted by fraud?

Seems to be Ohio

2. How are debit/credit card fraud rates related to income level?

Credit/debit card fraud tends to target lower-income clients, but varies across levels of debt.

3. Are men or women most impacted by fraud?

Looks to be women

# DASHBOARD SAMPLE

![dashboard_overview](https://github.com/user-attachments/assets/f24d8879-3b55-4a4b-a284-fbbee0b865e1)


![dashboard_pic](https://github.com/user-attachments/assets/425b5858-f010-4ebc-aad1-765eb30f0e78)

