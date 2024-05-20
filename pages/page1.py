from utils.utils import data
from utils.figpanel import create_empty_figure_with_text, create_main_dashboard
from utils.uploader import parse_contents, load_signatures
from dash import dcc, html
from main import app
import numpy as np
from dash import Input, Output, State
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd
import dash




organs = [
    "Breast", "Ovary", "Kidney", "Colorectal", "Bone_SoftTissue",
    "Lung", "Uterus", "CNS", "Prostate", "Bladder", "Skin",
    "Stomach", "NET", "Pancreas", "Biliary", "Liver", "Lymphoid",
    "Myeloid", "Oral_Oropharyngeal", "Esophagus", "Head_neck"
]
data = {
    f'{organ}_Signature.csv': pd.read_csv(f'data/signatures_organ/latest/{organ}_Signature.csv', sep=',').columns[1:].to_list() for organ in organs
}

# Application layout
page1_layout = html.Div([
    dcc.Dropdown(
        id='dropdown-cancer',
        options=[
            {'label': f'{organ}_Signature.csv', 'value': f'{organ}_Signature.csv'} for organ in organs
        ],
        disabled=False,
        value='Biliary_Signature.csv'
    ),
    dcc.Dropdown(
            id='signatures-dropdown-cancer',
            options=[{'label': k, 'value': k} for k in data.keys()],
            multi=True,
            value=[k for k in data['Biliary_Signature.csv']],
        ),
    html.H1("Visualization of Tri-nucleotide Context Mutations"),
    dcc.Graph(
        id='signature-plot'
    ),
    dcc.Graph(
        id='reprint-plot'
    ),
])


@app.callback(
    [Output('signatures-dropdown-cancer', 'options'),
     Output('signatures-dropdown-cancer', 'value')],
    [Input('dropdown-cancer', 'value')]
)
def set_options(selected_category):
    return [{'label': f"{i}", 'value': i} for i in data[selected_category]], [i for i in data[selected_category]]

import plotly.graph_objects as go

@app.callback(
    [Output('signature-plot', 'figure'),
     Output('reprint-plot', 'figure')],
    [Input('signatures-dropdown-cancer', 'value'),
     Input('dropdown-cancer', 'value')]
)
def update_graph(selected_signatures, selected_file):
    if not selected_signatures:
        return go.Figure()

    df_signatures = pd.read_csv(f"/Users/mw/PycharmProjects/RePrint/data/signatures/COSMIC_v2_SBS_GRCh37.txt", sep='\t', index_col=0)

    df_reprint = pd.read_csv(f"/Users/mw/PycharmProjects/RePrint/data/signatures/COSMIC_v2_SBS_GRCh37_reprint.txt",  sep='\t', index_col=0)

    print(df_signatures.columns)
    return (create_main_dashboard(df_signatures['Signature_6'].to_numpy()*100,
                                  title='Frequency of Specific Tri-nucleotide Context Mutations by Mutation Type'),
            create_main_dashboard(df_reprint['Signature_6'].to_numpy()*100,
                                  title='Reprint - Frequency of Specific Tri-nucleotide Context Mutations by Mutation Type'))