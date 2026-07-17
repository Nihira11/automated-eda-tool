### Note: The app may take a few seconds to wake up if it has been inactive.

# Automated EDA Tool (Interactive Data Analysis App)

An interactive data analysis tool that helps users quickly understand any CSV dataset without writing code.

After uploading a file, the app automatically checks data quality, creates charts, calculates summary statistics, identifies possible problems and produces useful insights.

---

## Live Demo
Live app: https://automated-eda-tool.streamlit.app/ 

---

## Features

### Dataset Overview
Provides a quick summary of the uploaded dataset, including:

- Number of rows and columns
- Column names and information
- Data types
- Summary statistics
- Dataset preview

![Overview](screenshots/overview.png)

### Automated Insights
Automatically reviews the dataset and highlights important findings, including:

- Dataset structure
- Missing values
- Skewed columns
- Possible outliers
- Data quality warnings

![Insights](screenshots/insights.png)

### Missing Value Analysis
Finds and explains missing data using:

- Missing value counts
- Missing value percentages
- Visual comparisons between columns

![Missing Values](screenshots/missing_values.png)

### Distribution Analysis
Helps users understand how numerical values are spread across the dataset through:

- Histograms
- Box plots
- Distribution explanations
- Skewness detection

![Distributions](screenshots/distributions.png)
![Distributions](screenshots/distributions_2.png)

### Outlier Detection
Uses the Interquartile Range (IQR) method to identify unusual values.

The page shows:
- Number of outliers
- Percentage of outliers
- Outlier visualisations
- Column-level comparisons

![Outliers](screenshots/outliers.png)

### Correlation Analysis
Studies the relationships between numerical columns using:

- Correlation heatmaps
- Strongest numeric relationships
- Simple relationship explanations

![Correlations](screenshots/correlations.png)

### Target Variable Analysis
Allows users to select a target column and explore the variables connected to it.

It includes:
- Target distribution
- Important driver rankings
- Feature importance insights
- Relationships between the target and other columns

![Target Analysis](screenshots/target.png)

### Data Quality Checks
Checks the dataset for common problems, including:

- Duplicate records
- Possible incorrect data types
- Columns with too many unique values
- Possible ID columns

![Duplicates](screenshots/duplicate_detection.png)

---

## Project Purpose

Exploratory Data Analysis is an important first step in most data science projects. However, checking every column, creating charts and finding data quality problems can take a lot of time. This tool automates the most common EDA tasks and helps analysts, students and researchers understand a new dataset before starting modelling or deeper analysis.

The application follows a normal data analysis process by automatically:
- Checking data quality
- Finding missing values
- Identifying possible outliers
- Studying data distributions
- Analysing correlations
- Creating useful dataset insights

---

## Tools and Technologies

| Category | Tools |
| ------- | ------------ |
| Language | Python |
| Data processing | Pandas |
| Visualisation | Plotly |
| Web application | Streamlit |
| Design | Custom CSS |

---

## Project Structure

```
automated-eda-tool/
│
├── app.py                              # Main Streamlit app
├── README.md                           # Project documentation
├── requirements.txt                    # Project dependencies
│
├── modules/
│   ├── overview.py                     # Dataset overview and summary statistics
│   ├── insights.py                     # Automated insight generation
│   ├── missing.py                      # Missing values analysis
│   ├── distributions.py                # Distribution charts and analysis
│   ├── correlations.py                 # Correlation analysis and heatmaps
│   ├── outliers.py                     # Outlier detection and analysis
│   ├── target_analysis.py              # Target analysis and driver detection
│   └── styles.py                       # App styling
│
├── data/                               # Sample datasets used for testing
│
└── screenshots/                        # Screenshots
│   ├── overview.png
│   ├── overview_2.png
│   ├── insights.png
│   ├── missing_values.png
│   ├── distributions.png
│   ├── distributions_2.png
│   ├── duplicate_detection.png
│   ├── outliers.png
│   ├── correlations.png
│   └── target.png
```

---

## Installation

```bash
# 1. Clone the repository:
git clone https://github.com/Nihira11/automated-eda-tool.git

# 2. Open the project directory:
cd automated-eda-tool

# 3. Install dependencies:
pip install -r requirements.txt

# 4. Run the application:
streamlit run app.py
```

---

## Example Datasets Tested

- [IBM Telco Customer Churn Dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
- [Titanic Survival Prediction Dataset](https://www.kaggle.com/datasets/yasserh/titanic-dataset)
- Small Synthetic Dataset (Self-made, included in the repository)

The application is designed to work with most structured CSV datasets

---

## Future Improvements

Possible improvements include:

- Export complete EDA reports as PDF or HTML
- Recommend useful features for modelling
- Add support for time-series datasets
- Include more advanced statistical tests
- Check whether a dataset is ready for machine learning
- Allow users to download analysis summaries

---

## Author

Developed as a Data Analytics and Data Science portfolio project demonstrating:

- Data cleaning
- Exploratory Data Analysis
- Data visualisation
- Streamlit development
- Python application development
