from utils.figpanel import create_heatmap_with_custom_sim
from utils.utils import FILES, DEFAULT_SIGNATURES
from main import app
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd



data = {}
for file in FILES:
    data[file] = pd.read_csv(f'data/signatures/{file}', sep='\t').columns[1:].to_list()

dropdown_options = [{'label': file, 'value': file} for file in FILES]
linkage_methods = ['single', 'complete', 'average', 'ward']


# Application layout
page1_layout = html.Div([
    navbar,
    dbc.Container([
        dbc.Card(
            [
                dbc.CardHeader("Actions"),
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Button(
                                        "Advanced Options",
                                        id="toggle-button",
                                        color="dark",
                                        className="w-100"
                                    ),
                                    dbc.Tooltip(
                                        "Show or hide advanced settings",
                                        target="toggle-button",
                                        placement="bottom"
                                    )
                                ],
                                width=2
                            ),
                            dbc.Col(
                                [
                                    dbc.Button(
                                        "Download Reprints",
                                        id="btn_csv-1",
                                        color="info",
                                        className="w-100"
                                    ),
                                    dbc.Tooltip(
                                        "Download CSV file with reprint data",
                                        target="btn_csv-1",
                                        placement="bottom"
                                    )
                                ],
                                width=2
                            ),
                            dbc.Col(
                                [
                                    dbc.Button(
                                        "Run Analysis",
                                        id="submit-button",
                                        color="primary",
                                        className="w-100"
                                    ),
                                    dbc.Tooltip(
                                        "Start the analysis pipeline",
                                        target="submit-button",
                                        placement="bottom"
                                    )
                                ],
                                width=2
                            ),
                        ],
                        className="mb-3",
                        align="center"
                    )
                )
            ],
            className="mb-4 shadow"
        ),
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
                                options=[{'label': method.title(), 'value': method} for method in linkage_methods],
                                placeholder="Select clustering method",
                                value='single',
                                clearable=False,
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
            value=DEFAULT_SIGNATURES
        ),
        dcc.Dropdown(
                id='signatures-dropdown-1',
                options=[{'label': k, 'value': k} for k in data.keys()],
                multi=True,
                value=[k for k in data[DEFAULT_SIGNATURES]],
            )
    ]),
        dbc.Alert(
        [
            html.H5("Expected File Format", style={"font-size": "18px", "font-weight": "bold"}),
            html.P("The uploaded file should be a tab-separated file (.txt) containing mutation types and corresponding mutation signatures.",
                style={"font-size": "14px"}),
            html.P("Columns:", style={"font-size": "14px", "margin-bottom": "5px"}),
            html.Ul([
                html.Li("Type: Mutation type (e.g., A[C>A]A, A[C>A]C, ...).", style={"font-size": "13px"}),
                html.Li("SBS1, SBS2, ..., SBSN: Signature mutation values (frequencies or probabilities).", style={"font-size": "13px"})
            ], style={"padding-left": "20px", "margin-bottom": "5px"}),
            html.P("Example first few rows:", style={"font-size": "14px", "margin-bottom": "5px"}),
            html.Pre(
                "Type\tSBS1\tSBS2\tSBS3\n"
                "A[C>A]A\t0.001\t0.002\t0.003\n"
                "A[C>A]C\t0.004\t0.005\t0.006",
                style={"white-space": "pre-wrap", "font-family": "monospace", "font-size": "12px", "background-color": "#f8f9fa", "padding": "5px"}
            ),
        ],
        color="info",
        dismissable=True,
        style={"font-size": "14px", "padding": "10px"}
    ),
    dcc.Upload(
            id='upload-data-1-signatures',
            children=html.Div(['Drag and drop your signatures']),
            style={
                'width': '300px',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),

    html.Div(id='info_uploader'),
    dcc.Store(id='session-1-signatures', storage_type='session', data=None),
    dbc.Row([
        dbc.Col(html.Label("Hide Heatmap:", className="h5"), width="auto"),
        dbc.Col(
            dbc.Switch(
                id="toggle-heatmap",
                value=False,
                label="On/Off",
                className="mb-3"
            ),
            width="auto"
        ),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            html.H5("Signature similarity"),
            dcc.Loading(
                id="loading-heatmap-plot",
                type="default",
                children=dcc.Graph(id='heatmap-plot')
            )
        ]),
        dbc.Col([
            html.H5("RePrint similarity"),
            dcc.Loading(
                id="loading-heatmap-reprint-plot",
                type="default",
                children=dcc.Graph(id='heatmap-reprint-plot')
            )
        ])
    ]),
    dcc.Location(id='url-page1', refresh=False),
    dcc.Download(id="download-dataframe-csv-1")
    ], fluid=True),

])

from utils.utils import parse_signatures
import dash

