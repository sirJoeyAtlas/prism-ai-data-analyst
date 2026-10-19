import streamlit as st
import pandas as pd
import os
from pathlib import Path
from database import db
from engine import profiler

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/uploads")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: lowercase, strip spaces, replace spaces/dashes/slashes with underscores."""
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        for c in df.columns
    ]
    return df


def render_upload():
    st.sidebar.header("📁 Dataset")

    uploaded = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])

    if uploaded:
        filepath = os.path.join(UPLOAD_DIR, uploaded.name)
        with open(filepath, "wb") as f:
            f.write(uploaded.getbuffer())

        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # 🔑 Normalize column names
        df = clean_columns(df)

        profile = profiler.profile_dataframe(df)
        dataset_id = db.save_dataset(
            uploaded.name, filepath, len(df), len(df.columns), profile
        )

        st.session_state.dataset_id = dataset_id
        st.session_state.df = df
        st.session_state.profile = profile

        st.sidebar.success(f"Loaded {uploaded.name}")
        st.sidebar.caption(f"{len(df)} rows × {len(df.columns)} columns")
        st.sidebar.caption(f"Columns: {', '.join(df.columns)}")

        return df

    if "df" in st.session_state:
        return st.session_state.df

    return None