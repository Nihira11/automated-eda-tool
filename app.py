import streamlit as st
import pandas as pd

from modules.overview import show_overview
from modules.missing import show_missing_values
from modules.distributions import show_distribution
from modules.outliers import show_outliers
from modules.correlations import show_correlations
from modules.target import show_target_analysis
from modules.insights import show_automated_insights
from modules.styles import apply_custom_styles


st.set_page_config(
    page_title="Automated EDA Tool",
    page_icon="📊",
    layout="wide"
)

apply_custom_styles()

st.title("Automated EDA Tool")

st.write(
    "Upload a CSV file to generate an interactive exploratory data analysis report."
)


if "df" not in st.session_state:
    st.session_state.df = None

if "filename" not in st.session_state:
    st.session_state.filename = None


if st.session_state.df is None:

    uploaded_file = st.file_uploader(
        "Upload your CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.filename = uploaded_file.name
            st.rerun()

        except pd.errors.EmptyDataError:
            st.error("The uploaded CSV file is empty. Please upload a valid dataset.")

        except Exception as e:
            st.error(f"Unable to read the CSV file: {e}")

else:

    df = st.session_state.df
    filename = st.session_state.filename

    col_file, col_button = st.columns([3, 1])

    with col_file:
        st.markdown(
            f"""
            <div style="
                background-color:#FFFFFF;
                border:1px solid #E5E0D8;
                border-radius:14px;
                padding:14px 18px;
                color:#374151;
                font-weight:600;
            ">
                Dataset: {filename}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_button:
        if st.button("Change file"):
            st.session_state.df = None
            st.session_state.filename = None
            st.rerun()

    st.info("Dataset uploaded successfully.")

    tabs = st.tabs(
        [
            "Overview",
            "Insights",
            "Missing Values",
            "Distributions",
            "Outliers",
            "Correlations",
            "Target Analysis"
        ]
    )

    with tabs[0]:
        show_overview(df)

    with tabs[1]:
        show_automated_insights(df)

    with tabs[2]:
        show_missing_values(df)

        st.markdown("---")

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

            col1.metric("Missing Rows", selected_missing_count)
            col2.metric("Missing %", f"{selected_missing_percent}%")

            st.dataframe(
                df[df[col_to_check].isnull()],
                use_container_width=True
            )

        else:
            st.success("No missing values found in any column.")

    with tabs[3]:
        show_distribution(df)

    with tabs[4]:
        show_outliers(df)

    with tabs[5]:
        show_correlations(df)

    with tabs[6]:
        show_target_analysis(df)