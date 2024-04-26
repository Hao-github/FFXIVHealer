from collections import defaultdict
from typing import Any
from pyecharts.charts import Timeline, Bar, Line
from pyecharts.commons.utils import JsCode
import pyecharts.options as opts
from models.player import Player

js_string = """
        function (params) {
            console.log(params);
            let ret = `time: ${params[0].axisValue}<br/>event: pass<br/>`;
            for (let i = 0; i < params.length; i++) {
                ret += `${params[i].seriesName}: ${params[i].data[1]} (${params[i].data[2]})`;
                if (i < params.length - 1) {
                    ret += '<br/>';
                }
            }
            return ret;
        }
"""


class Output:
    output = open("output.txt", "w", encoding="utf-8")
    timeline = Timeline()
    x: list[float] = []
    y: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    @classmethod
    def info(cls, info: str):
        cls.output.write(info)

    @classmethod
    def addSnapshot(cls, time: float, playerList: dict[str, Player]):
        cls.x.append(round(time, 2))
        for name, player in playerList.items():
            cls.y[name].append({"hp": player.hp, "status": f"[{player.statusList}]"})

    @classmethod
    def addBar(cls, timeStr: str, playerList: dict[str, Player]):
        cls.timeline.add(
            Bar(init_opts=opts.InitOpts(width="900px", height="500px"))
            .add_xaxis(
                list(map(lambda x: f"{x[0]}-{x[1].name}", playerList.items())),
            )
            .add_yaxis(
                "hp",
                list(map(lambda x: x.hp, playerList.values())),
                label_opts=opts.LabelOpts(position="top"),
            )
            .add_yaxis(
                "maxHp",
                list(map(lambda x: x.maxHp, playerList.values())),
                label_opts=opts.LabelOpts(is_show=False),
                gap="-100%",
                z=-1,
                itemstyle_opts=opts.ItemStyleOpts(color="rgba(255, 0, 0, 0.5)"),
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts={"rotate": -10},
                ),
                yaxis_opts=opts.AxisOpts(
                    splitline_opts=opts.SplitLineOpts(is_show=False)
                ),
            ),
            timeStr,
        )

    @classmethod
    def showBar(cls):
        cls.timeline.render()

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
                textstyle_opts=opts.TextStyleOpts(
                    font_family="Courier New",  # 设置等宽字体
                    font_weight="bold",  # 设置字体为粗体
                    font_size=14,  # 根据需要调整字体大小
                ),
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
        ).render("testasdf.html")
        # pass
