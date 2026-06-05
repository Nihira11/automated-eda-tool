import streamlit as st
import pandas as pd


def detect_likely_id_columns(df: pd.DataFrame):
    likely_ids = []

    for col in df.columns:
        clean_series = df[col].dropna()
        unique_count = clean_series.nunique()
        total_count = len(clean_series)

        if total_count == 0:
            continue

        unique_ratio = unique_count / total_count
        col_lower = col.lower()

        has_id_signal = (
            col_lower == "id"
            or col_lower.endswith("id")
            or "id_" in col_lower
            or "_id" in col_lower
        )

        if has_id_signal and unique_ratio > 0.85:
            likely_ids.append(col)

    return likely_ids


def show_overview(df: pd.DataFrame):
    st.subheader("Dataset Overview")

    total_missing = df.isnull().sum().sum()

    likely_id_cols = detect_likely_id_columns(df)

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", total_missing)

    st.markdown("### Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)
    
    st.markdown("### Duplicate Detection")

    st.write(
        "Select columns that should uniquely identify a record."
    )

    default_duplicate_cols = [
        col for col in df.columns
        if col not in likely_id_cols
    ]

    selected_cols = st.multiselect(
        "Select columns to check for repeated records",
        df.columns.tolist(),
        default=default_duplicate_cols[:min(3, len(default_duplicate_cols))]
    )

    if selected_cols and len(selected_cols) == 1:
        unique_ratio = df[selected_cols[0]].nunique(dropna=True) / len(df)

        if unique_ratio < 0.5:
            st.warning(
                "This column contains many repeated values. "
                "Select additional columns for a more reliable repeated-record check."
            )
        else:
            st.info(
                "This column is fairly unique, but using more than one column usually gives a better check."
            )

    ignore_missing = st.checkbox(
        "Ignore rows with missing values in selected columns",
        value=True
    )

    if selected_cols:
        temp_df = df.copy()

        if ignore_missing:
            temp_df = temp_df.dropna(subset=selected_cols)

        repeated_records = temp_df.duplicated(subset=selected_cols).sum()
        repeated_percent = round(repeated_records / len(temp_df) * 100, 2) if len(temp_df) > 0 else 0

        col_a, col_b = st.columns(2)

        col_a.metric("Potential Duplicate Records", repeated_records)
        col_b.metric("Duplicate %", f"{repeated_percent}%")

        if repeated_records > 0:
            st.warning(
                f"{repeated_records} potential repeated record(s) found using: "
                + ", ".join(selected_cols)
            )

            repeated_rows = temp_df[
                temp_df.duplicated(subset=selected_cols, keep=False)
            ]

            st.dataframe(repeated_rows, use_container_width=True)

        else:
            st.success("No repeated records found using the selected columns.")

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
        "Unique Values": df.nunique(dropna=True).values
    })

    overview_df["Unique %"] = (
        overview_df["Unique Values"] / len(df) * 100
    ).round(2)

    overview_df["Role Hint"] = overview_df["Column"].apply(
        lambda col: "Likely ID" if col in likely_id_cols else "Data Feature"
    )

    st.dataframe(overview_df, use_container_width=True)