import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home page", href="/", id="nav-home")),
        dbc.NavItem(dbc.NavLink("Upload your signatures", href="/page1.py", id="nav-page1.py")),
    ],
    brand="SigConfide analyzer",
    brand_href="/",
    color="primary",
    dark=True,
)