import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('SteamSavvy'),

    html.H4('Discover the full potential of steam data for market analysis.'),

], className="custom_body")