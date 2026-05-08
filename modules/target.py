import streamlit as st
import pandas as pd
import plotly.express as px


HIGH_CARDINALITY_THRESHOLD = 30
TOP_DRIVER_LIMIT = 5
MIN_GROUP_SIZE = 30


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
    unique_count = clean_series.nunique()
    total_count = len(clean_series)

    if total_count == 0:
        return "empty"

    column_lower = column_name.lower()
    unique_ratio = unique_count / total_count

    id_signals = ["id", "uuid", "identifier", "key"]

    has_id_signal = any(
        column_lower == signal
        or column_lower.endswith(signal)
        or column_lower.startswith(signal)
        or f"_{signal}" in column_lower
        or f"{signal}_" in column_lower
        for signal in id_signals
    )

    if has_id_signal and unique_ratio > 0.85 and unique_count > 20:
        return "id"

    if pd.api.types.is_numeric_dtype(clean_series):
        if unique_count <= 10:
            return "categorical_numeric"

        return "continuous_numeric"

    if unique_count > HIGH_CARDINALITY_THRESHOLD:
        return "high_cardinality"

    return "categorical"


def get_target_type(series: pd.Series) -> str:
    clean_series = series.dropna()
    unique_count = clean_series.nunique()

    if pd.api.types.is_numeric_dtype(clean_series) and unique_count > 15:
        return "numeric"

    if unique_count == 2:
        return "binary_categorical"

    return "multiclass_categorical"


def choose_default_target(df: pd.DataFrame, usable_targets: list) -> int:
    # General logic only:
    # 1. Prefer binary columns because they are common classification targets.
    # 2. If no binary column exists, use the last usable column because many ML datasets place target last.
    for i, col in enumerate(usable_targets):
        if df[col].dropna().nunique() == 2:
            return i

    return len(usable_targets) - 1


def choose_default_class(values: list) -> int:
    # General structural logic:
    # If values are numeric, choose the larger value as the positive/target class.
    numeric_values = pd.to_numeric(pd.Series(values), errors="coerce")

    if numeric_values.notna().all():
        return int(numeric_values.idxmax())

    # Otherwise choose the less frequent/second class by default is not possible
    # without target counts here, so use first available class and let user change it.
    return 0


def calculate_class_driver_score(
    df: pd.DataFrame,
    feature: str,
    target: str,
    selected_class,
    feature_type: str
):
    temp_df = df[[feature, target]].dropna().copy()

    if temp_df.empty:
        return None

    temp_df["_target_binary"] = (temp_df[target] == selected_class).astype(int)

    if feature_type == "continuous_numeric":
        try:
            temp_df["_feature_group"] = pd.qcut(
                temp_df[feature],
                q=4,
                duplicates="drop"
            )
        except ValueError:
            return None
    else:
        temp_df["_feature_group"] = temp_df[feature].astype(str)

    group_summary = (
        temp_df
        .groupby("_feature_group", observed=False)
        .agg(
            target_rate=("_target_binary", "mean"),
            count=("_target_binary", "count")
        )
        .reset_index()
    )

    group_summary = group_summary[group_summary["count"] >= MIN_GROUP_SIZE]

    if len(group_summary) < 2:
        return None

    overall_rate = temp_df["_target_binary"].mean()

    group_summary["weighted_difference"] = (
        abs(group_summary["target_rate"] - overall_rate)
        * (group_summary["count"] / len(temp_df))
    )

    driver_score = group_summary["weighted_difference"].sum()

    highest_group = group_summary.sort_values(
        by="target_rate",
        ascending=False
    ).iloc[0]

    lowest_group = group_summary.sort_values(
        by="target_rate",
        ascending=True
    ).iloc[0]

    return {
        "score": driver_score,
        "highest_group": str(highest_group["_feature_group"]),
        "highest_rate": highest_group["target_rate"],
        "highest_count": int(highest_group["count"]),
        "lowest_group": str(lowest_group["_feature_group"]),
        "lowest_rate": lowest_group["target_rate"],
        "lowest_count": int(lowest_group["count"])
    }


