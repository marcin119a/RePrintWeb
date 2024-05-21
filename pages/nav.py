import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Start page", href="/", id="nav-home")),
        dbc.NavItem(dbc.NavLink("Upload your signatures", href="/page1", id="nav-page1")),
    ],
    brand="Reprint",
    brand_href="/",
    color="primary",
    dark=True,
)