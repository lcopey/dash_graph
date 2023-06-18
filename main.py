import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, dcc, html

# from pivot_graph import DashGraphAIO
# from graphs import DashGraphAIO
from dash_graph import DashGraphAIO

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
datas = pd.read_parquet('./iris.parquet')

store = dcc.Store(id='store', data=datas.to_dict('records'))
dash_graph = DashGraphAIO('main', source_store_id='store')
app.layout = html.Div([dash_graph, store])

if __name__ == '__main__':
    app.run(port=8050, debug=True)
