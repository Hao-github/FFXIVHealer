import os

import pandas as pd
import streamlit as st

from ..models.Jobs.constant import STR2JOB_CLASSES
from .st_utils import resources_dir, load_data


def get_players_df():
    default_df_path = os.path.join(resources_dir, "default.csv")
    default_df = load_data(default_df_path)
    if "player_df" not in st.session_state:
        st.session_state["player_df"] = default_df

    translate_df = load_data(os.path.join(resources_dir, "locale", "job.csv"))
    job_dict = dict(zip(translate_df["job_en"], translate_df["job_cn"]))
    with st.sidebar.expander("队伍配置"):
        options = list(STR2JOB_CLASSES.keys())
        for i, tab in enumerate(st.tabs(default_df["name"].to_list())):
            position = default_df.at[i, "name"]
            with tab:
                col1, col2 = st.columns([3, 1])
                selected_job = col1.selectbox(
                    f"{position}_job",
                    options=options,
                    label_visibility="collapsed",
                    format_func=lambda x: job_dict.get(x),
                    key=f"{position}_job",
                    index=options.index(default_df.at[i, "job"]),
                )
                col2.image(f".\\static\\images\\job\\{selected_job}.png", width=40)
                st.number_input(
                    "生命值上限",
                    step=1,
                    min_value=0,
                    key=f"{position}_max_hp",
                    value=default_df.at[i, "hp"],
                )
                st.number_input(
                    "治疗威力",
                    step=0.01,
                    min_value=0.0,
                    key=f"{position}_potency",
                    value=float(default_df.at[i, "potency"]),
                )
                if selected_job in ["Scholar", "WhiteMage", "Sage"]:
                    st.number_input(
                        "咏速",
                        step=0.01,
                        max_value=2.5,
                        min_value=2.14,
                        key=f"{position}_spellSpeed",
                        value=default_df.at[i, "spellSpeed"],
                    )
        if st.button("Save"):
            st.session_state["player_df"] = pd.DataFrame(
                [
                    [
                        name,
                        st.session_state.get(f"{name}_job"),
                        st.session_state.get(f"{name}_max_hp"),
                        st.session_state.get(f"{name}_potency"),
                        st.session_state.get(f"{name}_spellSpeed", 2.5),
                    ]
                    for name in default_df["name"]
                ],
                columns=default_df.columns,
            )
            st.session_state["player_df"].to_csv(default_df_path)

        return st.session_state["player_df"]
