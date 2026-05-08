import streamlit as st
import pandas as pd


def show_overview(df: pd.DataFrame):
    st.subheader("Dataset Overview")

    exact_duplicates = df.duplicated().sum()
    total_missing = df.isnull().sum().sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Exact Duplicates", exact_duplicates)
    col4.metric("Missing Values", total_missing)

    st.markdown("### Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)

    st.markdown("### Duplicate Detection")

    selected_cols = st.multiselect(
        "Select columns to check for repeated records",
        df.columns.tolist()
    )

    if selected_cols and len(selected_cols) == 1:
        st.info(
            "Selecting only one broad column may flag many repeated values. "
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

            st.dataframe(repeated_rows, use_container_width=True)

        else:
            st.success("No repeated records found for the selected columns.")

    else:
        st.info("Select one or more columns to check for repeated records.")

    st.markdown("### Column Information")

    overview_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum().values,
        "Missing %": (
            df.isnull().sum().values / len(df) * 100
        ).round(2),
        "Unique Values": df.nunique().values
    })

    st.dataframe(overview_df, use_container_width=True)