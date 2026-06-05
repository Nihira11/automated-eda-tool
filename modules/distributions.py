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


def show_distribution(df: pd.DataFrame):
    st.subheader("Distribution Analysis")

    column = st.selectbox("Select a column to analyze", df.columns)

    series = df[column]
    series_clean = series.dropna()

    if series_clean.empty:
        st.warning("Column contains only missing values.")
        return

    unique_vals = series_clean.nunique()
    is_numeric = pd.api.types.is_numeric_dtype(series_clean)

    if is_numeric and unique_vals < 15:
        is_categorical = True
    else:
        is_categorical = not is_numeric

    if is_categorical:

        value_counts = series_clean.value_counts().reset_index()
        value_counts.columns = [column, "Count"]

        total = value_counts["Count"].sum()
        value_counts["Percent"] = (value_counts["Count"] / total * 100).round(2)

        if unique_vals <= 5:

            st.write("### Category Breakdown")

            st.dataframe(value_counts, use_container_width=True)

            fig = px.bar(
                value_counts,
                x=column,
                y="Count",
                text="Count",
                title=f"Distribution of {column}",
                color_discrete_sequence=["#7C8DB5"]
            )

            fig.update_traces(
                textposition="outside",
                textfont=dict(color="#1F2937"),
                marker_line_color="#374151",
                marker_line_width=0.5
            )

            fig.update_layout(
                height=400,
                bargap=0.3
            )

            fig = style_plotly_chart(fig)

            st.plotly_chart(fig, use_container_width=True)

            top = value_counts.iloc[0]
            st.info(
                f"Most common value is **{top[column]}** "
                f"({top['Percent']}% of rows)."
            )

        elif unique_vals <= 15:

            st.write("### Top Categories")

            value_counts = value_counts.head(10)

            fig = px.bar(
                value_counts,
                x=column,
                y="Count",
                text="Count",
                title=f"Top Categories in {column}",
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
                xaxis_tickangle=-30,
                bargap=0.2
            )

            fig = style_plotly_chart(fig)

            st.plotly_chart(fig, use_container_width=True)

            st.info(f"{column} has {unique_vals} unique categories.")

        else:
            st.warning(
                f"{column} has too many unique values ({unique_vals}). "
                "Visualization skipped."
            )

    else:

        st.write("### Histogram")

        fig = px.histogram(
            df,
            x=column,
            nbins=30,
            title=f"Distribution of {column}",
            opacity=0.85,
            color_discrete_sequence=["#7C8DB5"]
        )

        fig.update_traces(
            marker_line_color="#374151",
            marker_line_width=0.5
        )

        fig.update_layout(
            height=450,
            bargap=0.1
        )

        fig = style_plotly_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.write("### Box Plot")

        fig_box = px.box(
            df,
            x=column,
            title=f"Box Plot of {column}",
            color_discrete_sequence=["#C4A7E7"]
        )

        fig_box.update_layout(height=280)

        fig_box = style_plotly_chart(fig_box)

        st.plotly_chart(fig_box, use_container_width=True)

        skew = series_clean.skew()

        if skew > 1:
            st.info(f"{column} is strongly right-skewed.")
        elif skew < -1:
            st.info(f"{column} is strongly left-skewed.")
        else:
            st.info(f"{column} is fairly symmetric.")