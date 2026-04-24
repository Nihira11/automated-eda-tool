import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Automated EDA Tool",
    page_icon="📊",
    layout="wide"
)

st.title("Automated EDA Tool")
st.write("Upload any CSV file to generate an instant exploratory data analysis report.")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success("Dataset uploaded successfully.")

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Duplicate Rows", df.duplicated().sum())
    col4.metric("Missing Values", df.isnull().sum().sum())

    st.subheader("Column Information")
    overview_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum().values,
        "Missing %": (df.isnull().sum().values / len(df) * 100).round(2),
        "Unique Values": df.nunique().values
    })

    st.dataframe(overview_df)
else:
    st.info("Upload a CSV file to begin.")