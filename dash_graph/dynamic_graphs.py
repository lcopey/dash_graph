from dataclasses import dataclass
from types import MappingProxyType
from typing import Dict, List, Tuple

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, html

from .parallel import parallel
from .radar_chart import radar_chart


@dataclass(frozen=True)
class ControlAttribute:
    name: str
    label: str
    kwargs: str
    multi: bool = False


class SequenceOfControls(tuple):
    def __new__(cls, iterable):
        items = {}
        for item in iterable:
            assert isinstance(item, ControlAttribute)
            items[item.name] = item

        instance = super().__new__(cls, iterable)
        instance._items = MappingProxyType(items)
        return instance

    def __getitem__(self, key) -> ControlAttribute:
        if isinstance(key, (int, slice)):
            return super().__getitem__(key)
        elif isinstance(key, str):
            return self._items[key]

    @property
    def names(self) -> Tuple[str]:
        return tuple(item.name for item in self)

    @property
    def labels(self) -> Tuple[str]:
        return tuple(item.label for item in self)

    @property
    def kwargs(self) -> Tuple[str]:
        return tuple(item.kwargs for item in self)


class BaseIds:
    def __init__(self, aio_id: str):
        self.aio_id = aio_id

    def generate_id(self, subcomponent: str):
        return f'{self.aio_id}-{subcomponent}'


CONTROLS = SequenceOfControls(
    [ControlAttribute('xaxis', 'x-axis :', 'x'),
     ControlAttribute('yaxis', 'y-axis :', 'y'),
     ControlAttribute('values', 'Values :', 'values'),
     ControlAttribute('names', 'Names :', 'names'),
     ControlAttribute('dimensions', 'Dimensions : ', 'dimensions', multi=True),
     ControlAttribute('color', 'Legend :', 'color'),]
)

FIGURES = {'bar': px.bar, 'scatter': px.scatter, 'line': px.line, 'pie': px.pie,
           'parallel': parallel,
           'radar': radar_chart}
CONTROLS_PER_CHART_TYPE = {'bar': ['xaxis', 'yaxis', 'color'],
                           'scatter': ['xaxis', 'yaxis', 'color'],
                           'line': ['xaxis', 'yaxis', 'color'],
                           'pie': ['values', 'names'],
                           'parallel': ['dimensions', 'color'],
                           'radar': ['dimensions', 'color']}


def get_select_component(group_id: str,
                         select_id: str,
                         label: str,
                         options: List[Dict[str, str]
                                       ] | List[str] | None = None,
                         value: str | None = None,
                         multi: bool = False):
    input_group = dbc.InputGroupText(label, style={'width': '40%'})
    if multi:
        select = dcc.Dropdown(id=select_id, multi=True,
                              style={'width': 'auto'})
    else:
        select = dbc.Select(id=select_id, options=options, value=value)
    return dbc.InputGroup(id=group_id, children=(input_group, select))


class DashGraphIds(BaseIds):
    def select(self, name: str, group_level: bool = False):
        if group_level:
            name = f'{name}-group'
        return self.generate_id(name)

    def figure(self):
        return self.generate_id('figure')

    def chart_type(self, group_level: bool = False):
        return self.select('chart_type', group_level)


class DashGraphAIO(html.Div):

    def _select(self, name: str, options=None, value=None):
        group_id = self.ids.select(name, True)
        select_id = self.ids.select(name, False)
        label = CONTROLS[name].label
        return get_select_component(group_id=group_id,
                                    select_id=select_id,
                                    label=label,
                                    options=options,
                                    value=value,
                                    multi=CONTROLS[name].multi)

    def __init__(self, aio_id: str, source_store_id: str):
        self.ids = DashGraphIds(aio_id=aio_id)

        figure = dcc.Graph(id=self.ids.figure())
        chart_type = get_select_component(group_id=self.ids.chart_type(True),
                                          select_id=self.ids.chart_type(False),
                                          label='Chart type :',
                                          options=list(FIGURES.keys()),
                                          value='bar')

        chart_controls = [self._select(name) for name in CONTROLS.names]

        layout = dbc.Row(
            [
                dbc.Col([chart_type, *chart_controls], width=4),
                dbc.Col(figure, width=8)]
        )
        super().__init__(layout)

        @callback(
            [Output(self.ids.select(name), 'options')
             for name in CONTROLS.names],
            Input(source_store_id, 'data')
        )
        def synchronize_selection(data):
            data = pd.DataFrame(data)
            selection = [{'value': c, 'label': c} for c in data.columns]
            return (selection,) * len(CONTROLS)

        @callback(
            [Output(self.ids.select(name, True), 'style')
             for name in CONTROLS.names],
            Input(self.ids.chart_type(), 'value'))
        def update_control_visibility(chart_type_value):
            controls = CONTROLS_PER_CHART_TYPE[chart_type_value]
            displayed = [{'display': 'none' if name not in controls else 'flex'}
                         for name in CONTROLS.names]
            return displayed

        @callback(
            Output(figure, 'figure'),
            Input(self.ids.chart_type(), 'value'),
            State(source_store_id, 'data'),
            [Input(self.ids.select(name), 'value') for name in CONTROLS.names]
        )
        def update_graph(chart_type_value, data, *args):
            if chart_type_value:
                data = pd.DataFrame(data)
                kwargs = dict(zip(CONTROLS.kwargs, args))
                # select relevant options
                for name in CONTROLS.names:
                    if name not in CONTROLS_PER_CHART_TYPE[chart_type_value]:
                        kwargs.pop(CONTROLS[name].kwargs)
                if any(kwargs.values()):
                    func = FIGURES[chart_type_value]
                    return func(data, **kwargs)
            return go.Figure()
