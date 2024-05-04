import os
import json
import pandas as pd
import streamlit as st
from .st_utils import load_data, resources_dir


# 创建解析JSON字符串的函数
def parse_dot_json(json_str):
    # 将 JSON 字符串解析为字典对象
    dot_data = json.loads(json_str)

    # 提取数据
    name = dot_data.get("name", "")
    duration = dot_data.get("duration", 0)
    value = dot_data.get("value", 0)

    return f"{duration}秒伤害{value}每跳的{name}Dot"


# 定义style_function
def style_function(row):
    style = {}
    if row["type"] == "physics":
        style["name"] = "color: #ffa34a;"  # 设置红色样式
    elif row["type"] == "magic":
        style["name"] = "color: #2599be;"  # 设置蓝色样式
    return pd.Series(style)


# 获取副本时间轴数据
def get_raid_table() -> pd.DataFrame:
    raid_list = ["P9S"]
    raid = st.sidebar.selectbox(
        "想要奶茶小散分析什么副本", raid_list, key="raid_choice"
    )
    if not raid:
        st.title("还未支持这个本/这个不是副本！")
        return pd.DataFrame()

    # 加载副本时间轴数据
    raid_df = load_data(os.path.join(resources_dir, "raid_timeline", f"{raid}.csv"))

    # 创建 display_df 作为可编辑的副本数据副本
    display_df = raid_df.copy()

    # 显示 DataFrame
    st.dataframe(
        display_df.style.apply(style_function, axis=1, subset=["name", "type"]).format(
            formatter=parse_dot_json, subset=["extra_info"], na_rep="-"
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
