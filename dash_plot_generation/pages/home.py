import dash
from dash import html, dcc

from dash_plot_generation.styles_and_handles import DOWNLOAD_MAIN_PAGE

global app
dash.register_page(__name__, path='/')

layout = html.Div(
    children=[
    html.Div(children=[
        html.H1('SteamSavvy',
                className="heading-1"),
        html.H3("Steam API data analysis dashboard.",
                className="heading-3"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.A("Dashboard", className="heading-4", href="/dashboard"),
                        html.H5("Discover market trends on Steam", className="sub-text")
                    ],
                    className="container-3"
                ),
                html.Div(
                    children=[
                        html.A("About", className="heading-4", href="/about"),
                        html.H5("Learn more about the website", className="sub-text")
                    ],
                    className="container-3"
                ),
                html.Div(
                    children=[
                        html.A('Technical report',
                               className="heading-4", id=DOWNLOAD_MAIN_PAGE),
                        html.H5("Read the project documentation", className="sub-text"),
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