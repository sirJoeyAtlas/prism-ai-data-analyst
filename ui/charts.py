import streamlit as st
import pandas as pd


def render_result(result, fig):
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

    if isinstance(result, pd.DataFrame):
        st.dataframe(result, use_container_width=True)
    elif isinstance(result, pd.Series):
        st.dataframe(result.to_frame(), use_container_width=True)
    elif isinstance(result, (int, float)):
        # Scalar number → display as a metric
        if isinstance(result, float):
            st.metric("Result", f"{result:,.2f}")
        else:
            st.metric("Result", f"{result:,}")
    elif isinstance(result, str):
        st.info(f"**Result:** {result}")
    elif result is not None:
        st.write(result)


def render_data_preview(df: pd.DataFrame):
    with st.expander("📊 Data Preview", expanded=False):
        st.dataframe(df.head(50), use_container_width=True)


def render_profile(profile: dict):
    with st.expander("🔍 Data Profile", expanded=False):
        col1, col2 = st.columns(2)
        col1.metric("Rows", profile["rows"])
        col2.metric("Columns", profile["columns"])

        for col, info in profile["column_info"].items():
            st.write(f"**{col}** — {info['dtype']}")
            if info.get("min") is not None:
                st.caption(
                    f"Missing: {info['missing']} | Min: {info['min']:.2f} | "
                    f"Max: {info['max']:.2f} | Mean: {info['mean']:.2f}"
                )
            else:
                st.caption(f"Missing: {info['missing']} | Unique: {info.get('unique', 'N/A')}")