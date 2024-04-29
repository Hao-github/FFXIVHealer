from src.Fight import Simulation
from src.models.Jobs.constant import JOB_CLASSES
from src.report.Output import Output

import streamlit as st
from streamlit.components.v1 import html
import os
import pandas as pd


def on_change(df_key: str):
    """
    Callback function to handle changes in the data editor.
    """
    origin_df = st.session_state[df_key]

    for idx, row in st.session_state["update_part"].get("edited_rows", {}).items():
        origin_df.loc[idx, list(row.keys())] = list(row.values())
        if "job" in row:
            origin_df.loc[idx, "pic"] = f"app\\static\\images\\job\\{row['job']}.png"

    st.session_state[df_key] = origin_df


@st.cache_data
def load_data(df_str: str) -> pd.DataFrame:
    return pd.read_csv(df_str, encoding="utf-8")


def player_list_expander():
    with st.sidebar.expander("队伍配置"):
        for position in ["mt", "st", "h1", "h2", "d1", "d2", "d3", "d4"]:
            col1, col2 = st.columns([3, 1])
            selected_job = col1.selectbox(
                position, options=JOB_CLASSES.keys(), label_visibility="collapsed"
            )
            col2.image(f".\\static\\images\\job\\{selected_job}.png", width=40)


def get_healing_df() -> pd.DataFrame:
    uploaded_file = st.sidebar.file_uploader("在这里上传你的奶轴")
    if not uploaded_file:
        return pd.DataFrame()
    return pd.read_excel(uploaded_file, engine="openpyxl")


def get_player_df(default_df: pd.DataFrame) -> pd.DataFrame:
    # Load default player data
    default_df["pic"] = default_df["job"].apply(
        lambda x: f"app\\static\\images\\job\\{x}.png"
    )
    df_key = "job_df"
    if df_key not in st.session_state:
        st.session_state[df_key] = default_df

    with st.expander("..."):
        player_df = st.data_editor(
            st.session_state[df_key].copy(),
            key="update_part",
            column_config={
                "job": st.column_config.SelectboxColumn(
                    "职业", width="small", options=JOB_CLASSES.keys(), required=True
                ),
                "hp": st.column_config.NumberColumn(
                    "血量上限", step=1, min_value=0, required=True
                ),
                "damagePerPotency": st.column_config.NumberColumn(
                    "每威力治疗下限",
                    step=0.0001,
                    min_value=0.0,
                    required=True,
                ),
                "pic": st.column_config.ImageColumn("职业图片"),
            },
            disabled=["name"],
            args=(df_key,),
            hide_index=True,
            on_change=on_change,
        )
    return player_df


def main():
    resources_dir = os.path.join(os.getcwd(), "static")
    translate_df = load_data(os.path.join(resources_dir, "locale", "zh-cn.csv"))
    raid_list = ["P9S"]
    raid = st.sidebar.selectbox("想要奶茶小散分析什么副本", raid_list)
    if not raid:
        st.title("还未支持这个本/这个不是副本！")
        return

    default_df = load_data(os.path.join(resources_dir, "default.csv"))

    player_df = get_player_df(default_df)
    raid_df = load_data(os.path.join(resources_dir, "raid_timeline", f"{raid}.csv"))

    healing_df = get_healing_df()
    if healing_df.empty:
        st.write("没有奶轴的话, 奶茶小散也没法虚空分析呀")
        return

    if st.sidebar.button("RUN!", type="primary"):
        simulation = Simulation(translate_df, player_df)
        simulation.add_raid_timeline(raid_df)
        simulation.add_healing_timeline(healing_df)
        simulation.run(0.01)
        Output.show_line()

    player_list_expander()

    html(Output.result.render_embed(), width=900, height=600)


if __name__ == "__main__":
    main()
