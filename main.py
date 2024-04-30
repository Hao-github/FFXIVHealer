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
if "player_df" not in st.session_state:
    st.session_state["player_df"] = default_df


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


def get_healing_df():
    uploaded_file = st.sidebar.file_uploader("在这里上传你的奶轴")
    if not uploaded_file:
        st.write("没有奶轴的话, 奶茶小散也没法虚空分析呀")
        return False
    st.session_state["healing_df"] = pd.read_excel(uploaded_file, engine="openpyxl")
    return True

def edit_healing_df():
    res = st.data_editor(
        st.session_state["healing_df"],
        key="healing_df_editor",
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "user": st.column_config.SelectboxColumn(
                "释放者",
                options=["mt", "st", "h1", "h2", "d1", "d2", "d3", "d4"],
                required=True,
            ),
            "target": st.column_config.SelectboxColumn(
                "目标",
                options=["mt", "st", "h1", "h2", "d1", "d2", "d3", "d4"],
                help="不填入目标, 则默认为以释放者为目标;群体技能和状态类(如秘策)技能无需填入目标",
            ),
            "time": st.column_config.TextColumn(
                "释放时间",
                help="填入的时间格式为xx:yy.zzz, 否则无法填入",
                validate=r"^\d{2}:(0[0-9]|[1-5][0-9])\.\d{3}$",
                required=True,
            ),
            "name": st.column_config.TextColumn(
                "技能",
                required=True,
            ),
            "duration": st.column_config.NumberColumn(
                "持续时间",
                help="仅针对学者的绿线设置的参数",
            ),
        },
        hide_index=True,
        args=(),
        on_change=on_change,
    )
    st.session_state["healing_df"] = res


def get_raid_df() -> pd.DataFrame:
    raid_list = ["P9S"]
    raid = st.sidebar.selectbox("想要奶茶小散分析什么副本", raid_list)
    if not raid:
        st.title("还未支持这个本/这个不是副本！")
        return pd.DataFrame()
    return load_data(os.path.join(resources_dir, "raid_timeline", f"{raid}.csv"))


def on_change():
    changes = st.session_state["healing_df_editor"]
    df0: pd.DataFrame = st.session_state["healing_df"]
    if edited_rows := changes.get("edited_rows"):
        df0.update(pd.DataFrame.from_dict(edited_rows, orient="index"))
    if deleted_rows := changes.get("deleted_rows"):
        df0.drop(df0.index[deleted_rows], inplace=True)
    if add_rows := changes.get("added_rows"):
        df0 = pd.concat(
            [df0, pd.DataFrame([pd.Series(row) for row in add_rows])],
            axis=0,
            ignore_index=True,
        )


def main():
    raid_df = get_raid_df()
    if raid_df.empty:
        return

    if not get_healing_df():
        return


    healing_tab, result_tab = st.tabs(["奶轴", "结果"])

    click_run = st.sidebar.button("RUN!", type="primary")
    player_list_expander()

    with healing_tab:
        edit_healing_df()
        if st.button("Save", key="save_edited_healing_df"):
            pass

    if click_run:
        translate_df = load_data(os.path.join(resources_dir, "locale", "skill.csv"))
        healing_df = st.session_state["healing_df"]
        simulation = Simulation(st.session_state["player_df"])
        simulation.add_raid_timeline(raid_df)
        simulation.add_healing_timeline(healing_df.merge(translate_df, on="name"))
        output: Output = simulation.run(0.01)
        with result_tab:
            html(output.show_line().render_embed(), width=800, height=600)


if __name__ == "__main__":
    main()
