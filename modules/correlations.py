import streamlit as st
import pandas as pd
import plotly.express as px


def convert_numeric_strings(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    for col in df_copy.columns:
        if df_copy[col].dtype == "object":
            converted = pd.to_numeric(df_copy[col], errors="coerce")

            if converted.notna().mean() > 0.8:
                df_copy[col] = converted

    return df_copy


def detect_feature_type(series: pd.Series, column_name: str) -> str:
    unique_count = series.nunique(dropna=True)
    total_count = len(series)

    if "id" in column_name.lower():
        return "id"

    if pd.api.types.is_numeric_dtype(series):
        unique_ratio = unique_count / total_count

        if unique_ratio > 0.9 and unique_count > 20:
            return "possible_id"

        if unique_count <= 10:
            return "categorical_numeric"

        return "continuous_numeric"

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
        if feature_types[col] not in ["id", "possible_id"]
    ]

    numeric_cols = [
        col for col in usable_cols
        if pd.api.types.is_numeric_dtype(df_clean[col])
    ]

    st.write(
        "This section explores relationships between columns. "
        "The tool automatically detects feature types and selects a suitable chart."
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
        f"Detected types — {x_axis}: {x_type}, {y_axis}: {y_type}. "
        "Chart type selected automatically."
    )

    x_is_numeric = pd.api.types.is_numeric_dtype(relationship_df[x_axis])
    y_is_numeric = pd.api.types.is_numeric_dtype(relationship_df[y_axis])

    x_is_categorical = x_type in ["categorical", "categorical_numeric"]
    y_is_categorical = y_type in ["categorical", "categorical_numeric"]

    # CASE 1: categorical vs categorical
    if x_is_categorical and y_is_categorical:
        plot_df = relationship_df.copy()
        plot_df[x_axis] = plot_df[x_axis].astype(str)
        plot_df[y_axis] = plot_df[y_axis].astype(str)

        fig_relationship = px.histogram(
            plot_df,
            x=x_axis,
            color=y_axis,
            barmode="group",
            title=f"{x_axis} by {y_axis}"
        )

        st.info("Both variables behave like categories, so a grouped bar chart is shown.")

    # CASE 2: categorical vs numeric
    elif x_is_categorical and y_is_numeric:
        plot_df = relationship_df.copy()
        plot_df[x_axis] = plot_df[x_axis].astype(str)

        fig_relationship = px.box(
            plot_df,
            x=x_axis,
            y=y_axis,
            title=f"{y_axis} by {x_axis}"
        )

        st.info(f"Showing **{y_axis}** distribution across categories of **{x_axis}**.")

    # CASE 3: numeric vs categorical
    elif x_is_numeric and y_is_categorical:
        plot_df = relationship_df.copy()
        plot_df[y_axis] = plot_df[y_axis].astype(str)

        fig_relationship = px.box(
            plot_df,
            x=y_axis,
            y=x_axis,
            title=f"{x_axis} by {y_axis}"
        )

        st.info(f"Showing **{x_axis}** distribution across categories of **{y_axis}**.")

    # CASE 4: numeric vs numeric
    else:
        fig_relationship = px.scatter(
            relationship_df,
            x=x_axis,
            y=y_axis,
            title=f"{x_axis} vs {y_axis}",
            opacity=0.55
        )

        st.info("Both variables are numeric, so a scatter plot is shown.")

    fig_relationship.update_layout(
        height=500,
        bargap=0.25
    )

    st.plotly_chart(fig_relationship, use_container_width=True)