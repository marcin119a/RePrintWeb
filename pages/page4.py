from utils.utils import parse_signatures
from dash import dcc, html
from main import app
from dash import Input, Output, State
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd
from utils.utils import FILES, DEFAULT_SIGNATURES


data = {}

for file in FILES:
    data[file] = pd.read_csv(f'data/signatures/{file}', sep='\t').columns[1:].to_list()

dropdown_options = [{'label': file, 'value': file} for file in FILES]

# Application layout
page4_layout = html.Div([
    navbar,
    dcc.Interval(id='initial-load', interval=1000, n_intervals=0, max_intervals=1),
    dbc.Container([
        dbc.Row([
            dcc.Dropdown(
                id='dropdown-4',
                options=dropdown_options,
                disabled=False,
                value=DEFAULT_SIGNATURES
            ),
            dcc.Dropdown(
                id='signatures-dropdown-4',
                options=[{'label': k, 'value': k} for k in data.keys()],
                multi=True,
                value=[k for k in data[DEFAULT_SIGNATURES]],
            ),
        ]),
        dcc.Upload(
            id='upload-data-4-signatures',
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
        html.Div(id='info_uploader-4'),
        dbc.Alert(
            [
                html.H5("Expected File Format", style={"font-size": "18px", "font-weight": "bold"}),
                html.P(
                    "The uploaded file should be a tab-separated file (.txt) containing mutation types and corresponding mutation signatures.",
                    style={"font-size": "14px"}),
                html.P("Columns:", style={"font-size": "14px", "margin-bottom": "5px"}),
                html.Ul([
                    html.Li("Type: Mutation type (e.g., A[C>A]A, A[C>A]C, ...).", style={"font-size": "13px"}),
                    html.Li("SBS1, SBS2, ..., SBSN: Signature mutation values (frequencies or probabilities).",
                            style={"font-size": "13px"})
                ], style={"padding-left": "20px", "margin-bottom": "5px"}),
                html.P("Example first few rows:", style={"font-size": "14px", "margin-bottom": "5px"}),
                html.Pre(
                    "Type\tSBS1\tSBS2\tSBS3\n"
                    "A[C>A]A\t0.001\t0.002\t0.003\n"
                    "A[C>A]C\t0.004\t0.005\t0.006",
                    style={"white-space": "pre-wrap", "font-family": "monospace", "font-size": "12px",
                           "background-color": "#f8f9fa", "padding": "5px"}
                ),
            ],
            color="info",
            dismissable=True,
            style={"font-size": "14px", "padding": "10px"}),
        dcc.Store(id='session-4-signatures', storage_type='session', data=None),
        dbc.Button("Generate plots", id="reload-button", className="ms-2"),
        dbc.Row([
            dbc.Col([
                html.H5("Signature similarity"),
                dcc.Loading(
                    id="loading-heatmap-4",
                    type="default",
                    children=dcc.Graph(id='heatmap-plot-4')
                )
            ]),
            dbc.Col([
                html.H5("RePrint similarity"),
                dcc.Loading(
                    id="loading-reprint-4",
                    type="default",
                    children=dcc.Graph(id='heatmap-reprint-plot-4')
                )
            ])
        ]),
        dcc.Location(id='url-page4', refresh=False),
    ], fluid=True)
])

import dash
from utils.utils import reprint


@app.callback(
    [Output('heatmap-plot-4', 'figure'),
     Output('heatmap-reprint-plot-4', 'figure')],
    [Input('initial-load', 'n_intervals'),
     Input('dropdown-4', 'value'),
     Input('reload-button', 'n_clicks')],
    [State('signatures-dropdown-4', 'value'),
     State('session-4-signatures', 'data')]
)
def update_graph(init_load, selected_file, n_clicks, selected_signatures, signatures):
    ctx = dash.callback_context

    if not ctx.triggered:
        trigger_id = 'initial-load'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'initial-load' or trigger_id == 'reload-button':
        if not selected_signatures or not selected_file:
            return {}, {}
        if signatures is not None:
            if isinstance(signatures, list):
                df_signatures = pd.DataFrame(signatures[0]['signatures_data'])
            else:
                df_signatures = pd.DataFrame(signatures['signatures_data'])
            df_signatures.set_index('Type', inplace=True)

            df_reprint_all = reprint(df_signatures, epsilon=0.0001)

            df_reprint = df_reprint_all[[col for col in selected_signatures if col in df_reprint_all.columns]]
        else:
            df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)
            df_signatures.columns = [f"{c}_ref" for c in df_signatures.columns]

            df_signatures = df_signatures[selected_signatures]
            df_reprint = reprint(df_signatures, epsilon=0.0001)[selected_signatures]

        from utils.figpanel import create_vertical_dendrogram_with_query_labels_right
        return create_vertical_dendrogram_with_query_labels_right(df_signatures), create_vertical_dendrogram_with_query_labels_right(df_reprint)
    else:
        return {}, {}


@app.callback(
    Output('session-4-signatures', 'data'),
    Input('upload-data-4-signatures', 'contents'),
    State('upload-data-4-signatures', 'filename'),
    State('dropdown-4', 'value')  # dodajemy nazwę pliku bazowego
)
def update_output_signatures(contents, filename, selected_file):
    if contents is None:
        return dash.no_update

    df_ref = pd.read_csv(f"data/signatures/{selected_file}", sep='\t')
    df_ref = df_ref.rename(columns={col: f"{col}_ref" for col in df_ref.columns if col != 'Type'})
    df_ref.set_index('Type', inplace=True)

    df_query = parse_signatures(contents, filename)
    if 'Type' in df_query.columns:
        df_query.set_index('Type', inplace=True)
    df_query = df_query.rename(columns={col: f"{col}_query" for col in df_query.columns})

    # Merge
    merged = df_ref.join(df_query, how='inner')
    merged.reset_index(inplace=True)

    return [{
        'signatures_data': merged.to_dict('records'),
        'filename': filename,
        'info': f'Merged base: {selected_file} with upload: {filename}'
    }]


@app.callback(
    [Output('signatures-dropdown-4', 'options'),
     Output('signatures-dropdown-4', 'value'),
     Output('dropdown-4', 'style'),
     Output('info_uploader-4', 'children')],
    [Input('dropdown-4', 'value'),
     Input('session-4-signatures', 'data')],
)
def set_options(selected_category, contents):
    base_signatures = data[selected_category]

    if contents is not None:
        if isinstance(contents, list):
            content = contents[0]
        else:
            content = contents

        df = pd.DataFrame(content['signatures_data'])
        if 'Type' in df.columns:
            df.set_index('Type', inplace=True)

        all_columns = df.columns.tolist()
        ref_cols = sorted([col for col in all_columns if col.endswith('_ref')])
        query_cols = sorted([col for col in all_columns if col.endswith('_query')])

        combined = ref_cols + query_cols

        return (
            [{'label': sig, 'value': sig} for sig in combined],
            combined,
            {'display': 'None'},
            content.get('info', f'Merged {selected_category} with uploaded file')
        )

    return (
        [{'label': f"{s}_ref", 'value': f"{s}_ref"} for s in base_signatures],
        [f"{s}_ref" for s in base_signatures],
        {'display': 'block'},
        'Not Uploaded'
    )
