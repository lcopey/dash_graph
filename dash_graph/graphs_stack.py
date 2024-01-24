from dash import (html, dcc, ALL, MATCH, callback,
                  Input, Output, State, callback_context, no_update)
import plotly.graph_objects as go
import numpy as np


def format_selection(selection) -> np.ndarray:
    if selection and 'points' in selection:
        return np.array([point['customdata'][0] for point in selection['points']])


def select_points(figure: dict, selected_points: np.ndarray | None):
    for trace in figure['data']:
        ids = np.array(trace['customdata'])[:, 0]
        if selected_points is not None:
            trace_selection, = np.where(np.isin(ids, selected_points))
            trace.update({'selectedpoints': trace_selection})
        else:
            trace.pop('selectedpoints', None)

    return figure


class GraphStack(html.Div):
    def __init__(self, aio_id: str, *figures: go.Figure):
        layout = [
            dcc.Graph(id={'type': 'figure', 'index': n}, figure=fig)
            for n, fig in enumerate(figures)
        ]
        super().__init__(id=aio_id, children=layout)

        @callback(
            Output({'type': 'figure', 'index': ALL}, 'figure'),
            Input({'type': 'figure', 'index': ALL}, 'selectedData'),
            State({'type': 'figure', 'index': ALL}, 'figure'),
        )
        def select(selected, figures):
            triggered_id = callback_context.triggered_id
            if triggered_id:
                triggered_index = triggered_id['index']
                selected_points = format_selection(selected[triggered_index])

                return [select_points(figure, selected_points) for figure in figures]
            return no_update
