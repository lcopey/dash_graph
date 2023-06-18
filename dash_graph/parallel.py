from typing import List

import pandas as pd
import plotly.graph_objects as go


def _get_dimension(values: pd.Series, label: str):
    kwargs = {}
    if values.dtype == object:
        labels = {value: n for n, value in enumerate(values.unique())}
        values.replace(labels, inplace=True)
        kwargs['tickvals'] = list(labels.values())
        kwargs['ticktext'] = list(labels.keys())

    return go.parcoords.Dimension(values=values, label=label, **kwargs)


def parallel(dataframe: pd.DataFrame,
             dimensions: List[str],
             color: str | None = None,
             color_continuous_scale: str | None = None):
    dataframe = dataframe.copy()
    kwargs = {}
    if color and color not in dimensions:
        dimensions = [*dimensions, color]

    dimensions = [_get_dimension(values=dataframe[col],
                                 label=col) for col in dimensions]
    if color:
        kwargs['line'] = {'color': dataframe[color],
                          'colorscale': color_continuous_scale}
    return go.Figure(go.Parcoords(dimensions=dimensions, **kwargs))
