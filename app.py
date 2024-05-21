from dash import dcc, html
from dash.dependencies import Input, Output
from main import *
from pages.page1 import page1_layout
from pages.page2 import page2_layout

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

@app.callback(Output('url', 'pathname'),
              [Input('page1-button', 'n_clicks')],
              prevent_initial_call=True)
def redirect_to_page1(n_clicks):
    return '/page1?example=True'


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return page1_layout
    elif pathname == '/page2':
        return page2_layout

# Callback to set the active state
@app.callback(
    [Output("nav-home", "active"),
     Output("nav-page1", "active")
    ],
    [Input("url", "pathname")]
)
def set_active_nav(pathname):
    # Check the current pathname and return True for the matching NavLink
    if pathname == "/":
        return True, False
    elif pathname == "/page1":
        return False, True
    elif pathname == "/page2":
        return False, False

    # Default case if no path matches
    return False, False, False


if __name__ == '__main__':
    app.run_server(debug=True)
