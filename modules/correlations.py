import streamlit as st
import pandas as pd
import plotly.express as px


HIGH_CARDINALITY_THRESHOLD = 30
SOFT_GROUP_COLOURS = ["#8FB9E3", "#6F9FD8", "#E6A0A8", "#C4A7E7"]


def style_plotly_chart(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#1F2937"),
        title_font=dict(color="#1F2937", size=20),
        legend=dict(
            font=dict(color="#1F2937", size=14),
            title_font=dict(color="#1F2937", size=15),
            bgcolor="rgba(255,255,255,0.90)",
            bordercolor="#E5E0D8",
            borderwidth=1
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(color="#1F2937", size=13),
            title_font=dict(color="#1F2937", size=14)
        ),
        margin=dict(l=70, r=70, t=80, b=70),
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


def convert_numeric_strings(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    for col in df_copy.columns:
        if df_copy[col].dtype == "object":
            converted = pd.to_numeric(df_copy[col], errors="coerce")

            if converted.notna().mean() > 0.8:
                df_copy[col] = converted

    return df_copy


def detect_feature_type(series: pd.Series, column_name: str) -> str:
    clean_series = series.dropna()
    unique_count = clean_series.nunique(dropna=True)
    total_count = len(clean_series)

    if total_count == 0:
        return "empty"

    col_lower = column_name.lower()
    unique_ratio = unique_count / total_count

    id_like_names = [
        "id",
        "uuid",
        "identifier",
        "key",
        "name",
        "ticket"
    ]

    has_id_signal = any(
        col_lower == signal
        or col_lower.endswith(signal)
        or col_lower.startswith(signal)
        or f"_{signal}" in col_lower
        or f"{signal}_" in col_lower
        for signal in id_like_names
    )

    if has_id_signal and unique_ratio > 0.5:
        return "id"

    if unique_ratio > 0.85 and unique_count > 30:
        return "possible_id"

    if pd.api.types.is_numeric_dtype(clean_series):
        if unique_count <= 10:
            return "categorical_numeric"

        return "continuous_numeric"

    if unique_count > HIGH_CARDINALITY_THRESHOLD:
        return "high_cardinality"

    return "categorical"


def show_correlations(df: pd.DataFrame):
    st.subheader("Relationship Analysis")

    df_clean = convert_numeric_strings(df)

    feature_types = {
        col: detect_feature_type(df_clean[col], col)
        for col in df_clean.columns
    }

    usable_cols = [
        col for col in df_clean.columns
        if feature_types[col] not in [
            "id",
            "possible_id",
            "high_cardinality",
            "empty"
        ]
    ]

    numeric_cols = [
        col for col in usable_cols
        if pd.api.types.is_numeric_dtype(df_clean[col])
    ]

    st.write(
        "This section explores relationships between suitable columns. "
        "ID-like and high-cardinality columns are skipped to avoid unreadable charts."
    )

    skipped_cols = [
        col for col, col_type in feature_types.items()
        if col_type in ["id", "possible_id", "high_cardinality"]
    ]

    if skipped_cols:
        st.info(
            "Skipped columns not suitable for relationship charts: "
            + ", ".join(skipped_cols)
        )

    if len(numeric_cols) >= 2:
        st.markdown("### Correlation Heatmap")

        corr = df_clean[numeric_cols].corr()

        fig = px.imshow(
            corr.round(2),
            text_auto=True,
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Numeric Correlation Heatmap"
        )

        fig.update_layout(height=550)
        fig = style_plotly_chart(fig)

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Strongest Numeric Relationships")

        corr_pairs = corr.unstack().reset_index()
        corr_pairs.columns = ["Feature 1", "Feature 2", "Correlation"]

        corr_pairs = corr_pairs[corr_pairs["Feature 1"] != corr_pairs["Feature 2"]]

        corr_pairs["Pair"] = corr_pairs.apply(
            lambda row: tuple(sorted([row["Feature 1"], row["Feature 2"]])),
            axis=1
        )

        corr_pairs = corr_pairs.drop_duplicates(subset="Pair")
        corr_pairs["Absolute Correlation"] = corr_pairs["Correlation"].abs()

        top_corr = corr_pairs.sort_values(
            by="Absolute Correlation",
            ascending=False
        ).head(5)

        if top_corr.empty:
            st.info("No meaningful numeric correlations found.")
        else:
            for _, row in top_corr.iterrows():
                direction = "positive" if row["Correlation"] > 0 else "negative"

                st.write(
                    f"- **{row['Feature 1']} ↔ {row['Feature 2']}**: "
                    f"{row['Correlation']:.2f} ({direction} relationship)"
                )
    else:
        st.warning("Not enough numeric columns for correlation heatmap.")

    st.markdown("### Explore Any Relationship")

    if len(usable_cols) < 2:
        st.warning("Not enough usable columns for relationship analysis.")
        return

    col1, col2 = st.columns(2)

    x_axis = col1.selectbox(
        "Select X-axis",
        usable_cols,
        key="relationship_x_axis"
    )

    y_axis = col2.selectbox(
        "Select Y-axis",
        [col for col in usable_cols if col != x_axis],
        key="relationship_y_axis"
    )

    relationship_df = df_clean[[x_axis, y_axis]].dropna()

    if relationship_df.empty:
        st.warning("No usable rows available for the selected columns.")
        return

    x_type = feature_types[x_axis]
    y_type = feature_types[y_axis]

    st.caption(
        f"Detected types – {x_axis}: {x_type}, {y_axis}: {y_type}. "
        "Chart type selected automatically."
    )

    x_is_numeric = pd.api.types.is_numeric_dtype(relationship_df[x_axis])
    y_is_numeric = pd.api.types.is_numeric_dtype(relationship_df[y_axis])

    x_is_categorical = x_type in ["categorical", "categorical_numeric"]
    y_is_categorical = y_type in ["categorical", "categorical_numeric"]

    if x_is_categorical and y_is_categorical:
        plot_df = relationship_df.copy()
        plot_df[x_axis] = plot_df[x_axis].astype(str)
        plot_df[y_axis] = plot_df[y_axis].astype(str)

        fig_relationship = px.histogram(
            plot_df,
            x=x_axis,
            color=y_axis,
            barmode="group",
            title=f"{x_axis} by {y_axis}",
            color_discrete_sequence=SOFT_GROUP_COLOURS
        )

        st.info("Both variables behave like categories, so a grouped bar chart is shown.")

    elif x_is_categorical and y_is_numeric:
        plot_df = relationship_df.copy()
        plot_df[x_axis] = plot_df[x_axis].astype(str)

        fig_relationship = px.box(
            plot_df,
            x=x_axis,
            y=y_axis,
            title=f"{y_axis} by {x_axis}",
            color_discrete_sequence=["#C4A7E7"]
        )

        st.info(f"Showing **{y_axis}** distribution across categories of **{x_axis}**.")

    elif x_is_numeric and y_is_categorical:
        plot_df = relationship_df.copy()
        plot_df[y_axis] = plot_df[y_axis].astype(str)

        fig_relationship = px.box(
            plot_df,
            x=y_axis,
            y=x_axis,
            title=f"{x_axis} by {y_axis}",
            color_discrete_sequence=["#C4A7E7"]
        )

        st.info(f"Showing **{x_axis}** distribution across categories of **{y_axis}**.")

    else:
        fig_relationship = px.scatter(
            relationship_df,
            x=x_axis,
            y=y_axis,
            title=f"{x_axis} vs {y_axis}",
            opacity=0.6,
            color_discrete_sequence=["#8796B3"]
        )

        st.info("Both variables are numeric, so a scatter plot is shown.")

    fig_relationship = style_plotly_chart(fig_relationship)

    fig_relationship.update_layout(
        height=520,
        bargap=0.25,
        margin=dict(l=70, r=40, t=80, b=80),
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor="right",
            yanchor="top",
            font=dict(color="#1F2937", size=14),
            title_font=dict(color="#1F2937", size=15),
            bgcolor="rgba(255,255,255,0.90)",
            bordercolor="#E5E0D8",
            borderwidth=1
        )
    )

    st.plotly_chart(fig_relationship, use_container_width=True)