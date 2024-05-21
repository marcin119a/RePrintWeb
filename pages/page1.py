from utils.utils import data
from utils.figpanel import create_main_dashboard, create_heatmap
from dash import dcc, html
from main import app
from dash import Input, Output
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd




data = {
    'COSMIC_v2_SBS_GRCh37.txt': pd.read_csv('data/signatures/COSMIC_v2_SBS_GRCh37.txt', sep='\t').columns[1:].to_list(),
    'COSMIC_v3.1_SBS_GRCh37.txt': pd.read_csv('data/signatures/COSMIC_v3.1_SBS_GRCh37.txt', sep='\t').columns[1:].to_list(),
    'COSMIC_v3.4_SBS_GRCh37.txt': pd.read_csv('data/signatures/COSMIC_v3.4_SBS_GRCh37.txt', sep='\t').columns[1:].to_list(),
}

# Application layout
page1_layout = html.Div([
    navbar,
    dbc.Container([
    dbc.Row([
        dcc.Dropdown(
            id='dropdown-cancer',
            options=[
                {'label': 'COSMIC_v2_SBS_GRCh37.txt', 'value': 'COSMIC_v2_SBS_GRCh37.txt'},
                {'label': 'COSMIC_v3.1_SBS_GRCh37.txt', 'value': 'COSMIC_v3.1_SBS_GRCh37.txt'},
                {'label': 'COSMIC_v3.4_SBS_GRCh37.txt', 'value': 'COSMIC_v3.4_SBS_GRCh37.txt'},
            ],
            disabled=False,
            value='COSMIC_v2_SBS_GRCh37.txt'
        ),
        dcc.Dropdown(
                id='signatures-dropdown-cancer',
                options=[{'label': k, 'value': k} for k in data.keys()],
                multi=True,
                value=[k for k in data['COSMIC_v2_SBS_GRCh37.txt']],
            ),
        html.H1("Visualization of Tri-nucleotide Context Mutations"),
        dcc.Graph(
            id='signature-plot'
        ),
        dcc.Graph(
            id='reprint-plot'
        ),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='heatmap-plot')),
        dbc.Col(dcc.Graph(id='heatmap-reprint-plot'))
    ])
    ])
])



import plotly.graph_objects as go

@app.callback(
    [Output('signature-plot', 'figure'),
     Output('reprint-plot', 'figure'),
     Output('heatmap-plot', 'figure'),
     Output('heatmap-reprint-plot', 'figure')
     ],
    [Input('signatures-dropdown-cancer', 'value'),
     Input('dropdown-cancer', 'value')]
)
def update_graph(selected_signatures, selected_file):
    if not selected_signatures:
        return go.Figure()

    df_signatures = pd.read_csv(f"data/signatures/{selected_file}", sep='\t', index_col=0)[selected_signatures]

    df_reprint = pd.read_csv(f"data/signatures/{selected_file}.reprint",  sep='\t', index_col=0)[selected_signatures]

    print(df_signatures.columns)
    return (create_main_dashboard(df_signatures[selected_signatures[0]].to_numpy()*100,
                                  title='Frequency of Specific Tri-nucleotide Context Mutations by Mutation Type'),
            create_main_dashboard(df_reprint[selected_signatures[0]].to_numpy()*100,
                                  title='Reprint - Frequency of Specific Tri-nucleotide Context Mutations by Mutation Type'),
            create_heatmap(df_signatures),
            create_heatmap(df_reprint)
            )

@app.callback(
    [Output('signatures-dropdown-cancer', 'options'),
     Output('signatures-dropdown-cancer', 'value')],
    [Input('dropdown-cancer', 'value')]
)
def set_options(selected_category):
    return [{'label': f"{i}", 'value': i} for i in data[selected_category]], [i for i in data[selected_category]]
