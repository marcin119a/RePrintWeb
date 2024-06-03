from utils.figpanel import create_heatmap_with_rmse
from main import app
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd

# List of available files
files = [
    'COSMIC_v1_SBS_GRCh37.txt', 'COSMIC_v2_SBS_GRCh37.txt', 'COSMIC_v3.1_SBS_GRCh37.txt',
    'COSMIC_v3.2_SBS_GRCh37.txt', 'COSMIC_v3.3.1_SBS_GRCh37.txt', 'COSMIC_v3.4_SBS_GRCh37.txt',
    'COSMIC_v3_SBS_GRCh37.txt', 'COSMIC_v1_SBS_GRCh38.txt', 'COSMIC_v2_SBS_GRCh38.txt',
    'COSMIC_v3.1_SBS_GRCh38.txt', 'COSMIC_v3.2_SBS_GRCh38.txt', 'COSMIC_v3.3.1_SBS_GRCh38.txt',
    'COSMIC_v3.4_SBS_GRCh38.txt', 'COSMIC_v3_SBS_GRCh38.txt', 'Zou2018-signatures.SBS-96.tsv'
]

# Load data from files
data = {}
for file in files:
    data[file] = pd.read_csv(f'data/signatures/{file}', sep='\t').columns[1:].to_list()

# Dropdown options for file selection
dropdown_options = [{'label': file, 'value': file} for file in files]

# Application layout
page3_layout = html.Div([
    navbar,
    dbc.Container([
        dbc.Row([
            dcc.Dropdown(
                id='dropdown-3',
                options=dropdown_options,
                disabled=False,
                multi=True,
                placeholder="Select signature files"
            ),
        ]),
        dcc.Dropdown(
            id='signatures-dropdown-3',
            multi=True,
            placeholder="Select signatures"
        ),
        dbc.Row([
            dbc.Col([
                html.H5("Signature similarity"),
                dcc.Graph(id='heatmap-plot-3')
            ]),
            dbc.Col([
                html.H5("RePrint similarity"),
                dcc.Graph(id='heatmap-reprint-plot-3')
            ])
        ]),
        dcc.Location(id='url-page3', refresh=False),
        dbc.Button("Download TSV", id="btn_csv_3", className="mt-3", color="dark"),
        dcc.Download(id="download-dataframe-csv-3")
    ], fluid=True),
])
from utils.utils import reprint

@app.callback(
    [Output('signatures-dropdown-3', 'options'),
     Output('signatures-dropdown-3', 'value')],
    [Input('dropdown-3', 'value')]
)
def update_signature_dropdown(selected_files):
    if selected_files:
        common_signatures = set(data[selected_files[0]])
        for file in selected_files[1:]:
            common_signatures.update(data[file])

        options = [{'label': sig, 'value': sig} for sig in common_signatures]
        return options, list(common_signatures)
    return [], []


@app.callback(
    [Output('heatmap-plot-3', 'figure'),
     Output('heatmap-reprint-plot-3', 'figure')],
    [Input('dropdown-3', 'value'),
     Input('signatures-dropdown-3', 'value')]
)
def update_output(selected_files, selected_signatures):
    if selected_files and selected_signatures:
        combined_df = pd.concat([pd.read_csv(f"data/signatures/{file}", sep='\t', index_col=0)
                                 for file in selected_files], axis=1)[selected_signatures]
        combined_reprint = reprint(combined_df)

        return (
            create_heatmap_with_rmse(combined_df),
            create_heatmap_with_rmse(combined_reprint, colorscale='Viridis')
        )
    return {}, {}

@app.callback(
    Output("download-dataframe-csv-3", "data"),
    Input("btn_csv_3", "n_clicks"),
    [State('dropdown-3', 'value')],
    prevent_initial_call=True
)
def func(n_clicks, selected_files):
    combined_df = pd.concat([pd.read_csv(f"data/signatures/{file}", sep='\t', index_col=0) for file in selected_files], axis=1)
    return dcc.send_data_frame(combined_df.to_csv, filename="combined_data.csv")