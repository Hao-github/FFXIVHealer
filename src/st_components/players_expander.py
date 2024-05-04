import os

import pandas as pd
import streamlit as st

from src.st_components.database_handler import DatabaseHandler

from .st_utils import resources_dir, load_data


def get_players_df(db_handler: DatabaseHandler):
    default_df_path = os.path.join(resources_dir, "default.csv")
    default_df = load_data(default_df_path)
    if "player_df" not in st.session_state:
        st.session_state["player_df"] = default_df

    job_df = db_handler.query("SELECT * FROM job_translate").set_index("en_name")
    with st.sidebar.expander("队伍配置"):
        for i, tab in enumerate(st.tabs(default_df["name"].to_list())):
            row = default_df.iloc[i]
            with tab:
                col1, col2 = st.columns([3, 1])
                selected_job = col1.selectbox(
                    f"{row['name']}_job",
                    options=job_df.index.values,
                    label_visibility="collapsed",
                    format_func=lambda x: job_df.loc[x, "cn_name"],
                    key=f"{row['name']}_job",
                    index=job_df.index.get_loc(row["job"]),  # type: ignore
                )
                col2.image(bytes(job_df.loc[selected_job, "image_data"]), width=40)  # type: ignore
                st.number_input(
                    "生命值上限",
                    step=1,
                    min_value=0,
                    key=f"{row['name']}_max_hp",
                    value=row["hp"],
                )
                st.number_input(
                    "治疗威力",
                    step=0.01,
                    min_value=0.0,
                    key=f"{row['name']}_potency",
                    value=float(row["potency"]),
                )
                if selected_job in ["Scholar", "WhiteMage", "Sage"]:
                    st.number_input(
                        "咏速",
                        step=0.01,
                        max_value=2.5,
                        min_value=2.14,
                        key=f"{row['name']}_spellSpeed",
                        value=row["spellSpeed"],
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
