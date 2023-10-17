import dash
from dash import html

global APP

dash.register_page(__name__, path='/')

layout = html.Div(
    children=[
    html.Div(children=[
        html.H1('SteamSavvy',
                className="heading-1"),
        html.H3("Steam API data analysis dashboard",
                className="heading-3"),
        # html.H4('Discover the full potential of steam data for market analysis.', className="heading-3"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.A("Dashboard", className="heading-4", href="/dashboard"),
                        html.P("Discover market trends on Steam", className="sub-text")
                    ],
                    className="container-3"
                ),
                html.Div(
                    children=[
                        html.A("About", className="heading-4", href="/about"),
                        html.P("Learn more about the website", className="sub-text")
                    ],
                    className="container-3"
                ),
                html.Div(
                    children=[
                        html.A('Technical report',
                               className="heading-4", href="",
                               download='dark city.jpg', target="_blank",),
                        html.P("Read the project documentation", className="sub-text")
                    ],
                    className="container-3"
                )
            ],
            className="container-2"
        )
    ],
             className="container-1"),


    ],
    style={},
    className="body")