def calculate_numeric_driver_score(
    df: pd.DataFrame,
    feature: str,
    target: str,
    feature_type: str
):
    temp_df = df[[feature, target]].dropna().copy()

    if temp_df.empty:
        return None

    if feature_type == "continuous_numeric":
        corr = temp_df[feature].corr(temp_df[target])

        if pd.isna(corr):
            return None

        return {
            "score": abs(corr),
            "relationship": "positive" if corr > 0 else "negative",
            "detail": f"Correlation = {corr:.3f}"
        }

    temp_df["_feature_group"] = temp_df[feature].astype(str)

    group_summary = (
        temp_df
        .groupby("_feature_group", observed=False)
        .agg(
            target_mean=(target, "mean"),
            count=(target, "count")
        )
        .reset_index()
    )

    group_summary = group_summary[group_summary["count"] >= MIN_GROUP_SIZE]

    if len(group_summary) < 2:
        return None

    target_range = temp_df[target].max() - temp_df[target].min()

    if target_range == 0:
        return None

    score = (
        group_summary["target_mean"].max()
        - group_summary["target_mean"].min()
    ) / target_range

    highest_group = group_summary.sort_values(
        by="target_mean",
        ascending=False
    ).iloc[0]

    lowest_group = group_summary.sort_values(
        by="target_mean",
        ascending=True
    ).iloc[0]

    return {
        "score": score,
        "highest_group": str(highest_group["_feature_group"]),
        "highest_mean": highest_group["target_mean"],
        "highest_count": int(highest_group["count"]),
        "lowest_group": str(lowest_group["_feature_group"]),
        "lowest_mean": lowest_group["target_mean"],
        "lowest_count": int(lowest_group["count"])
    }


def show_target_distribution(df: pd.DataFrame, target: str, target_type: str):
    st.markdown("### 1. Target Distribution")

    if target_type == "numeric":
        fig = px.histogram(
            df,
            x=target,
            nbins=30,
            title=f"Distribution of {target}"
        )

        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

        summary = df[target].describe().reset_index()
        summary.columns = ["Metric", "Value"]
        st.dataframe(summary, use_container_width=True)

    else:
        counts = (
            df[target]
            .dropna()
            .astype(str)
            .value_counts()
            .reset_index()
        )

        counts.columns = [target, "Count"]
        counts["Percentage"] = (
            counts["Count"] / counts["Count"].sum() * 100
        ).round(2)

        fig = px.bar(
            counts,
            x=target,
            y="Count",
            text="Count",
            title=f"Distribution of {target}"
        )

        fig.update_traces(textposition="outside")
        fig.update_layout(height=420)

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(counts, use_container_width=True)


def build_driver_table(
    df: pd.DataFrame,
    valid_features: list,
    feature_types: dict,
    target: str,
    target_type: str,
    selected_class
):
    rows = []

    for feature in valid_features:
        feature_type = feature_types[feature]

        if target_type in ["binary_categorical", "multiclass_categorical"]:
            result = calculate_class_driver_score(
                df,
                feature,
                target,
                selected_class,
                feature_type
            )

            if result is None:
                continue

            insight = (
                f"Highest {selected_class} rate: {result['highest_group']} "
                f"({result['highest_rate'] * 100:.1f}%, n={result['highest_count']}); "
                f"lowest: {result['lowest_group']} "
                f"({result['lowest_rate'] * 100:.1f}%, n={result['lowest_count']})"
            )

        else:
            result = calculate_numeric_driver_score(
                df,
                feature,
                target,
                feature_type
            )

            if result is None:
                continue

            if feature_type == "continuous_numeric":
                insight = f"{result['relationship'].title()} relationship. {result['detail']}."
            else:
                insight = (
                    f"Highest average {target}: {result['highest_group']} "
                    f"({result['highest_mean']:.2f}, n={result['highest_count']}); "
                    f"lowest: {result['lowest_group']} "
                    f"({result['lowest_mean']:.2f}, n={result['lowest_count']})"
                )

        rows.append({
            "Feature": feature,
            "Driver Score": round(result["score"], 4),
            "Feature Type": feature_type,
            "Key Insight": insight
        })

    if not rows:
        return pd.DataFrame()

    return (
        pd.DataFrame(rows)
        .sort_values(by="Driver Score", ascending=False)
        .head(TOP_DRIVER_LIMIT)
    )


def show_driver_chart(driver_df, target, target_type, selected_class):
    st.markdown("### 2. Top Drivers")

    fig = px.bar(
        driver_df,
        x="Feature",
        y="Driver Score",
        text="Driver Score",
        title=f"Top {TOP_DRIVER_LIMIT} Drivers of {target}"
    )

    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(height=430, xaxis_tickangle=-30)

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(driver_df, use_container_width=True)

    top_3 = driver_df.head(3)["Feature"].tolist()

    if target_type in ["binary_categorical", "multiclass_categorical"]:
        st.success(
            f"Main EDA finding: **{target} = {selected_class}** appears most related to "
            f"**{', '.join(top_3)}**."
        )
    else:
        st.success(
            f"Main EDA finding: **{target}** appears most related to "
            f"**{', '.join(top_3)}**."
        )


