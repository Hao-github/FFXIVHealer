import os

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html

from src.Fight import Simulation
from src.models.Jobs.constant import JOB_CLASSES
from src.report.Output import Output


resources_dir = os.path.join(os.getcwd(), "static")


@st.cache_data
def load_data(df_str: str) -> pd.DataFrame:
    return pd.read_csv(df_str, encoding="utf-8")


default_df_path = os.path.join(resources_dir, "default.csv")
default_df = load_data(default_df_path)
df_key = "job_df"
if df_key not in st.session_state:
    st.session_state[df_key] = default_df


def player_list_expander():
    translate_df = load_data(os.path.join(resources_dir, "locale", "job.csv"))
    job_dict = dict(zip(translate_df["job_en"], translate_df["job_cn"]))
    with st.sidebar.expander("队伍配置"):
        options = list(JOB_CLASSES.keys())
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
                    value=float(default_df.at[i, "damagePerPotency"]),
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
            st.session_state[df_key] = pd.DataFrame(
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
            st.session_state[df_key].to_csv(default_df_path)


def get_healing_df() -> pd.DataFrame:
    uploaded_file = st.sidebar.file_uploader("在这里上传你的奶轴")
    if not uploaded_file:
        st.write("没有奶轴的话, 奶茶小散也没法虚空分析呀")
        return pd.DataFrame()
    st.session_state["healing_df"] = pd.read_excel(uploaded_file, engine="openpyxl")
    return st.session_state["healing_df"]


def get_raid_df() -> pd.DataFrame:
    raid_list = ["P9S"]
    raid = st.sidebar.selectbox("想要奶茶小散分析什么副本", raid_list)
    if not raid:
        st.title("还未支持这个本/这个不是副本！")
        return pd.DataFrame()
    return load_data(os.path.join(resources_dir, "raid_timeline", f"{raid}.csv"))


def main():
    raid_df = get_raid_df()
    if raid_df.empty:
        return

    healing_df = get_healing_df()
    if healing_df.empty:
        return

    healing_tab, result_tab = st.tabs(["奶轴", "结果"])

    with healing_tab:
        # st.data_editor(
        #     st.session_state["healing_df"],
        #     key="healing_df_editor",
        #     num_rows="dynamic",
        #     use_container_width=True,
        #     column_config={
        #         "user": st.column_config.SelectboxColumn(
        #             "释放者", options=["mt", "st", "h1", "h2", "d1", "d2", "d3", "d4"]
        #         )
        #     },
        #     hide_index=True,
        # )
        pass

    click_run = st.sidebar.button("RUN!", type="primary")
    player_list_expander()

    if click_run:
        translate_df = load_data(os.path.join(resources_dir, "locale", "skill.csv"))
        simulation = Simulation(st.session_state[df_key])
        simulation.add_raid_timeline(raid_df)
        simulation.add_healing_timeline(healing_df.merge(translate_df, on="name"))
        # simulation.run(0.01)
        # Output.show_line()
        # html(Output.result.render_embed(), width=800, height=600)


if __name__ == "__main__":
    main()
