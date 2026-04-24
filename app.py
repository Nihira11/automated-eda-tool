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
    st.dataframe(df.head(), use_container_width=True)

    st.subheader("Dataset Overview")

    exact_duplicates = df.duplicated().sum()
    total_missing = df.isnull().sum().sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Exact Duplicates", exact_duplicates)
    col4.metric("Missing Values", total_missing)

    st.subheader("Duplicate Detection (Advanced)")

    selected_cols = st.multiselect(
        "Select columns to check for logical duplicates",
        df.columns.tolist()
    )

    if selected_cols:
        logical_duplicates = df.duplicated(subset=selected_cols).sum()

        st.metric("Logical Duplicates", logical_duplicates)

        if logical_duplicates > 0:
            st.warning(
                f"{logical_duplicates} potential logical duplicate row(s) found based on: "
                + ", ".join(selected_cols)
            )

            duplicate_rows = df[df.duplicated(subset=selected_cols, keep=False)]
            st.write("Potential duplicate records:")
            st.dataframe(duplicate_rows, use_container_width=True)
        else:
            st.success("No logical duplicates found for the selected columns.")
    else:
        st.info("Select one or more columns to check for logical duplicates.")

    st.subheader("Column Information")

    overview_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum().values,
        "Missing %": (df.isnull().sum().values / len(df) * 100).round(2),
        "Unique Values": df.nunique().values
    })

    st.dataframe(overview_df, use_container_width=True)

else:
    st.info("Upload a CSV file to begin.")