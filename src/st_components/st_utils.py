import os

import pandas as pd
import streamlit as st


@st.cache_data
def load_data(df_str: str) -> pd.DataFrame:
    return pd.read_csv(df_str, encoding="utf-8")


resources_dir = os.path.join(os.getcwd(), "static")
members = ["MT", "ST", "H1", "H2", "D1", "D2", "D3", "D4"]
translate_df = load_data(os.path.join(resources_dir, "locale", "skill.csv"))
