from utils.figpanel import create_heatmap_with_rmse
from main import app
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd




files = [
    'COSMIC_v1_SBS_GRCh37.txt', 'COSMIC_v2_SBS_GRCh37.txt', 'COSMIC_v3.1_SBS_GRCh37.txt',
    'COSMIC_v3.2_SBS_GRCh37.txt', 'COSMIC_v3.3.1_SBS_GRCh37.txt', 'COSMIC_v3.4_SBS_GRCh37.txt', 'COSMIC_v3_SBS_GRCh37.txt',
    'COSMIC_v1_SBS_GRCh38.txt', 'COSMIC_v2_SBS_GRCh38.txt', 'COSMIC_v3.1_SBS_GRCh38.txt',
    'COSMIC_v3.2_SBS_GRCh38.txt', 'COSMIC_v3.3.1_SBS_GRCh38.txt', 'COSMIC_v3.4_SBS_GRCh38.txt', 'COSMIC_v3_SBS_GRCh38.txt'
]

data = {}

for file in files:
    data[file] = pd.read_csv(f'data/signatures/{file}', sep='\t').columns[1:].to_list()

dropdown_options = [{'label': file, 'value': file} for file in files]


# Application layout
page1_layout = html.Div([
    navbar,
    dbc.Container([
        dbc.Button("Advanced Options", id="toggle-button", className="mb-3", color="dark"),
        dbc.Collapse(
            dbc.Card(dbc.CardBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Distance Metric", html_for="distance-metric"),
                            dcc.Dropdown(
                                id='distance-metric',
                                options=[
                                    {'label': 'Cosine', 'value': 'cosine'},
                                    {'label': 'RMSE', 'value': 'rmse'}
                                ],
                                placeholder="Select distance metric",
                                value='rmse',
                            ),
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Clustering Method", html_for="clustering-method"),
                            dcc.Dropdown(
                                id='clustering-method',
                                options=[
                                    {'label': 'Linkage Algorithm', 'value': 'linkage'}
                                ],
                                placeholder="Select clustering method",
                                value='linkage',
                            ),
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Epsilon", html_for="epsilon"),
                            dbc.Input(
                                type="number",
                                id="epsilon",
                                placeholder="Enter epsilon value",
                                value=10e-4,
                                min=1e-10,  # Minimum value
                                max=1e-2  # Maximum value
                            ),
                        ])
                    ]),
                    dbc.Button("Submit", id="submit-button", className="mt-3", color="primary")
                ])
            ])),
            id="collapse-form"
        ),
        html.Div(id='form-output')
    ], fluid=True),
    dbc.Container([
    dbc.Row([
        dcc.Dropdown(
            id='dropdown-1',
            options=dropdown_options,
            disabled=False,
            value=files[1]
        ),
        dcc.Dropdown(
                id='signatures-dropdown-1',
                options=[{'label': k, 'value': k} for k in data.keys()],
                multi=True,
                value=[k for k in data['COSMIC_v2_SBS_GRCh37.txt']],
            )
    ]),
    dbc.Row([
        dbc.Col([
            html.H5("Signature similarity"),
            dcc.Graph(id='heatmap-plot')
        ]),
        dbc.Col([
            html.H5("RePrint similarity"),
            dcc.Graph(id='heatmap-reprint-plot')
        ])
    ]),
    dcc.Location(id='url-page1', refresh=False),
    dbc.Button("Download TSV", id="btn_csv", className="mt-3", color="dark"),
    dcc.Download(id="download-dataframe-csv")
    ], fluid=True),

])

@app.callback(
    Output("collapse-form", "is_open"),
    [Input("toggle-button", "n_clicks")],
    [State("collapse-form", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

from utils.utils import reprint, calculate_rmse, calculate_cosine
@app.callback(
    [Output('form-output', 'children'),
     Output('heatmap-plot', 'figure'),
     Output('heatmap-reprint-plot', 'figure')],
    [Input('submit-button', 'n_clicks'),
     Input('signatures-dropdown-1', 'value'),
     Input('dropdown-1', 'value')],
    [State('distance-metric', 'value'),
     State('clustering-method', 'value'),
     State('epsilon', 'value')]
)
def update_output(n_clicks, selected_signatures, selected_file, distance_metric, clustering_method, epsilon):
    if n_clicks:
        df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]
        functions = {'rmse': calculate_rmse, 'cosine': calculate_cosine}
        df_reprint = reprint(df_signatures, epsilon=epsilon)
        return (f'Submitted: Distance Metric: {distance_metric}, Clustering Method: {clustering_method}, Epsilon: {epsilon}',
                create_heatmap_with_rmse(df_signatures, calc_func=functions[distance_metric], colorscale='BuPu'),
                create_heatmap_with_rmse(df_reprint, calc_func=functions[distance_metric], colorscale='Blues')
                )
    else:
        df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]

        df_reprint = pd.read_csv(f"data/cosmic_reprints/{selected_file}.reprint", sep='\t', index_col=0)[selected_signatures]

        return (f'Distance Metric: {distance_metric}, Clustering Method: {clustering_method}, Epsilon: {epsilon}',
                create_heatmap_with_rmse(df_signatures, colorscale='BuPu'),
                create_heatmap_with_rmse(df_reprint, colorscale='Blues')
                )

@app.callback(
    [Output('signatures-dropdown-1', 'options'),
     Output('signatures-dropdown-1', 'value')],
    [Input('dropdown-1', 'value')]
)
def set_options(selected_category):
    return [{'label': f"{i}", 'value': i} for i in data[selected_category]], [i for i in data[selected_category]]

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    [State('signatures-dropdown-1', 'value'),
     State('dropdown-1', 'value'),
     State('epsilon', 'value')],
    prevent_initial_call=True
)
def func(n_clicks, selected_signatures, selected_file, epsilon):
    df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]
    df_reprint = reprint(df_signatures, epsilon=epsilon)
    return dcc.send_data_frame(df_reprint.to_csv, filename="data.csv")