import streamlit as st
import pandas as pd
import plotly.express as px


def style_plotly_chart(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#1F2937"),
        title_font=dict(color="#1F2937", size=20),
        legend=dict(
            font=dict(color="#1F2937"),
            title_font=dict(color="#1F2937"),
            bgcolor="rgba(255,255,255,0.8)"
        ), 
        margin=dict(l=40, r=40, t=70, b=40),
        xaxis=dict(
            gridcolor="#E5E7EB",
            linecolor="#CBD5E1",
            tickfont=dict(color="#1F2937"),
            title_font=dict(color="#1F2937")
        ),
        yaxis=dict(
            gridcolor="#E5E7EB",
            linecolor="#CBD5E1",
            tickfont=dict(color="#1F2937"),
            title_font=dict(color="#1F2937")
        )
    )
    return fig


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
    percent_missing = round(total_missing / (df.shape[0] * df.shape[1]) * 100, 2)

    st.info(
        f"Dataset contains **{total_missing:,} missing value(s)** across "
        f"**{len(missing_df)} column(s)**, covering **{percent_missing}%** of all cells."
    )

    st.markdown("### Columns with Missing Values")
    st.caption("Columns are ordered by highest missing percentage.")

    st.dataframe(
        missing_df,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        missing_df,
        x="Column",
        y="Missing %",
        title="Missing Percentage by Column",
        text="Missing %",
        color_discrete_sequence=["#7C8DB5"]
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#1F2937"),
        marker_line_color="#374151",
        marker_line_width=0.5
    )

    fig.update_layout(
        height=450,
        yaxis_title="Missing Percentage (%)",
        xaxis_tickangle=-45,
        bargap=0.25
    )

    fig = style_plotly_chart(fig)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Cleaning Recommendations")

    for _, row in missing_df.iterrows():
        column = row["Column"]
        percent = row["Missing %"]

        if percent < 5:
            recommendation = "Low missingness – simple imputation may be suitable."
        elif percent < 30:
            recommendation = "Moderate missingness – investigate patterns before imputing."
        else:
            recommendation = "High missingness – consider dropping this column or using advanced imputation."

        st.write(f"**{column}**: {percent}% missing – {recommendation}")