def show_driver_inspection(
    df: pd.DataFrame,
    feature: str,
    target: str,
    target_type: str,
    selected_class,
    feature_type: str
):
    st.markdown("### 4. Inspect One Driver")

    temp_df = df[[feature, target]].dropna().copy()

    if temp_df.empty:
        st.info("No usable rows available for this driver.")
        return

    if target_type in ["binary_categorical", "multiclass_categorical"]:
        temp_df["_target_binary"] = (temp_df[target] == selected_class).astype(int)

        if feature_type == "continuous_numeric":
            try:
                temp_df["_feature_group"] = pd.qcut(
                    temp_df[feature],
                    q=4,
                    duplicates="drop"
                )
            except ValueError:
                st.warning("Unable to group this numeric feature reliably.")
                return
        else:
            temp_df["_feature_group"] = temp_df[feature].astype(str)

        rate_df = (
            temp_df
            .groupby("_feature_group", observed=False)
            .agg(
                rate=("_target_binary", "mean"),
                count=("_target_binary", "count")
            )
            .reset_index()
        )

        rate_df = rate_df[rate_df["count"] >= MIN_GROUP_SIZE]

        if rate_df.empty:
            st.warning("Unable to inspect this driver because groups are too small.")
            return

        rate_df["rate"] = (rate_df["rate"] * 100).round(2)
        rate_df["_feature_group"] = rate_df["_feature_group"].astype(str)

        fig = px.bar(
            rate_df,
            x="_feature_group",
            y="rate",
            text="rate",
            title=f"{selected_class} rate by {feature}"
        )

        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(
            height=420,
            xaxis_title=feature,
            yaxis_title=f"{selected_class} Rate (%)",
            xaxis_tickangle=-30,
            yaxis_range=[0, 100]
        )

        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(rate_df, use_container_width=True)

    else:
        if feature_type == "continuous_numeric":
            fig = px.scatter(
                temp_df,
                x=feature,
                y=target,
                opacity=0.55,
                title=f"{feature} vs {target}"
            )
        else:
            temp_df[feature] = temp_df[feature].astype(str)

            fig = px.box(
                temp_df,
                x=feature,
                y=target,
                title=f"{target} across {feature}"
            )

        fig.update_layout(height=420, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)


def show_target_analysis(df: pd.DataFrame):
    st.subheader("Target Analysis")

    st.write(
        "This section uses general EDA logic instead of dataset-specific keywords. "
        "It suggests a target structurally, ranks likely drivers, and explains when "
        "a reliable comparison cannot be made."
    )

    df_clean = convert_numeric_strings(df)

    feature_types = {
        col: detect_feature_type(df_clean[col], col)
        for col in df_clean.columns
    }

    usable_targets = [
        col for col in df_clean.columns
        if feature_types[col] not in ["id", "high_cardinality", "empty"]
    ]

    if not usable_targets:
        st.warning("No suitable target columns found.")
        return

    default_target_index = choose_default_target(df_clean, usable_targets)

    target = st.selectbox(
        "Select Target Variable",
        usable_targets,
        index=default_target_index,
        key="target_variable_select"
    )

    target_type = get_target_type(df_clean[target])

    st.caption(f"Detected target type: **{target_type}**")

    valid_features = [
        col for col in df_clean.columns
        if col != target
        and feature_types[col] not in ["id", "high_cardinality", "empty"]
    ]

    skipped_cols = [
        col for col, col_type in feature_types.items()
        if col != target and col_type in ["id", "high_cardinality"]
    ]

    if skipped_cols:
        st.warning(
            "Skipped columns that are not suitable for reliable EDA comparisons: "
            + ", ".join(skipped_cols)
        )

    if not valid_features:
        st.warning("No usable features are available to compare against the target.")
        return

    show_target_distribution(df_clean, target, target_type)

    selected_class = None

    if target_type in ["binary_categorical", "multiclass_categorical"]:
        target_values = df_clean[target].dropna().unique().tolist()

        selected_class = st.selectbox(
            "Choose the target class to analyse",
            target_values,
            index=choose_default_class(target_values),
            key="target_class_select"
        )

        if target_type == "multiclass_categorical":
            st.info(
                "This target has more than two categories, so the tool uses a one-vs-rest approach."
            )

    driver_df = build_driver_table(
        df_clean,
        valid_features,
        feature_types,
        target,
        target_type,
        selected_class
    )

    if driver_df.empty:
        st.warning(
            "Unable to calculate reliable target drivers. This can happen when groups are too small, "
            "the target has too many rare categories, or there are not enough usable features."
        )
        return

    show_driver_chart(driver_df, target, target_type, selected_class)

    selected_driver = st.selectbox(
        "Choose one driver to inspect visually",
        driver_df["Feature"].tolist(),
        key="driver_inspection_select"
    )

    show_driver_inspection(
        df_clean,
        selected_driver,
        target,
        target_type,
        selected_class,
        feature_types[selected_driver]
    )