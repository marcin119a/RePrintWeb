import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import plotly.graph_objects as go
import numpy as np

def create_main_dashboard(df, signature, title, yaxis_title):
    frequencies = df[signature] * 1

    mutations = ['C>A', 'C>G', 'C>T', 'T>A', 'T>C', 'T>G']
    bases = ['A', 'C', 'G', 'T']
    contexts = [f'{x}[{m}]{y}' for m in mutations for x in bases for y in bases]

    colors = {
        'C>A': 'blue',
        'C>G': 'black',
        'C>T': 'red',
        'T>A': 'gray',
        'T>C': 'green',
        'T>G': 'pink'
    }

    fig = go.Figure()
    
    for mutation in mutations:
        mutation_contexts = [c for c in contexts if f'[{mutation}]' in c]
        mutation_frequencies = [frequencies[mc] if mc in frequencies.index else 0 for mc in mutation_contexts]
        
        fig.add_trace(go.Bar(
            x=mutation_contexts,
            y=mutation_frequencies,
            name=mutation,
            marker_color=colors[mutation]
        ))

    y_max = frequencies.max()

    fig.update_layout(
        title=title,
        xaxis_title='Mutation Context',
        yaxis_title=yaxis_title,
        xaxis_tickangle=-90,
        template='plotly_white',
        barmode='group',
        legend_title='Mutation Type',
        yaxis_range=[0, y_max], 
        margin=dict(l=50, r=50, t=50, b=150),
        xaxis=dict(tickfont=dict(size=8)),
        yaxis=dict(tickfont=dict(size=10))
    )

    return fig

from scipy.spatial.distance import pdist, squareform

def create_heatmap(df):

    df = df.T
    labels = df.index.tolist()

    fig = ff.create_dendrogram(df.values, labels=labels, orientation='bottom')
    fig.for_each_trace(lambda trace: trace.update(visible=False))

    for i in range(len(fig['data'])):
        fig['data'][i]['yaxis'] = 'y2'

    dendro_side = ff.create_dendrogram(df.values, orientation='right')
    for i in range(len(dendro_side['data'])):
        dendro_side['data'][i]['xaxis'] = 'x2'

    for data in dendro_side['data']:
        fig.add_trace(data)

    #  Create Heatmap
    dendro_leaves = dendro_side['layout']['yaxis']['ticktext']
    dendro_leaves = list(map(int, dendro_leaves))
    data_dist = pdist(df.values)
    heat_data = squareform(data_dist)
    heat_data = heat_data[dendro_leaves, :]
    heat_data = heat_data[:, dendro_leaves]

    heatmap = [
        go.Heatmap(
            x=dendro_leaves,
            y=dendro_leaves,
            z=heat_data,
            colorscale='Blues',
            colorbar=dict(
                x=1.2,
                xpad=10
            )
        )
    ]

    heatmap[0]['x'] = fig['layout']['xaxis']['tickvals']
    heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']

    # Add Heatmap Data to Figure
    for data in heatmap:
        fig.add_trace(data)

    # Edit Layout
    fig.update_layout({'width': 600, 'height': 600,
                       'showlegend': False, 'hovermode': 'closest',
                       })

    # Edit xaxis
    fig.update_layout(xaxis={'domain': [.15, 1],
                             'mirror': False,
                             'showgrid': False,
                             'showline': False,
                             'zeroline': False,
                             'side': 'top',
                             'tickvals': heatmap[0]['x'],
                             'ticktext': [labels[i] for i in dendro_leaves]
                             })

    # Edit xaxis2
    fig.update_layout(xaxis2={'domain': [0, .15],
                              'mirror': False,
                              'showgrid': False,
                              'showline': False,
                              'zeroline': False,
                              'showticklabels': False,
                              })

    # Edit yaxis
    fig.update_layout(yaxis={'domain': [0, 1],
                             'mirror': False,
                             'showgrid': False,
                             'showline': False,
                             'zeroline': False,
                             'side': 'right',
                             'tickvals': heatmap[0]['y'],
                             'ticktext': [labels[i] for i in dendro_leaves]
                             })

    # Edit yaxis2
    fig.update_layout(yaxis2={'domain': [.825, .975],
                              'mirror': False,
                              'showgrid': False,
                              'showline': False,
                              'zeroline': False,
                              'showticklabels': True,
                              'ticks': "",
                              })

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")

    return fig

