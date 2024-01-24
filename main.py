import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px

# from pivot_graph import DashGraphAIO
# from graphs import DashGraphAIO
from dash_graph import DashGraphAIO, GraphStack

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
datas = pd.read_parquet('./iris.parquet')
datas['id'] = list(range(datas.shape[0]))

store = dcc.Store(id='store', data=datas.to_dict('records'))
# dash_graph = DashGraphAIO('main', source_store_id='store')
dash_graph = GraphStack(
    'main',
    px.scatter(datas, 'sepal width (cm)', 'sepal length (cm)', custom_data='id'),
    px.scatter(datas, 'petal width (cm)', 'petal length (cm)', custom_data='id')
)
app.layout = html.Div([dash_graph, store])

if __name__ == '__main__':
    app.run(port=8050, debug=True)
