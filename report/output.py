from collections import defaultdict
from typing import Any
from pyecharts.charts import Line
from pyecharts.commons.utils import JsCode
import pyecharts.options as opts
from models.player import Player

js_string = """
function customTooltip(params) {
    console.log(params);
    let tooltipContent = `time: ${params[0].axisValue}<br/>event: pass<br/>`;
    params.forEach((param, index) => {
        const hpSpan = `<span style="font-family: 'EurostarRegularExtended'; font-size: 14px; vertical-align: middle; width: 70px; display: inline-block; text-align: left;">${param.data[1]}</span>`;
        const jobImage = `<img src="img/job/${param.data[3]}.png" alt="${param.seriesName}" style="width: 20px; height: 20px;">`;
        const skillDetails = Object.entries(param.data[2])
            .map(([skillName, remainingTime]) => {
                const imgTag = `<img src="img/skill/${skillName}.png" alt="${skillName}" style="width: 20px; height: 20px;">`;
                const remainingTimeSpan = `<span style="display: block; margin-top: -10px; font-size: 12px;">${remainingTime.toFixed(1)}</span>`;
                return `<div style="display: inline-block; text-align: center; margin-right: 5px; vertical-align: middle; width: 30px">${imgTag}${remainingTimeSpan}</div>`;
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


class Output:
    output = open("output.txt", "w", encoding="utf-8")
    x: list[float] = []
    y: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    @classmethod
    def info(cls, info: str):
        cls.output.write(info)

    @classmethod
    def add_snapshot(cls, time: float, player_list: dict[str, Player]):
        cls.x.append(round(time, 2))
        for name, player in player_list.items():
            cls.y[name].append(
                {
                    "hp": player.hp,
                    "extra": player.status_list.get_remaining_times(),
                    "job": player.job,
                }
            )

    @classmethod
    def showLine(cls):
        line_chart = Line().add_xaxis(cls.x)

        for k, v in cls.y.items():
            line_chart.add_yaxis(
                series_name=k,
                y_axis=v,
                label_opts=opts.LabelOpts(is_show=False),
                is_symbol_show=False,
            )

        line_chart.set_global_opts(
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
                type_="value",
                min_=cls.x[0],
                max_=cls.x[-1],
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
                src: url('fonts/eurostarregularextended.ttf') format('truetype');
            }
            @font-face {
                font-family: 'AxisStdExtralight';
                src: url('fonts/axisstd-extralight.otf') format('opentype');
            }
        `;
        document.head.appendChild(style);
        """).render()
