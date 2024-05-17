from dash import dcc, html
from main import app
import dash
from utils.uploader import parse_contents, parse_signatures
from utils.figpanel import create_main_dashboard, create_empty_figure_with_text
import numpy as np
from dash import Input, Output, State
import dash_bootstrap_components as dbc
from pages.nav import navbar
import pandas as pd



# Application layout
page2_layout = html.Div([
    navbar,
    dbc.Container([
    html.Div([
        html.Div([
        dcc.Upload(
            id='upload-data-3',
            children=html.Div(['Drag and Drop Mutational Profiles (csv, tsv, vcf) format (required) ']),
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
        dcc.Upload(
            id='upload-data-3-signatures',
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
        ], style={'display': 'flex'}),
        dcc.Store(id='session-3', storage_type='session', data=None),
        dcc.Store(id='session-3-signatures', storage_type='session', data=None),
        dcc.Dropdown(
            id='patient-dropdown-3',
            options=[],
            value='',
            placeholder='Please upload your catalogs to chose the patient'
        ),
        dcc.Input(
            id='only-text-3',
            disabled=True,
            value='Please upload your signatures'
        ),
        dcc.Dropdown(
            id='signatures-dropdown-3',
            options=[],
            multi=True,
            value=[],
        ),
    ], style={'padding': '10px'}),
        html.Div(id='upload-message-3',
                     style={
                         'width': '50%',
                         'height': '60px',
                         'lineHeight': '60px',
                         'borderWidth': '1px',
                         'borderStyle': 'line',
                         'borderRadius': '5px',
                         'textAlign': 'center',
                         'margin': '10px'
                     },
    ),
    html.Div([
        dbc.InputGroup(
            [
                dbc.InputGroupText("Bootstrap replicates:"),
                dbc.Input(id='input-R-3', type='number', value=50),
            ],
            className="mb-3",
        ),
        dbc.Tooltip("The number of bootstrap replicates used for significance testing.", target="input-R", placement='top'),

        dbc.InputGroup(
            [
                dbc.InputGroupText("Mutation count:"),
                dbc.Input(id='input-mutation-count-3', type='number', value=1000),
            ],
            className="mb-3",
        ),
        dbc.Tooltip("The observed mutation profile vector for a patient/sample. "
                    "If m is a vector of counts, then mutation.count equals the summation of all the counts. "
                    "If m is probabilities, then mutation.count has to be specified.", target="input-mutation-count", placement='top'),

        dbc.InputGroup(
            [
                dbc.InputGroupText("P-value:"),
                dbc.Input(id='input-p-value-3', type='number', value=0.02, step=0.01),
            ],
            className="mb-3",
        ),
        dbc.Tooltip("The p-value threshold below which a signature is considered significant.", target="input-p-value", placement='top'),

        dbc.InputGroup(
            [
                dbc.InputGroupText("Threshold:"),
                dbc.Input(id='input-threshold-3', type='number', value=0.01, step=0.01),
            ],
            className="mb-3",
        ),
        dbc.Tooltip("The threshold used to determine if a signature's exposure is significant in the bootstrap samples.", target="input-threshold", placement='top'),
    ], style={'display': 'flex', 'justifyContent': 'center', 'padding': '10px'}),
    html.Button('Run model',
                id='clear-button-3',
                className='btn btn-primary'),
    dcc.Loading(
        id="loading-1",
        type="default",
        children=[
            dcc.Graph(id='bar-plot-bootstrap-3'),
            dcc.Graph(id='bar-plot-modelselection-3')
        ],
    ),
])
])


@app.callback(
    [Output('session-3', 'data')],
    [Input('upload-data-3', 'contents')],
    [State('upload-data-3', 'filename')]
)
def update_output_2(contents, filename):
    if contents is not None:
        df = parse_contents(contents, filename)
        patient = df.columns.to_list()[0]
        return [{'data': df.to_dict('records'), 'filename': filename, 'patient': patient}]
    else:
        return dash.no_update

@app.callback(
    [Output('session-3-signatures', 'data')],
    [Input('upload-data-3-signatures', 'contents')],
    [State('upload-data-3-signatures', 'filename')]
)
def update_output_signatures(contents, filename):
    if contents is not None:
        df_signatures = parse_signatures(contents, filename)
        signatures_info = "Some information extracted from df_signatures"
        return [{'signatures_data': df_signatures.to_dict('records'), 'filename': filename, 'info': signatures_info}]
    else:
        return dash.no_update

@app.callback(
    [Output('signatures-dropdown-3', 'options'),
    Output('signatures-dropdown-3', 'value'),
    Output('only-text-3', 'value')],
    [Input('session-3-signatures', 'data')]
)
def update_message(contents):
    if contents is not None:
        df = pd.DataFrame(contents['signatures_data'])
        signatures = df.columns.to_list()
        return [{'label': signature, 'value': signature} for signature in signatures], [signature for signature in signatures], contents['filename']
    return dash.no_update

@app.callback(
    [Output('upload-message-3', 'children'),
    Output('patient-dropdown-3', 'options'),
    Output('patient-dropdown-3', 'value')],
    [Input('session-3', 'data')]
)
def update_message(contents):
    if contents is not None:
        df = pd.DataFrame(contents['data'])
        patients = df.columns.to_list()
        return html.Div(f'File {contents["filename"]} has been uploaded.'), [{'label': patient, 'value': patient} for patient in patients], contents['patient']
    return '', [{'label': 'None', 'value': 'None'}], None



@app.callback(
    [Output('bar-plot-bootstrap-3', 'figure'),
     Output('bar-plot-modelselection-3', 'figure'),
     Output('input-mutation-count-3', 'value')],
    [Input('session-3', 'data'),
     Input('clear-button-3', 'n_clicks'),
     Input('patient-dropdown-3', 'value')
    ],
    [State('session-3-signatures', 'data'),
     State('signatures-dropdown-3', 'value'),
     State('input-R-3', 'value'),
     State('input-mutation-count-3', 'value'),
     State('input-p-value-3', 'value'),
     State('input-threshold-3', 'value'),
     ]
)
def update_output(contents, button, patient, signatures, signatures_new, R, mutation_count, p_value, threshold):
    if contents is not None and signatures is not None and patient != '':
        df = pd.DataFrame(contents['data'])
        data, patients = df.to_numpy(), df.columns.to_numpy()
        column_index = np.where(patients == patient)[0]

        patient_column = data[:, column_index].squeeze()


        data = pd.DataFrame(signatures['signatures_data'])
        signatures, names = data.values, data.columns.to_list()
        return create_main_dashboard(names, signatures_new, signatures, patient_column, patient, R, mutation_count, threshold, p_value)
    else:
        return create_empty_figure_with_text("Please upload catalogs and signatures to view the plot."), create_empty_figure_with_text("Please upload catalogs and signatures to view the plot."), 1000

