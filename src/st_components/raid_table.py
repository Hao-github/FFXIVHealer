import os

import pandas as pd
import streamlit as st
from .utils import load_data, resources_dir


def get_raid_table() -> pd.DataFrame:
    raid_list = ["P9S"]
    raid = st.sidebar.selectbox("想要奶茶小散分析什么副本", raid_list)
    if not raid:
        st.title("还未支持这个本/这个不是副本！")
        return pd.DataFrame()
    raid_df = load_data(os.path.join(resources_dir, "raid_timeline", f"{raid}.csv"))
    st.dataframe(raid_df, use_container_width=True, hide_index=True)
    return raid_df
