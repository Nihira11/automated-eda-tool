import streamlit as st
import pandas as pd

from modules.overview import show_overview
from modules.missing import show_missing_values
from modules.distributions import show_distribution
from modules.correlations import show_correlations
from modules.target import show_target_analysis


st.set_page_config(
    page_title="Automated EDA Tool",
    page_icon="📊",
    layout="wide"
)

st.title("Automated EDA Tool")

st.write(
    "Upload any CSV file to automatically generate an exploratory data analysis report."
)

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success("Dataset uploaded successfully.")

    # overview
    show_overview(df)

    st.markdown("---")

    # missing values
    show_missing_values(df)

    st.markdown("---")

    # missing value inspector
    st.subheader("Missing Value Inspector")

    st.write(
        "Choose a column to inspect rows containing missing values."
    )

    missing_columns = df.columns[df.isnull().sum() > 0].tolist()

    if missing_columns:

        col_to_check = st.selectbox(
            "Choose a column with missing values",
            missing_columns
        )

        selected_missing_count = df[col_to_check].isnull().sum()

        selected_missing_percent = (
            selected_missing_count / len(df) * 100
        ).round(2)

        col1, col2 = st.columns(2)

        col1.metric(
            "Missing Rows",
            selected_missing_count
        )

        col2.metric(
            "Missing %",
            f"{selected_missing_percent}%"
        )

        st.dataframe(
            df[df[col_to_check].isnull()],
            use_container_width=True
        )

    else:
        st.success("No missing values found in any column.")

    st.markdown("---")

    # distributions
    show_distribution(df)

    st.markdown("---")

    # relationship explorer
    show_correlations(df)

    st.markdown("---")

    # target analysis
    show_target_analysis(df)

else:
    st.info("Upload a CSV file to begin.")