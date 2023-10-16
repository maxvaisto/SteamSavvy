import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('About page'),
    html.H4('SteamSavvy has the goal of giving company performance insights about the steam market data.'
            'Special focus is given to find exploitable sections in the steam game market.'),
    html.H4('SteamSavvy is a project made by Linsen Gao, Sergei Panarin and Max Väistö created for the Introduction'
            ' to Data Science course in Helsinki University.'),

], className="custom_body")


dash.register_page(
    __name__,
    title="Dashboard",
    description="Main dashboard",
    path="/about",
)