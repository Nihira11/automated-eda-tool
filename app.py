import streamlit as st
import pandas as pd
from modules.missing import show_missing_values

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

    st.subheader("Duplicate Detection")

    selected_cols = st.multiselect(
        "Select columns to check for repeated records",
        df.columns.tolist()
    )

    if selected_cols and len(selected_cols) == 1:
        st.info(
            "Tip: selecting only one broad column may flag many repeated values. "
            "Select multiple identifying columns for better duplicate detection."
        )

    ignore_missing = st.checkbox(
        "Ignore missing values in duplicate check",
        value=True
    )

    if selected_cols:
        temp_df = df.copy()

        if ignore_missing:
            temp_df = temp_df.dropna(subset=selected_cols)

        repeated_records = temp_df.duplicated(subset=selected_cols).sum()

        st.metric("Repeated Records", repeated_records)

        if repeated_records > 0:
            st.warning(
                f"{repeated_records} row(s) share repeated values based on: "
                + ", ".join(selected_cols)
            )

            repeated_rows = temp_df[
                temp_df.duplicated(subset=selected_cols, keep=False)
            ]

            st.write("Rows with repeated values:")
            st.dataframe(repeated_rows, use_container_width=True)
        else:
            st.success("No repeated records found for the selected columns.")
    else:
        st.info("Select one or more columns to check for repeated records.")

    st.subheader("Column Information")

    overview_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum().values,
        "Missing %": (df.isnull().sum().values / len(df) * 100).round(2),
        "Unique Values": df.nunique().values
    })

    st.dataframe(overview_df, use_container_width=True)

    show_missing_values(df)

    st.subheader("Missing Value Inspector")
    st.write(
        "Choose a column to see how many empty values it has and view the rows where those values are missing."
    )

    missing_columns = df.columns[df.isnull().sum() > 0].tolist()

    if missing_columns:
        col_to_check = st.selectbox(
            "Choose a column with missing values",
            missing_columns
        )

        selected_missing_count = df[col_to_check].isnull().sum()
        selected_missing_percent = (selected_missing_count / len(df) * 100).round(2)

        col_a, col_b = st.columns(2)
        col_a.metric("Missing Rows", selected_missing_count)
        col_b.metric("Missing %", f"{selected_missing_percent}%")

        st.write(f"Rows where **{col_to_check}** is missing:")
        st.dataframe(
            df[df[col_to_check].isnull()],
            use_container_width=True
        )
    else:
        st.success("No missing values found in any column.")

else:
    st.info("Upload a CSV file to begin.")