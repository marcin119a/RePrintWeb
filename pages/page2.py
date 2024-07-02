from utils.figpanel import create_main_dashboard
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
    'transcribed.txt', 'untranscribed.txt'
]


data = {}

for file in files:
    data[file] = pd.read_csv(f'data/signatures/{file}', sep='\t').columns[1:].to_list()

dropdown_options = [{'label': file, 'value': file} for file in files]

# Application layout
page2_layout = html.Div([
    navbar,
    dcc.Interval(id='initial-load', interval=1000, n_intervals=0, max_intervals=1),
    dbc.Container([
    dbc.Row([
        dcc.Dropdown(
            id='dropdown-2',
            options=dropdown_options,
            disabled=False,
            value='COSMIC_v2_SBS_GRCh37.txt'
        ),
        dcc.Dropdown(
                id='signatures-dropdown-2',
                options=[{'label': k, 'value': k} for k in data.keys()],
                multi=True,
                value=[k for k in data['COSMIC_v2_SBS_GRCh37.txt']],
            ),
    ]),
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
    html.Div(id='info_uploader-2'),
    dcc.Store(id='session-2-signatures', storage_type='session', data=None),
    dbc.Button("Generate plots", id="reload-button", className="ms-2"),
    dcc.Location(id='url-page2', refresh=False),
    dcc.Loading(
        id="loading-graphs",
        type="default",
        children=html.Div(id='plots-container-2')
    )
    ], fluid=True)
])


import dash
from utils.utils import reprint
@app.callback(
    Output('plots-container-2', 'children'),
    [Input('initial-load', 'n_intervals'),
     Input('dropdown-2', 'value'),
     Input('reload-button', 'n_clicks')],
    [State('signatures-dropdown-2', 'value'),
     State('session-2-signatures', 'data')]
)
def update_graph(init_load, selected_file, n_clicks, selected_signatures, signatures):
    ctx = dash.callback_context

    if not ctx.triggered:
        trigger_id = 'initial-load'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'initial-load' or trigger_id == 'reload-button':
        if not selected_signatures or not selected_file:
            return []
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
                                yaxis_title='Probabilites'
                            )
                        ), width=6
                    )
                ])
            )
        return plots
from utils.utils import parse_signatures

@app.callback(
    [Output('session-2-signatures', 'data')],
    [Input('upload-data-2-signatures', 'contents')],
    [State('upload-data-2-signatures', 'filename')]
)
def update_output_signatures(contents, filename):
    if contents is not None:
        df_signatures = parse_signatures(contents, filename)

        signatures_info = "Some information extracted from df_signatures"
        return [{'signatures_data': df_signatures.to_dict('records'), 'filename': filename, 'info': signatures_info}]
    else:
        return dash.no_update
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