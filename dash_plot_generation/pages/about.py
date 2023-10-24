import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div(children=[
        html.H1('About page', style={'margin-bottom': '50px'}),
        html.H4('SteamSavvy has the goal of giving company performance insights about the steam market data.'
                'Special focus is given to find exploitable sections in the steam game market.'),
        html.H4('SteamSavvy is a project made by Linsen Gao, Sergei Panarin and Max Väistö created for the Introduction'
                ' to Data Science course in Helsinki University.'),

    ],
        style={'margin-left': '150pxpx', 'margin-top': '400px', 'margin-right':'400px'}
    ),



], className="custom_body")


dash.register_page(
    __name__,
    title="Dashboard",
    description="Main dashboard",
    path="/about",
)