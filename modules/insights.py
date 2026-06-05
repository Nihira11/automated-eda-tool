import streamlit as st
import pandas as pd


def get_numeric_columns(df: pd.DataFrame):
    return df.select_dtypes(include="number").columns.tolist()


def get_categorical_columns(df: pd.DataFrame):
    return df.select_dtypes(exclude="number").columns.tolist()


def summarize_dataset_shape(df: pd.DataFrame):
    rows, cols = df.shape
    return f"The dataset contains **{rows:,} rows** and **{cols:,} columns**."


def summarize_column_types(df: pd.DataFrame):
    numeric_count = len(get_numeric_columns(df))
    categorical_count = len(get_categorical_columns(df))

    return (
        f"The dataset contains **{numeric_count} numeric column(s)** "
        f"and **{categorical_count} categorical column(s)**."
    )


def summarize_missing_values(df: pd.DataFrame):
    missing_percent = (df.isnull().sum() / len(df) * 100).round(2)
    missing_percent = missing_percent[missing_percent > 0].sort_values(ascending=False)

    if missing_percent.empty:
        return "No missing values were detected."

    top_missing = missing_percent.head(3)
    parts = [f"**{col}** ({percent}%)" for col, percent in top_missing.items()]

    return "Missing values are mainly present in " + ", ".join(parts) + "."


def summarize_possible_type_issues(df: pd.DataFrame):
    issues = []

    for col in get_categorical_columns(df):
        sample = df[col].dropna().astype(str).str.strip()

        if sample.empty:
            continue

        numeric_like_ratio = pd.to_numeric(
            sample,
            errors="coerce"
        ).notna().mean()

        if numeric_like_ratio > 0.9 and sample.nunique() > 20:
            issues.append(col)

    if not issues:
        return None

    return (
        "Potential data type issues detected: "
        + ", ".join(f"**{col}**" for col in issues)
        + " may contain numeric values stored as text."
    )


def summarize_numeric_skew(df: pd.DataFrame):
    if len(df) < 30:
        return "Dataset is too small for reliable skewness analysis."

    numeric_cols = get_numeric_columns(df)

    if not numeric_cols:
        return "No numeric columns were available for skewness analysis."

    skewed_cols = []

    for col in numeric_cols:
        series = df[col].dropna()

        if series.nunique() <= 15:
            continue

        skew_value = series.skew()

        if skew_value > 1:
            skewed_cols.append(f"**{col}** is strongly right-skewed")
        elif skew_value < -1:
            skewed_cols.append(f"**{col}** is strongly left-skewed")

    if not skewed_cols:
        return "No strongly skewed numeric columns were detected."

    return "Skewness detected: " + "; ".join(skewed_cols[:3]) + "."


def summarize_outlier_risk(df: pd.DataFrame):
    if len(df) < 30:
        return "Dataset is too small for reliable outlier analysis."
    
    numeric_cols = get_numeric_columns(df)

    if not numeric_cols:
        return "No numeric columns were available for outlier analysis."

    outlier_summaries = []

    for col in numeric_cols:
        series = df[col].dropna()

        if series.nunique() <= 15:
            continue

        if "year" in col.lower() or "id" in col.lower():
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_count = ((series < lower_bound) | (series > upper_bound)).sum()
        outlier_percent = round((outlier_count / len(series)) * 100, 2)

        if outlier_percent > 5:
            outlier_summaries.append(f"**{col}** ({outlier_percent}%)")

    if not outlier_summaries:
        return "No major outlier-heavy numeric columns were detected."

    return (
        "Potential outliers were detected in "
        + "; ".join(outlier_summaries[:3])
        + "."
    )


def summarize_categorical_columns(df: pd.DataFrame):
    categorical_cols = get_categorical_columns(df)

    if not categorical_cols:
        return "No categorical columns were found."

    high_cardinality = []

    for col in categorical_cols:
        if "id" in col.lower():
            continue

        sample = df[col].dropna().astype(str).str.strip()

        if sample.empty:
            continue

        numeric_like_ratio = pd.to_numeric(sample, errors="coerce").notna().mean()

        if numeric_like_ratio > 0.9:
            continue

        unique_count = df[col].nunique(dropna=True)

        if unique_count > 30:
            high_cardinality.append(f"**{col}** has {unique_count:,} unique values")

    if not high_cardinality:
        return "Categorical columns appear manageable for basic visual analysis."

    return (
        "Some categorical columns may be too detailed for simple charts: "
        + "; ".join(high_cardinality[:3])
        + "."
    )


def show_automated_insights(df: pd.DataFrame):
    st.subheader("Automated Insights Summary")

    st.caption(
        "A quick summary of the main data quality and structure patterns detected in the dataset."
    )

    insights = [
        summarize_dataset_shape(df),
        summarize_column_types(df),
        summarize_missing_values(df),
        summarize_numeric_skew(df),
        summarize_outlier_risk(df),
    ]

    type_issue = summarize_possible_type_issues(df)

    if type_issue:
        insights.append(type_issue)

    insights.append(summarize_categorical_columns(df))

    for insight in insights:
        st.markdown(f"- {insight}")

    st.info(
        "These insights are intended as a starting point for exploration. "
        "Review the detailed tabs before making final decisions."
    )