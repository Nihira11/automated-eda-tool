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


def show_outliers(df: pd.DataFrame):
    st.subheader("Outlier Analysis")

    numeric_cols = [
        col for col in df.select_dtypes(include="number").columns.tolist()
        if "year" not in col.lower() and "id" not in col.lower()
    ]

    if not numeric_cols:
        st.info("No numeric columns found for outlier analysis.")
        return

    column = st.selectbox(
        "Select a numeric column to check for outliers",
        numeric_cols,
        key="outlier_column_select"
    )

    series = df[column].dropna()

    if series.empty:
        st.warning("This column has no usable numeric values.")
        return

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        st.info("No meaningful outlier range found because the values are too similar.")
        return

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    outlier_rows = df[outlier_mask]

    outlier_count = len(outlier_rows)
    outlier_percent = round(outlier_count / len(df) * 100, 2)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Q1", round(q1, 2))
    col2.metric("Q3", round(q3, 2))
    col3.metric("IQR", round(iqr, 2))
    col4.metric("Outliers", f"{outlier_count} ({outlier_percent}%)")

    st.write(
        f"Outliers are detected using the IQR rule: values below **{lower_bound:.2f}** "
        f"or above **{upper_bound:.2f}** are flagged."
    )

    fig = px.box(
        df,
        x=column,
        title=f"Outlier Check for {column}",
        color_discrete_sequence=["#C4A7E7"]
    )

    fig.update_layout(height=300)

    fig = style_plotly_chart(fig)

    st.plotly_chart(fig, use_container_width=True)

    if outlier_count > 0:
        st.warning(f"{outlier_count} outlier row(s) found in **{column}**.")
        st.dataframe(
            outlier_rows,
            use_container_width=True
        )
    else:
        st.success(f"No outliers detected in **{column}**.")