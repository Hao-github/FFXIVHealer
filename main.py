import streamlit as st
from streamlit.components.v1 import html

from src.Simulation import Simulation
from src.st_components.players_expander import get_players_df
from src.st_components.raid_tab import get_raid_table
from src.st_components.healing_tab import get_healing_table
from src.st_components.st_utils import translate_df


def main():
    raid_tab, healing_tab, result_tab, other_tab = st.tabs(
        ["BOSS时间轴", "奶轴编辑", "结果折线图", "其他事项"]
    )

    with raid_tab:
        raid_df = get_raid_table()
        if raid_df.empty:
            return

    with healing_tab:
        healing_df = get_healing_table()
        if healing_df.empty:
            return

    click_run = st.sidebar.button("RUN!", type="primary")
    player_df = get_players_df()

    if click_run:
        output, evaluation = (
            Simulation(player_df)
            .add_raid_timeline(raid_df)
            .add_healing_timeline(healing_df.merge(translate_df, on="name"))
            .run(0.01)
        )
        with result_tab:
            html(output.show_line().render_embed(), width=800, height=600)
        with other_tab:
            st.write("暂时没写好，搁置")
            st.write(evaluation.gcd_cost)
            st.write(evaluation.cooperation)
            st.write(evaluation.tolerance)


if __name__ == "__main__":
    main()
    
