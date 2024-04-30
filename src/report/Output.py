from dataclasses import dataclass, field
from typing import Any
from pyecharts.charts import Line
from pyecharts.commons.utils import JsCode
import pyecharts.options as opts
import os

from ..models.player import Player
from ..models.Event import Event

project_root = os.path.dirname(os.path.abspath(__file__))

js_string = """
function customTooltip(params) {
    console.log(params);
    let tooltipContent = `time: ${params[0].axisValue}<br/>event: pass<br/>`;
    params.forEach((param, index) => {
        const hpSpan = `<span style="font-family: 'EurostarRegularExtended'; font-size: 14px; vertical-align: middle; width: 70px; display: inline-block; text-align: left;">${param.data[1]}</span>`;
        const jobImage = `<img src="app/static/images/job/${param.data[3]}.png" alt="${param.seriesName}" style="width: 20px; height: 20px;">`;
        const skillDetails = Object.entries(param.data[2])
            .map(([skillName, remainingTime]) => {
                const imgTag = `<img src="app/static/images/skill/${skillName}.png" alt="${skillName}" style="width: 15px; height: 20px;">`;
                const remainingTimeSpan = `<span style="display: block; margin-top: -10px; font-size: 12px;">${remainingTime.toFixed(1)}</span>`;
                return `<div style="display: inline-block; text-align: center; margin-right: 5px; vertical-align: middle; width: 25px">${imgTag}${remainingTimeSpan}</div>`;
            })
            .join('');

        tooltipContent += `${jobImage}: ${hpSpan} ${skillDetails}`;


        if (index < params.length - 1) {
            tooltipContent += '<br/>';
        }
    });
    return tooltipContent;
}
"""


@dataclass
class Snapshot:
    time: float
    event: Event
    player_info: dict[str, Any] = field(default_factory=dict)


class Output:
    def __init__(self) -> None:
        self.output = open("output.txt", "w", encoding="utf-8")
        self.snapshot_list: list[Snapshot] = []

    def info(self, info: str):
        self.output.write(info)

    def add_snapshot(self, time: float, player_list: dict[str, Player], event: Event):
        player_info = {
            name: {"hp": player.hp, "extra": player.remaining_status, "job": player.job}
            for name, player in player_list.items()
        }
        self.snapshot_list.append(Snapshot(round(time, 2), event, player_info))

    def show_line(self) -> Line:
        time_list = [snapshot.time for snapshot in self.snapshot_list]
        result = Line().add_xaxis(time_list)

        for player in self.snapshot_list[0].player_info.keys():
            result.add_yaxis(
                series_name=player,
                y_axis=[
                    snapshot.player_info[player] for snapshot in self.snapshot_list
                ],
                label_opts=opts.LabelOpts(is_show=False),
                is_symbol_show=False,
            )

        result.set_global_opts(
            title_opts=opts.TitleOpts(title="血量模拟", subtitle="v0.0.1"),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter=JsCode(js_string),
                textstyle_opts=opts.TextStyleOpts(font_family="AxisStdExtralight"),
                position=JsCode("""
                function (point, params, dom, rect, size) {
                    return ['10%', '10%']
                }"""),
            ),
            xaxis_opts=opts.AxisOpts(
                type_="value", min_=time_list[0], max_=time_list[-1]
            ),
            datazoom_opts=opts.DataZoomOpts(
                is_zoom_lock=False,
                type_="inside",
                range_start=0,
                range_end=100,
                orient="horizontal",
            ),
        ).add_js_funcs("""
        var style = document.createElement('style');
        style.type = 'text/css';
        style.innerHTML = `
            @font-face {
                font-family: 'EurostarRegularExtended';
                src: url('resources/fonts/eurostarregularextended.ttf') format('truetype');
            }
            @font-face {
                font-family: 'AxisStdExtralight';
                src: url('resources/fonts/axisstd-extralight.otf') format('opentype');
            }
        `;
        document.head.appendChild(style);
        """)
        
        return result

    # @classmethod
    # def show_txt_output(self):
    #     for snapshot in self.snapshot_list:
    #         if snapshot.event.name_is("naturalHeal"):
    #             continue
    #         Output.info(
    #             f"After Event {snapshot.event.name} At {self.__fromTimestamp(snapshot.time)}\n"
    #         )
    #         # for
    #         # Output.info(f"{name}-{str(player)}")
    #     pass

    # @staticmethod
    # def __fromTimestamp(rawTime: float) -> str:
    #     begin = ""
    #     if rawTime < 0:
    #         begin = "-"
    #         rawTime = -rawTime
    #     return f"{begin}{int(rawTime // 60)}:{round(rawTime % 60, 3)}"
