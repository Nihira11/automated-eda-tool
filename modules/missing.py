import streamlit as st
import pandas as pd
import plotly.express as px


def show_missing_values(df: pd.DataFrame):
    st.subheader("Missing Values Analysis")

    missing_count = df.isnull().sum()
    missing_percent = (missing_count / len(df) * 100).round(2)

    missing_df = pd.DataFrame({
        "Column": df.columns,
        "Missing Values": missing_count.values,
        "Missing %": missing_percent.values
    })

    missing_df = missing_df[missing_df["Missing Values"] > 0].sort_values(
        by="Missing %",
        ascending=False
    )

    if missing_df.empty:
        st.success("No missing values found in this dataset.")
        return

    total_missing = missing_count.sum()

    st.info(
        f"Dataset contains {total_missing} missing value(s) across "
        f"{len(missing_df)} column(s)."
    )

    st.markdown("### Columns with Missing Values")
    st.caption("Columns are ordered by highest missing percentage.")

    for _, row in missing_df.iterrows():
        st.write(
            f"- **{row['Column']}** → {row['Missing Values']} missing "
            f"({row['Missing %']}%)"
        )

    fig = px.bar(
        missing_df,
        x="Column",
        y="Missing %",
        title="Missing Percentage",
        text="Missing %"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        yaxis_title="Missing Percentage (%)",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Cleaning Recommendations")

    for _, row in missing_df.iterrows():
        column = row["Column"]
        percent = row["Missing %"]

        if percent < 5:
            recommendation = "Low missingness — simple imputation may be suitable."
        elif percent < 30:
            recommendation = "Moderate missingness — investigate patterns before imputing."
        else:
            recommendation = "High missingness — consider dropping this column or using advanced imputation."

        st.write(f"**{column}**: {percent}% missing — {recommendation}")