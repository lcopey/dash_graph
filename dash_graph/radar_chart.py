from typing import List

import pandas as pd
import plotly.express as px


def radar_chart(
    dataframe: pd.DataFrame,
    dimensions: List[str],
    color: str | None = None,
):
    if color:
        id_vars = ["index", color]
    else:
        id_vars = "index"

    dataframe = dataframe.copy()
    dataframe = (
        dataframe.rename_axis("index")
        .reset_index()
        .melt(id_vars=id_vars, value_vars=dimensions)
    )
    return px.line_polar(
        dataframe,
        r="value",
        theta="variable",
        line_group="index",
        line_close=True,
        color=color,
    )