@app.callback(
    [Output('session-1-signatures', 'data')],
    [Input('upload-data-1-signatures', 'contents')],
    [State('upload-data-1-signatures', 'filename')]
)
def update_output_signatures(contents, filename):
    if contents is not None:
        df_signatures = parse_signatures(contents, filename)

        signatures_info = "Some information extracted from df_signatures"
        return [{'signatures_data': df_signatures.to_dict('records'), 'filename': filename, 'info': signatures_info}]
    else:
        return dash.no_update

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
     Input("toggle-heatmap", "value"),
    [State('distance-metric', 'value'),
     State('clustering-method', 'value'),
     State('epsilon', 'value'),
     State('session-1-signatures', 'data'),
     ]
)
def update_output(n_clicks, selected_signatures, selected_file, hide_heatmap, distance_metric, clustering_method, epsilon, signatures):
    if n_clicks:
        if signatures is not None:
            data = pd.DataFrame(signatures['signatures_data'])
            data.index = data['Type']
            data = data.drop(columns='Type')[selected_signatures]
            functions = {'rmse': calculate_rmse, 'cosine': calculate_cosine}
            df_reprint = reprint(data, epsilon=epsilon)
            return (f'Submitted: Distance Metric: {distance_metric}, Clustering Method: {clustering_method}, Epsilon: {epsilon}',
                    create_heatmap_with_custom_sim(data, calc_func=functions[distance_metric], colorscale='BuPu', hide_heatmap=hide_heatmap, method=clustering_method),
                    create_heatmap_with_custom_sim(df_reprint, calc_func=functions[distance_metric], colorscale='Blues', hide_heatmap=hide_heatmap, method=clustering_method)
                    )
        else:
            df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]
            functions = {'rmse': calculate_rmse, 'cosine': calculate_cosine}
            df_reprint = reprint(df_signatures, epsilon=epsilon)
            return (f'Submitted: Distance Metric: {distance_metric}, Clustering Method: {clustering_method}, Epsilon: {epsilon}',
                    create_heatmap_with_custom_sim(df_signatures, calc_func=functions[distance_metric], colorscale='BuPu', hide_heatmap=hide_heatmap, method=clustering_method),
                    create_heatmap_with_custom_sim(df_reprint, calc_func=functions[distance_metric], colorscale='Blues', hide_heatmap=hide_heatmap, method=clustering_method)
                    )
    else:
        if signatures is not None:
            data = pd.DataFrame(signatures['signatures_data'])
            data.index = data['Type']
            data = data.drop(columns='Type')[selected_signatures]
            functions = {'rmse': calculate_rmse, 'cosine': calculate_cosine}
            df_reprint = reprint(data, epsilon=epsilon)
            return (f'Submitted: Distance Metric: {distance_metric}, Clustering Method: {clustering_method}, Epsilon: {epsilon}',
                    create_heatmap_with_custom_sim(data, calc_func=functions[distance_metric], colorscale='BuPu', hide_heatmap=hide_heatmap, method=clustering_method),
                    create_heatmap_with_custom_sim(df_reprint, calc_func=functions[distance_metric], colorscale='Blues', hide_heatmap=hide_heatmap, method=clustering_method)
                    )
        else:
            df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]
            df_reprint = pd.read_csv(f"data/cosmic_reprints/{selected_file}.reprint", sep='\t', index_col=0)[selected_signatures]

            return (f'Distance Metric: {distance_metric}, Clustering Method: {clustering_method}, Epsilon: {epsilon}',
                    create_heatmap_with_custom_sim(df_signatures, colorscale='BuPu', hide_heatmap=hide_heatmap, method=clustering_method),
                    create_heatmap_with_custom_sim(df_reprint, colorscale='Blues', hide_heatmap=hide_heatmap, method=clustering_method)
                    )

@app.callback(
    [Output('signatures-dropdown-1', 'options'),
     Output('signatures-dropdown-1', 'value'),
     Output('dropdown-1', 'style'),
     Output('info_uploader', 'children')
     ],
    [Input('dropdown-1', 'value'),
     Input('session-1-signatures', 'data')]
)
def set_options(selected_category, contents):
    if contents is not None:
        df = pd.DataFrame(contents['signatures_data'])
        df.index = df['Type']
        df = df.drop(columns='Type')
        signatures = df.columns.to_list()
        return (
            [{'label': signature, 'value': signature} for signature in signatures],
            signatures,
            {'display': 'None'},
            f'Added your signatures {contents["filename"]}')

    return ([{'label': f"{i}", 'value': i} for i in data[selected_category]],
            [i for i in data[selected_category]],
            {'display': 'block'},
            'Not Uploaded')


@app.callback(
    Output("download-dataframe-csv-1", "data"),
    Input("btn_csv-1", "n_clicks"),
    [State('signatures-dropdown-1', 'value'),
     State('dropdown-1', 'value'),
     State('epsilon', 'value'),
     State('session-1-signatures', 'data')],
    prevent_initial_call=True
)
def download_dataframe(n_clicks, selected_signatures, selected_file, epsilon, contents):
    if contents is not None:
        df_signatures = pd.DataFrame(contents['signatures_data'])
        df_signatures.index = df_signatures['Type']
        df_signatures = df_signatures.drop(columns='Type')[selected_signatures]
        df_reprint = reprint(df_signatures, epsilon=epsilon)

        df_reprint.columns = [f"reprint_{col}" for col in df_reprint.columns]

        return dcc.send_data_frame(df_reprint.to_csv, filename="reprints.csv")
    else:
        df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]
        df_reprint = reprint(df_signatures, epsilon=epsilon)

        df_reprint.columns = [f"reprint_{col}" for col in df_reprint.columns]

        return dcc.send_data_frame(df_reprint.to_csv, filename="reprints.csv")


