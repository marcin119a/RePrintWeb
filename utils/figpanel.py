import plotly.express as px
import plotly.graph_objects as go


def create_main_dashboard(frequencies, title):
    import plotly.graph_objects as go
    import numpy as np

    # Definiowanie kontekstów i grup mutacji
    mutations = ['C>A', 'C>G', 'C>T', 'T>A', 'T>C', 'T>G']
    bases = ['A', 'C', 'G', 'T']
    contexts = [f'{x}[{m}]{y}' for m in mutations for x in bases for y in bases]

    # Losowe wartości częstości dla każdego kontekstu
    np.random.seed(42)  # Dla powtarzalności wyników

    # Definiowanie kolorów dla każdej grupy mutacji
    colors = {
        'C>A': 'blue',
        'C>G': 'green',
        'C>T': 'red',
        'T>A': 'purple',
        'T>C': 'orange',
        'T>G': 'brown'
    }

    # Tworzenie wykresu
    fig = go.Figure()

    # Dodawanie słupków dla każdej grupy mutacji
    for mutation in mutations:
        mutation_contexts = [c for c in contexts if f'[{mutation}]' in c]
        mutation_frequencies = [frequencies[contexts.index(mc)] for mc in mutation_contexts]
        fig.add_trace(go.Bar(
            x=mutation_contexts,
            y=mutation_frequencies,
            name=mutation,  # Nazwa dla legendy
            marker_color=colors[mutation]  # Kolor dla grupy mutacji
        ))

    # Dodanie prostokątów i tekstu nad grupami
    annotations = []
    for i, mutation in enumerate(mutations):
        # Obliczanie pozycji dla prostokątów
        x0 = i * 16 - 0.5
        x1 = x0 + 16
        # Dodanie prostokąta
        fig.add_shape(type="rect",
                      x0=x0, y0=105, x1=x1, y1=115,
                      fillcolor=colors[mutation], opacity=0.5, line=dict(color=colors[mutation]))
        # Dodanie tekstu
        fig.add_annotation(x=(x0 + x1) / 2, y=110,
                           text=mutation, showarrow=False,
                           font=dict(color='white', size=12))

    # Dodanie tytułów i formatowanie osi

    fig.update_layout(
        title=title,
        xaxis_title='Mutation Context',
        yaxis_title='Frequency (%)',
        xaxis_tickangle=-45,
        template='plotly_white',
        barmode='group',
        legend_title='Mutation Type',
        yaxis_range=[0, 120],
        xaxis=dict(
            tickmode='linear',
            dtick=1  # Ustawia etykiety co jeden kontekst
        ),
        yaxis=dict(
            tickfont=dict(size=6)
        )
    )


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