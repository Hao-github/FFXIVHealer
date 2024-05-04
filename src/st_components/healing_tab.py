import pandas as pd
import streamlit as st

from src.st_components.database_handler import DatabaseHandler
from .st_utils import members


def upload_file(db_handler: DatabaseHandler) -> pd.DataFrame:
    """
    上传并读取奶轴文件。

    Returns:
        pd.DataFrame: 读取的奶轴数据。
    """
    uploaded_file = st.sidebar.file_uploader("在这里上传你的奶轴")
    if not uploaded_file:
        
        # st.write("没有奶轴的话, 奶茶小散也没法虚空分析呀")
        return db_handler.query("SELECT * FROM test_healing_timeline")

    return pd.read_excel(uploaded_file, engine="openpyxl")


def edit_healing_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    编辑奶轴 DataFrame。

    Args:
        df (pd.DataFrame): 待编辑的 DataFrame。

    Returns:
        pd.DataFrame: 编辑后的 DataFrame。
    """
    return st.data_editor(
        df,
        key="healing_df_editor",
        num_rows="dynamic",
        use_container_width=True,
        column_order=["time", "name", "user", "target", "duration", "kwargs"],
        column_config={
            "user": st.column_config.SelectboxColumn(
                "释放者",
                options=members,
                required=True,
            ),
            "target": st.column_config.SelectboxColumn(
                "目标",
                options=members,
                help="不填入目标, 则默认为以释放者为目标; 群体技能和状态类(如秘策)技能无需填入目标",
            ),
            "time": st.column_config.TextColumn(
                "释放时间",
                help="填入的时间格式为 xx:yy.zzz，否则无法填入",
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
    )


def get_healing_table(db_handler: DatabaseHandler) -> pd.DataFrame:
    """
    获取并编辑奶轴数据。

    Returns:
        pd.DataFrame: 编辑后的奶轴数据。
    """
    # 上传文件并读取数据
    df = upload_file(db_handler)

    # 如果没有上传文件，返回空的 DataFrame
    if df.empty:
        return df

    # 编辑数据
    edited_df = edit_healing_df(df)

    # 更新 session state 中的奶轴 DataFrame
    if st.button("Save", key="save_healing_timeline"):
        st.session_state["healing_df"] = edited_df
        db_handler.add_to_database(df, "test_healing_timeline")
    return edited_df
