from utils.figpanel import create_main_dashboard
from dash import dcc, html
from main import app
from dash import Input, Output
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd




data = {
    'COSMIC_v1_SBS_GRCh37.txt': pd.read_csv('data/signatures/COSMIC_v1_SBS_GRCh37.txt', sep='\t').columns[1:].to_list(),
    'COSMIC_v2_SBS_GRCh37.txt': pd.read_csv('data/signatures/COSMIC_v2_SBS_GRCh37.txt', sep='\t').columns[1:].to_list(),
    'COSMIC_v3.1_SBS_GRCh37.txt': pd.read_csv('data/signatures/COSMIC_v3.1_SBS_GRCh37.txt', sep='\t').columns[1:].to_list(),
    'COSMIC_v3.4_SBS_GRCh37.txt': pd.read_csv('data/signatures/COSMIC_v3.4_SBS_GRCh37.txt', sep='\t').columns[1:].to_list(),
}

# Application layout
page2_layout = html.Div([
    navbar,
    dbc.Container([
    dbc.Row([
        dcc.Dropdown(
            id='dropdown-2',
            options=[
                {'label': 'COSMIC_v1_SBS_GRCh37.txt', 'value': 'COSMIC_v1_SBS_GRCh37.txt'},
                {'label': 'COSMIC_v2_SBS_GRCh37.txt', 'value': 'COSMIC_v2_SBS_GRCh37.txt'},
                {'label': 'COSMIC_v3.1_SBS_GRCh37.txt', 'value': 'COSMIC_v3.1_SBS_GRCh37.txt'},
                {'label': 'COSMIC_v3.4_SBS_GRCh37.txt', 'value': 'COSMIC_v3.4_SBS_GRCh37.txt'},
            ],
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
    dcc.Location(id='url-page2', refresh=False),
    dcc.Loading(
        id="loading-graphs",
        type="default",
        children=html.Div(id='plots-container-2')
    )
    ], fluid=True)
])



import plotly.graph_objects as go

@app.callback(
    Output('plots-container-2', 'children'),
    [Input('signatures-dropdown-2', 'value'),
     Input('dropdown-2', 'value')]
)
def update_graph(selected_signatures, selected_file):
    if not selected_signatures or not selected_file:
        return []

    df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]
    df_reprint = pd.read_csv(f"data/signatures/{selected_file}.reprint", sep='\t', index_col=0)[selected_signatures]

    plots = []
    for signature in selected_signatures:
        plots.append(
            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        figure=create_main_dashboard(
                            df_signatures,
                            signature=signature,
                            title=f'{signature} Frequency of Specific Tri-nucleotide Context Mutations by Mutation Type'
                        )
                    ), width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=create_main_dashboard(
                            df_reprint,
                            signature=signature,
                            title=f'{signature} Reprint - Frequency of Specific Tri-nucleotide Context Mutations by Mutation Type'
                        )
                    ), width=6
                )
            ])
        )
    return plots

@app.callback(
    [Output('signatures-dropdown-2', 'options'),
     Output('signatures-dropdown-2', 'value')],
    [Input('dropdown-2', 'value')]
)
def set_options(selected_category):
    return [{'label': f"{i}", 'value': i} for i in data[selected_category]], [i for i in data[selected_category]]

