from utils.figpanel import create_main_dashboard
from dash import dcc, html
from main import app
from dash import Input, Output, State
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd
from utils.utils import FILES, DEFAULT_SIGNATURES, reprint, parse_signatures
import dash


data = {}

for file in FILES:
    data[file] = pd.read_csv(f'data/signatures/{file}', sep='\t').columns[1:].to_list()

dropdown_options = [{'label': file, 'value': file} for file in FILES]

# Application layout
page2_layout = html.Div([
    navbar,
    dcc.Interval(id='initial-load', interval=1000, n_intervals=0, max_intervals=1),
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
                                id="toggle-button-2",
                                color="dark",
                                className="w-100"
                            ),
                            dbc.Tooltip(
                                "Show or hide advanced settings",
                                target="toggle-button-2",
                                placement="bottom"
                            )
                        ],
                        width=2
                    ),
                    dbc.Col(
                        [
                            dbc.Button(
                                "Download Reprints",
                                id="btn_csv-2",
                                color="info",
                                className="w-100"
                            ),
                            dbc.Tooltip(
                                "Download CSV file with reprint data",
                                target="btn_csv-2",
                                placement="bottom"
                            )
                        ],
                        width=2
                    ),
                    dbc.Col(
                        [
                            dbc.Button(
                                "Download Signatures",
                                id="btn_csv-signatures-2",
                                color="secondary",
                                className="w-100"
                            ),
                            dbc.Tooltip(
                                "Download CSV file with selected signature data",
                                target="btn_csv-signatures-2",
                                placement="bottom"
                            )
                        ],
                        width=2
                    ),
                    dbc.Col(
                        [
                            dbc.Button(
                                "Generate Plots",
                                id="reload-button",
                                color="success",
                                className="w-100"
                            ),
                            dbc.Tooltip(
                                "Regenerate visualizations based on selected data",
                                target="reload-button",
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
                        dbc.Label("Epsilon", html_for="epsilon-2"),
                        dbc.Input(
                            type="number",
                            id="epsilon-2",
                            placeholder="Enter epsilon value",
                            value=10e-4,
                            min=1e-10,  # Minimum value
                            max=1e-2  # Maximum value
                        ),
                    ])
                ]),
            ])
        ])),
        id="collapse-form-2"
    ),
    dbc.Row([
        dcc.Dropdown(
            id='dropdown-2',
            options=dropdown_options,
            disabled=False,
            value=DEFAULT_SIGNATURES
        ),
        dcc.Dropdown(
                id='signatures-dropdown-2',
                options=[{'label': k, 'value': k} for k in data.keys()],
                multi=True,
                value=[k for k in data[DEFAULT_SIGNATURES]],
            ),
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
            id='upload-data-2-signatures',
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
    html.Div(id='upload-error-message-1'),
    html.Div(id='info_uploader-2'),
    dcc.Store(id='session-2-signatures', storage_type='session', data=None),
    dcc.Location(id='url-page2', refresh=False),
    dcc.Loading(
        id="loading-graphs",
        type="default",
        children=html.Div(id='plots-container-2')
    )
    ], fluid=True),
    dcc.Download(id="download-dataframe-csv-2"),
    dcc.Download(id="download-dataframe-csv-signatures-2"),
    dcc.Store(id='plots-page-store', data=0),    # stores the page number
    html.Div(id='plots-navigation', className='mb-3'),  # pagination buttons
    html.Div(id='plots-container-2')
])

@app.callback(
    Output('plots-page-store', 'data'),
    Input('prev-page-btn', 'n_clicks'),
    Input('next-page-btn', 'n_clicks'),
    State('plots-page-store', 'data'),
    prevent_initial_call=True
)
def update_page(prev_clicks, next_clicks, current_page):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'prev-page-btn' and current_page > 0:
        return current_page - 1
    elif trigger == 'next-page-btn':
        return current_page + 1
    return current_page

