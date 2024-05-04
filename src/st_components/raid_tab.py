import json
import pandas as pd
import streamlit as st

from .database_handler import DatabaseHandler

# 定义常量
PHYSICS_COLOR = "#ffa34a"
MAGIC_COLOR = "#2599be"


# 创建解析 JSON 字符串的函数
def parse_extra_info(json_str):
    try:
        dot_data = json.loads(json_str)
        name = dot_data.get("name", "")
        duration = dot_data.get("duration", 0)
        value = dot_data.get("value", 0)
        return f"{duration}秒伤害{value}每跳的{name}Dot"
    except json.JSONDecodeError:
        return "解析错误"


# 定义样式函数
def apply_style(row):
    style = {}
    if row["type"] == "physics":
        style["name"] = f"color: {PHYSICS_COLOR};"
    elif row["type"] == "magic":
        style["name"] = f"color: {MAGIC_COLOR};"
    return pd.Series(style)


# 获取副本时间轴数据
def get_raid_table(db_handler: DatabaseHandler) -> pd.DataFrame:
    raid_list = ["p9s"]
    raid = st.sidebar.selectbox("选择副本", raid_list, key="raid_choice")

    if not raid:
        st.warning("还未支持该副本！")
        return pd.DataFrame()

    # 获取副本数据
    try:
        raid_df = db_handler.query(f"SELECT * FROM {raid}_timeline")
    except Exception as e:
        st.error(f"无法从数据库中获取数据：{e}")
        return pd.DataFrame()

    # 显示 DataFrame
    st.dataframe(
        raid_df.style.apply(apply_style, axis=1).format(
            formatter=parse_extra_info, subset=["extra_info"], na_rep="-"
        ),
        use_container_width=True,
        hide_index=True,
        column_order=["prepare_time", "name", "damage", "target", "extra_info"],
        column_config={
            "name": st.column_config.TextColumn("伤害名"),
            "prepare_time": st.column_config.TextColumn("释放时间"),
            "damage": st.column_config.NumberColumn("伤害数值"),
            "target": st.column_config.TextColumn("目标"),
            "extra_info": st.column_config.TextColumn("其他", width="large"),
        },
    )

    return raid_df
