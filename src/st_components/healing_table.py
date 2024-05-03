from io import BytesIO

import pandas as pd
import streamlit as st
from .utils import members


def upload_file() -> pd.DataFrame:
    """
    上传并读取奶轴文件。

    Returns:
        pd.DataFrame: 读取的奶轴数据。
    """
    uploaded_file = st.sidebar.file_uploader("在这里上传你的奶轴")
    if not uploaded_file:
        st.write("没有奶轴的话, 奶茶小散也没法虚空分析呀")
        return pd.DataFrame()

    return pd.read_excel(uploaded_file, engine="openpyxl")


def edit_healing_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    编辑奶轴 DataFrame。

    Args:
        df (pd.DataFrame): 待编辑的 DataFrame。

    Returns:
        pd.DataFrame: 编辑后的 DataFrame。
    """
    res = st.data_editor(
        df,
        key="healing_df_editor",
        num_rows="dynamic",
        use_container_width=True,
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
    return res


def download_healing_df():
    """
    保存编辑后的奶轴 DataFrame，并提供下载按钮。

    Args:
        df (pd.DataFrame): 编辑后的 DataFrame。
    """

    # 定义一个下载文件的回调函数
    def to_excel():
        # 使用 pandas 的 to_excel 方法将 DataFrame 保存为 Excel 文件
        buffer = BytesIO()
        st.session_state["healing_df"].to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer

    if "healing_df" in st.session_state:
    # 使用 Streamlit 的 download_button 组件提供下载按钮
        st.download_button(
            label="下载奶轴",
            data=to_excel(),
            file_name="edited_healing_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def get_healing_table() -> pd.DataFrame:
    """
    获取并编辑奶轴数据。

    Returns:
        pd.DataFrame: 编辑后的奶轴数据。
    """
    # 上传文件并读取数据
    df = upload_file()

    # 如果没有上传文件，返回空的 DataFrame
    if df.empty:
        return df

    # 编辑数据
    edited_df = edit_healing_df(df)

    # 保存编辑后的数据
    download_healing_df()

    # 更新 session state 中的奶轴 DataFrame
    st.session_state["healing_df"] = edited_df

    return edited_df