@app.callback(
    Output('plots-container-2', 'children'),
    Output('plots-navigation', 'children'),
    [Input('initial-load', 'n_intervals'),
     Input('dropdown-2', 'value'),
     Input('reload-button', 'n_clicks'),
     Input('plots-page-store', 'data')],
    [State('signatures-dropdown-2', 'value'),
     State('session-2-signatures', 'data')]
)
def update_graph(init_load, selected_file, n_clicks, current_page, selected_signatures, signatures):
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = 'initial-load'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id in ['initial-load', 'reload-button', 'plots-page-store']:
        if not selected_signatures or not selected_file:
            return [], None

        if signatures is not None:
            df_signatures = pd.DataFrame(signatures['signatures_data'])
            df_signatures.index = df_signatures['Type']
            df_signatures = df_signatures.drop(columns='Type')
            df_reprint = reprint(df_signatures, epsilon=0.0001)[selected_signatures]
        else:
            df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]
            df_reprint = pd.read_csv(f"data/cosmic_reprints/{selected_file}.reprint", sep='\t', index_col=0)[selected_signatures]

        per_page = 5
        total_pages = (len(selected_signatures) + per_page - 1) // per_page
        current_page = min(current_page, total_pages - 1)
        start = current_page * per_page
        end = start + per_page
        visible_signatures = selected_signatures[start:end]

        plots = []
        for signature in visible_signatures:
            plots.append(
                dbc.Row([
                    dbc.Col(
                        dcc.Graph(
                            figure=create_main_dashboard(
                                df_signatures,
                                signature=signature,
                                title=f'{signature} Frequency of Specific Tri-nucleotide Context Mutations by Mutation Type',
                                yaxis_title='Frequencies'
                            )
                        ), width=6
                    ),
                    dbc.Col(
                        dcc.Graph(
                            figure=create_main_dashboard(
                                df_reprint,
                                signature=signature,
                                title=f'{signature} Reprint - Probabilities of Specific Tri-nucleotide Context Mutations by Mutation Type',
                                yaxis_title='Probabilites'
                            )
                        ), width=6
                    )
                ])
            )

        navigation = dbc.Row([
            dbc.Col(dbc.Button("Previous", id="prev-page-btn", disabled=(current_page == 0), color="secondary"), width="auto"),
            dbc.Col(html.Span(f"Page {current_page + 1} of {total_pages}"), width="auto", style={"padding": "10px"}),
            dbc.Col(dbc.Button("Next", id="next-page-btn", disabled=(current_page >= total_pages - 1), color="secondary"), width="auto")
        ], justify="center", align="center")

        return plots, navigation

    return [], None

@app.callback(
    Output('session-2-signatures', 'data'),
    Input('upload-data-2-signatures', 'contents'),
    State('upload-data-2-signatures', 'filename'),
    prevent_initial_call=True
)
def update_session_2_data(contents, filename):
    if contents is not None:
        try:
            df_signatures = parse_signatures(contents, filename)
            return {
                'signatures_data': df_signatures.to_dict('records'),
                'filename': filename,
                'info': "Signatures uploaded successfully"
            }
        except Exception:
            return dash.no_update
    return dash.no_update

@app.callback(
    Output('upload-error-message-1', 'children'),
    Input('upload-data-1-signatures', 'contents'),
    State('upload-data-1-signatures', 'filename'),
    prevent_initial_call=True
)
def show_upload_status(contents, filename):
    if contents is not None:
        try:
            _ = parse_signatures(contents, filename)
            return dbc.Alert(f"Successfully loaded file: {filename}", color="success", dismissable=True)
        except Exception as e:
            return dbc.Alert(f"Error while processing file '{filename}'", color="danger", dismissable=True)
    return ""


@app.callback(
    [Output('signatures-dropdown-2', 'options'),
     Output('signatures-dropdown-2', 'value'),
     Output('dropdown-2', 'style'),
     Output('info_uploader-2', 'children')
     ],
    [Input('dropdown-2', 'value'),
     Input('session-2-signatures', 'data')]
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
    Output("download-dataframe-csv-2", "data"),
    Input("btn_csv-2", "n_clicks"),
    [State('signatures-dropdown-2', 'value'),
     State('dropdown-2', 'value'),
     State('epsilon-2', 'value'),
     State('session-2-signatures', 'data')],
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

@app.callback(
    Output("collapse-form-2", "is_open"),
    [Input("toggle-button-2", "n_clicks")],
    [State("collapse-form-2", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("download-dataframe-csv-signatures-2", "data"),
    Input("btn_csv-signatures-2", "n_clicks"),
    [
        State('signatures-dropdown-2', 'value'),
        State('dropdown-2', 'value'),
        State('session-2-signatures', 'data')
    ],
    prevent_initial_call=True
)
def download_signatures_only_2(n_clicks, selected_signatures, selected_file, contents):
    if contents is not None:
        df_signatures = pd.DataFrame(contents['signatures_data'])
        df_signatures.index = df_signatures['Type']
        df_signatures = df_signatures.drop(columns='Type')[selected_signatures]
    else:
        df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]

    return dcc.send_data_frame(df_signatures.to_csv, filename="signatures.csv")
