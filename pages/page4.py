from utils.figpanel import create_main_dashboard
from utils.utils import parse_signatures
from dash import dcc, html
from main import app
from dash import Input, Output, State
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd


files = [
    'COSMIC_v1_SBS_GRCh37.txt', 'COSMIC_v2_SBS_GRCh37.txt', 'COSMIC_v3.1_SBS_GRCh37.txt',
    'COSMIC_v3.2_SBS_GRCh37.txt', 'COSMIC_v3.3.1_SBS_GRCh37.txt', 'COSMIC_v3.4_SBS_GRCh37.txt', 'COSMIC_v3_SBS_GRCh37.txt',
    'COSMIC_v1_SBS_GRCh38.txt', 'COSMIC_v2_SBS_GRCh38.txt', 'COSMIC_v3.1_SBS_GRCh38.txt',
    'COSMIC_v3.2_SBS_GRCh38.txt', 'COSMIC_v3.3.1_SBS_GRCh38.txt', 'COSMIC_v3.4_SBS_GRCh38.txt', 'COSMIC_v3_SBS_GRCh38.txt',
    'transcribed.normalized.txt', 'untranscribed.normalized.txt'
]


data = {}

for file in files:
    data[file] = pd.read_csv(f'data/signatures/{file}', sep='\t').columns[1:].to_list()

dropdown_options = [{'label': file, 'value': file} for file in files]

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
            value='COSMIC_v2_SBS_GRCh37.txt'
        ),
        dcc.Dropdown(
                id='signatures-dropdown-4',
                options=[{'label': k, 'value': k} for k in data.keys()],
                multi=True,
                value=[k for k in data['COSMIC_v2_SBS_GRCh37.txt']],
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
                dcc.Graph(id='heatmap-plot-4')
            ]),
            dbc.Col([
                html.H5("RePrint similarity"),
                dcc.Graph(id='heatmap-reprint-plot-4')
            ])
    ]),
    dcc.Location(id='url-page4', refresh=False),
    dcc.Loading(
        id="loading-graphs",
        type="default",
        children=html.Div(id='plots-container-4')
    )
    ], fluid=True)
])


import dash
from utils.utils import reprint
@app.callback(
    [Output('plots-container-4', 'children'),
     Output('heatmap-plot-4', 'figure'),
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
            return [], {}, {}
        if signatures is not None:
            df_signatures = pd.DataFrame(signatures['signatures_data'])
            df_signatures.index = df_signatures['Type']
            df_signatures = df_signatures.drop(columns='Type')
            df_reprint = reprint(df_signatures, epsilon=0.0001)[selected_signatures]

        else:
            df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]
            df_reprint = pd.read_csv(f"data/cosmic_reprints/{selected_file}.reprint", sep='\t', index_col=0)[selected_signatures]

        plots = []
        for signature in selected_signatures:
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
                                yaxis_title='Probabilities'
                            )
                        ), width=6
                    )
                ])
            )
        from utils.figpanel import create_heatmap_with_rmse
        return plots, create_heatmap_with_rmse(df_signatures),create_heatmap_with_rmse(df_reprint)
    else:
        return [], {}, {}

@app.callback(
    [Output('session-4-signatures', 'data')],
    [Input('upload-data-4-signatures', 'contents')],
    [State('upload-data-4-signatures', 'filename'),
     State('session-4-signatures', 'data')]
)
def update_output_signatures(contents, filename, existing_data):
    if contents is not None:
        new_df_signatures = parse_signatures(contents, filename)

        # Sprawdzenie, czy istnieją już zapisane sygnatury
        if existing_data is not None:
            existing_df = pd.DataFrame(existing_data['signatures_data'])

            # Jeśli indeks to 'Type', ustawienie go ponownie
            if 'Type' in existing_df.columns:
                existing_df.index = existing_df['Type']
                existing_df = existing_df.drop(columns='Type')

            # Połączenie starych i nowych danych, bez duplikatów
            merged_df = pd.merge(existing_df, new_df_signatures, on='Type', how='inner')
            merged_df.index = merged_df['Type']
        else:
            merged_df = new_df_signatures

        # Konwersja do listy rekordów dla sesji
        signatures_info = f"Updated signatures with {filename}"
        return [{'signatures_data': merged_df.to_dict('records'), 'filename': filename, 'info': signatures_info}]
    
    return dash.no_update


@app.callback(
    [Output('signatures-dropdown-4', 'options'),
     Output('signatures-dropdown-4', 'value'),
     Output('dropdown-4', 'style'),
     Output('info_uploader-4', 'children')],
    [Input('session-4-signatures', 'data')]
)
def set_options(contents):
    if contents is not None:
        df = pd.DataFrame(contents['signatures_data'])

        if 'Type' in df.columns:
            df.index = df['Type']
            df = df.drop(columns='Type')

        # Pobieramy listę sygnatur z załadowanych danych
        uploaded_signatures = df.columns.to_list()

        # Łączymy oba zestawy sygnatur, unikając duplikatów
        all_signatures = list(set(uploaded_signatures))

        return (
            [{'label': signature, 'value': signature} for signature in all_signatures],
            all_signatures,
            {'display': 'None'},
            f'Added your signatures from {contents["filename"]}'
        )

    return (
        [{'label': f"{i}", 'value': i} for i in data[selected_category]],
        [i for i in data[selected_category]],
        {'display': 'block'},
        'Not Uploaded'
    )
