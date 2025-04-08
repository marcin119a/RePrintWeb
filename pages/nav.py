import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Start page", href="/", id="nav-home")),
        dbc.NavItem(dbc.NavLink("Reprints COSMIC", href="/page1", id="nav-page1")),
        dbc.NavItem(dbc.NavLink("Custom Reprints", href="/page2", id="nav-page2")),
        dbc.NavItem(dbc.NavLink("Merge signatures", href="/page4", id="nav-page4")),
    ],
    brand_href="/",
    color="primary",
    dark=True,
)