from utils.utils import calculate_rmse
from scipy.spatial.distance import squareform
import numpy as np

def create_heatmap_with_rmse(df, calc_func=calculate_rmse, colorscale='Blues', hide_heatmap=False):
    # Transpose data and get labels
    df = df.T
    labels = df.index.tolist()

    n = df.shape[0]
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            rmse = calc_func(df.iloc[i, :], df.iloc[j, :])
            dist_matrix[i, j] = rmse
            dist_matrix[j, i] = rmse

    # Create bottom dendrogram
    fig = ff.create_dendrogram(dist_matrix, labels=labels, orientation='bottom')
    fig.for_each_trace(lambda trace: trace.update(visible=False))

    # Create side dendrogram
    dendro_side = ff.create_dendrogram(dist_matrix, orientation='right')
    if not hide_heatmap:
        for i in range(len(dendro_side['data'])):
            dendro_side['data'][i]['xaxis'] = 'x2'
    
    # Add side dendrogram data to the figure
    for data in dendro_side['data']:
        fig.add_trace(data)
    dendro_leaves = dendro_side['layout']['yaxis']['ticktext']
    dendro_leaves = list(map(int, dendro_leaves))
    
    if not hide_heatmap:
        # Create heatmap
        heat_data = dist_matrix[dendro_leaves, :]
        heat_data = heat_data[:, dendro_leaves]

        heatmap = [
            go.Heatmap(
                x=dendro_leaves,
                y=dendro_leaves,
                z=heat_data,
                colorscale=colorscale,
                colorbar=dict(
                    x=1.2,
                    xpad=10
                )
            )
        ]

        heatmap[0]['x'] = fig['layout']['xaxis']['tickvals']
        heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']

        # Add heatmap data to the figure
        for data in heatmap:
            fig.add_trace(data)

        fig.update_layout(xaxis={'domain': [.15, 1],
                                'mirror': False,
                                'showgrid': False,
                                'showline': False,
                                'zeroline': False,
                                'side': 'top',  # Ustawienie etykiet osi X na górze
                                'tickvals': fig['layout']['xaxis']['tickvals'],
                                'ticktext': [labels[i] for i in dendro_leaves]
                                })

        fig.update_layout(xaxis2={'domain': [0, .15],
                                'mirror': False,
                                'showgrid': False,
                                'showline': False,
                                'zeroline': False,
                                'showticklabels': False,
                                })

    fig.update_layout({'width': 700, 'height': 700,
                       'showlegend': False, 'hovermode': 'closest',
                       })
    fig.update_layout(yaxis={'domain': [0, 1],
                             'mirror': False,
                             'showgrid': False,
                             'showline': False,
                             'zeroline': False,
                             'showticklabels': True,
                             'tickvals': dendro_side['layout']['yaxis']['tickvals'],
                             'ticktext': [labels[i] for i in dendro_leaves],
                             'side': 'right',
                             })

    fig.update_layout(yaxis2={'domain': [.825, .975],
                              'mirror': False,
                              'showgrid': False,
                              'showline': False,
                              'zeroline': False,
                              'showticklabels': True,  
                              'ticks': "",
                              })

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")

    return fig



def create_empty_figure_with_text(text):
    fig = go.Figure()
    fig.update_layout(
        xaxis={'visible': True},
        yaxis={'visible': True},
        annotations=[{
            'text': text,
            'xref': 'paper',
            'yref': 'paper',
            'showarrow': False,
            'font': {'size': 20}
        }]
    )
    return fig