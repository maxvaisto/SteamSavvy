import math
import os

import numpy
import pandas
from dash import dash, dcc, html, Output, Input
from collections import Counter
from dash_plot_generation.utils import split_companies, extract_unique_companies, convert_owners_to_limits, \
    get_owner_means, round_to_three_largest_digits, replace_owner_number_with_symbol_real_numeric, \
    convert_to_numeric_str, label_with_rev, label_with_text
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px

SPACE_NORMAL_ENTRY = 35

DEV_AVERAGE_RATING_LABEL = "dev_average_rating"

RIGHT_SIDE_TEXT_DICT = {'display': 'inline-block',
                        'float': 'right', 'margin-right': '0%', 'margin-bottom': '0px'}

DARK_STEAM = "rgb(23,29,37)"
WHITE_STEAM = "rgb(235,235,235)"
TITLE_WHITE_STEAM = "rgb(197,195,192)"
DARK_BLUE_STEAM = "rgb(27,40,56)"
TAB_COLOR = "rgb(31,46,65)"
TAB_EDGE = "rgb(37,55,77)"
DROPDOWN_COLOR = "rgb(50,70,101"
SMALL_PANEL_COLOR = "rgb(22,32,45)"

DEFAULT_TABS_DICT = {'width': 'auto', 'display': 'flex',
                     'background-color': TAB_COLOR, 'border-color': TAB_EDGE}
TAB_HEADER_COLOR = "rgb(45,96,150)"
DEVELOPER_DROPDOWN = "developer_dropdown"
TAB_NORMAL_DICT = {'background-color': TAB_COLOR, 'color': TITLE_WHITE_STEAM,
                   'border': '0px solid',
                   'font-size': '15px',
                   'border_bottom': '2px solid ' + TAB_EDGE}
TAB_HIGHLIGHT_DICT = {'backgroundColor': TAB_HEADER_COLOR, 'color': 'white', "border-color": "transparent",
                      'font-size': '15px'}
PANEL_DEFAULT_DICT = {'display': 'inline-block',
                      'background-color': TAB_COLOR, 'border': '2px solid', 'border-color': TAB_EDGE,
                      'color': WHITE_STEAM, 'height': '600px'}
SMALL_PANEL_DICT = {'float': 'left', 'background-color': 'transparent', 'box-sizing': 'border-box',
                    'padding': '10px'}
SMALL_TAB_PANEL_DICT = SMALL_PANEL_DICT | {'width': '48%', 'height': '100%',
                                           'margin-bottom': '50px',
                                           'padding-top': '4%', 'padding-bottom': '5%', 'padding-left': '5%',
                                           'padding-right': '5%',
                                           'margin-top': '20px'
                                           }
SMALL_PANEL_HEADER_DICT = {'text-align': 'center', 'padding-top': '5%', 'padding-bottom': '2%'}

DEV_TOP_GENRES_LABEL = "dev_top_genres"

LIST_DICT = {'display': 'inline-block', 'margin-bottom': '0px', 'padding-right': '0px'}

DEV_CCU_LABEL = "dev_ccu"

DEV_GAME_COUNT_LABEL = "dev_game_count"

DEV_REV_PER_GAME_LABEL = "dev_rev_per_game"

DEV_REVENUE_LABEL = "dev_revenue"

DEV_TOP_GAMES = "pub_top_games"

PUB_TOP_GENRES_LABEL = "pub_top_genres"

PUB_CCU_LABEL = "pub_ccu"

PUB_GAME_COUNT_LABEL = "pub_game_count"

PUB_REV_PER_GAME_LABEL = "pub_rev_per_game"

PUB_REVENUE_LABEL = "pub_revenue"

PUB_TOP_GAMES = "pub_top_games"
DEMO_PLOT_LABELS = ["Action", "Adventure", "RPG", "Puzzle", "Strategy", "Other"]
DEMO_PLOT_COLORS = list(zip(DEMO_PLOT_LABELS, px.colors.qualitative.G10))
csv_path = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "api_exploration")
split_csv_path = os.path.join(csv_path, "file_segments")
# steam_dark_template = dict(layout=go.Layout(title_font))

df = None
DASH_ASSETS_PATH = "dash_assets"

APP = dash.Dash(
    name=__name__,
    assets_folder=DASH_ASSETS_PATH,
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
)


def initialize_data():
    global df
    dataframe = None
    for file in os.listdir(split_csv_path):
        file_path = os.path.join(split_csv_path, file)
        dataframe = pandas.concat([dataframe, pandas.read_csv(file_path)]) if dataframe is not None \
            else pandas.read_csv(file_path)
    df = dataframe


@APP.callback([Output(DEV_REVENUE_LABEL, "children"),
               Output(DEV_TOP_GENRES_LABEL, "children"),
               Output(DEV_CCU_LABEL, "children"),
               Output(DEV_GAME_COUNT_LABEL, "children"),
               Output(DEV_REV_PER_GAME_LABEL, "children"),
               Output(DEV_TOP_GAMES, "children"),
               Output(DEV_AVERAGE_RATING_LABEL, "children")],
              inputs=[Input(DEVELOPER_DROPDOWN, "value")])
def update_dev_info(dev_name):
    global df
    if not (dev_name and isinstance(df,pandas.DataFrame)):
        raise PreventUpdate

    # Remove empty rows
    mask = df.developer.apply(lambda x: dev_name in x if isinstance(x, str) else False)
    dev_data = df[mask]

    # Engineer revenue data into the dataframe
    add_game_revenues_and_owner_means(dev_data)

    # Top games
    dev_top_games_label = get_top_revenue_game_labels(dev_data)

    # Dev total revenue
    dev_revenue = get_total_revenue_label(dev_data)

    # Dev revenue per game
    dev_game_revenue_per_game = get_average_game_rev_label(dev_data)

    # Top genres
    dev_top_genre_labels = get_top_genre_labels(dev_data)

    # CCU
    dev_ccu = get_ccu_label(dev_data)

    # Game count
    dev_game_count = get_game_count_label(dev_data)

    user_rating_value = get_average_user_rating_label(dev_data)
    return dev_revenue, dev_top_genre_labels, dev_ccu, dev_game_count, dev_game_revenue_per_game, dev_top_games_label, \
        user_rating_value


def get_average_user_rating_label(dev_data):
    value_str = str(round(100 * dev_data["Review_rating"].mean())) + "%"
    label = label_with_text("Average game rating", value_str, SPACE_NORMAL_ENTRY, ".")
    return label


def get_game_count_label(dev_data):
    return label_with_text("Number of games", str(dev_data.shape[0]), SPACE_NORMAL_ENTRY, ".")


def add_game_revenues_and_owner_means(data):
    data["owner_means"] = data["owners"].apply(lambda x: get_owner_means(convert_owners_to_limits(x)))
    data["game_revenue"] = data.apply(lambda x: x["owner_means"] * x["price"] if
    not (pandas.isna(x["owner_means"]) or pandas.isna(x["price"]))
    else 0, axis=1)


def get_top_revenue_game_labels(data):
    top_games = data.sort_values(by=["game_revenue"], ascending=False).head(3)
    top_games_processed = top_games.apply(lambda x: label_with_rev(x["name"], x["game_revenue"], SPACE_NORMAL_ENTRY,
                                                                   ".", "$"), axis=1)
    dev_top_games_with_dot = [" ".join(["•", game]) for game in top_games_processed]
    dev_top_games_label = html.Div("\n".join(dev_top_games_with_dot),
                                   style={'white-space': 'pre-line', 'padding-left': '5%'})
    return dev_top_games_label


def get_total_revenue_label(data):
    top_games_processed = label_with_rev("• Total", numpy.nansum(data["game_revenue"]), SPACE_NORMAL_ENTRY, ".", "$")
    return top_games_processed


def get_top_genre_labels(data):
    genre_totals = [genre for genre_list in data["genres"] if isinstance(genre_list, str)
                    for genre in genre_list.split(", ")]
    genre_counts = Counter(genre_totals).most_common(3)
    top_genres_rows = [label_with_text(genre[0], str(genre[1]), 50, ".") for genre in genre_counts]
    top_genres_with_dot = [" ".join(["•", row]) for row in top_genres_rows]
    top_genre_labels = html.Div("\n".join(top_genres_with_dot),
                                    style={'white-space': 'pre-line', 'padding-left': '5%'})
    return top_genre_labels


def get_ccu_label(data):
    ccu = sum(data["ccu"])
    dev_ccu = convert_to_numeric_str(ccu)

    return label_with_text("Concurrent users", dev_ccu, SPACE_NORMAL_ENTRY, ".")


def get_average_game_rev_label(data):
    game_revenue_per_game_raw = numpy.nansum(data["game_revenue"]) / len(data["game_revenue"])
    dev_game_revenue_per_game_row = label_with_rev("Average", game_revenue_per_game_raw, SPACE_NORMAL_ENTRY, ".", "$")
    dev_game_revenue_per_game = " ".join(["•", dev_game_revenue_per_game_row])
    return dev_game_revenue_per_game


def initialize_dash(host: str = "0.0.0.0", **kwargs):
    """
    Runs the Dash server.
    Args:
        host: IP address of the server
        kwargs: Variables which are passed down to APP.run function as named arguments.
    Note:
        The server IP is not actually 0.0.0.0; if the dash app is not accessible via this address, use the same port
        number but replace the IP address with your local network IP instead.
    """

    global APP, df, DEMO_PLOT_COLORS, DEMO_PLOT_LABELS

    unique_publishers = extract_unique_companies(df["publisher"].apply(lambda x: split_companies(x)))
    unique_developers = extract_unique_companies(df["developer"].iloc[0:10].apply(lambda x: split_companies(x)))
    # unique_publishers = ["Valve"]
    # unique_developers = ["Valve"]

    APP.css.append_css({
        'external_url': 'styles.css'
    })
    APP.layout = html.Div(
        children=[
            html.Nav(className="nav nav-pills", children=[
                html.H6("SteamSavvy - Steam game data insights",
                        style={"margin-left": "60px", "width": "20%", "display": "inline-block"}),
                html.A('About', className="nav-item nav-link btn", href='/apps/App1',
                       style={"margin-left": "300px"}),
                html.A('Technical report', className="nav-item nav-link active btn", href='/apps/App2',
                       style={"margin-left": "150px"})
            ],
                     style={"background-color": "rgb(23,29,37)", "color": "rgb(197,195,192)", 'width': '100%'}),
            html.Div(className="row", children=[
                html.Div(children=[
                    dcc.Tabs(id="main_plots", value="tab1", children=[
                        dcc.Tab(label="Genre performance", value="tab1",
                                style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT,
                                children=[
                                    html.Div(children=[
                                        html.Div(
                                            children=[
                                                html.Div(style=SMALL_PANEL_DICT | {'width': '60%', 'height': '100%',
                                                                                   'margin-right': '5%',
                                                                                   'padding-left': '5%',
                                                                                   'margin-bottom': '5%',
                                                                                   'background-color': TAB_COLOR},
                                                         children=[dcc.Graph(
                                                             figure=go.Figure(data=[
                                                                 {'x': ["Action", "Adventure", "RPG", "Puzzle",
                                                                        "Strategy"],
                                                                  'y': [0.7, 0.4, 0.8, 1.2, 1.3],
                                                                  'type': 'bar'},
                                                             ],
                                                                 layout=dict(template="plotly_dark",
                                                                             title="Relative genre perfomance",
                                                                             plot_bgcolor=TAB_COLOR,
                                                                             paper_bgcolor=TAB_COLOR)),

                                                         ),
                                                             html.P(f"""Genre performance measures the assessed exploitability of the 
                                            specific game genre. The assesment is done by estimating the genre popularity,
                                            and games developed in the next two years and showing the relative differences
                                            between the genres.""")]),
                                                html.Div(style=SMALL_PANEL_DICT | {'width': '35%', 'height': '100%',
                                                                                   'background-color': TAB_COLOR},
                                                         children=[
                                                             html.Div(children=[
                                                                 html.Div(style={'width': '100%', 'height': '50%'},
                                                                          children=[dcc.Graph(
                                                                              figure=go.Figure(data=[go.Pie(
                                                                                  labels=["Action", "Adventure", "RPG",
                                                                                          "Puzzle",
                                                                                          "Strategy",
                                                                                          "Other"],
                                                                                  values=[0.8, 0.3, 0.4, 0.4, 0.3,
                                                                                          0.55],
                                                                                  sort=False)],
                                                                                  layout=dict(template="plotly_dark",
                                                                                              title="Genre popularity",
                                                                                              plot_bgcolor=TAB_COLOR,
                                                                                              paper_bgcolor=TAB_COLOR,
                                                                                              margin=dict(l=20, r=20,
                                                                                                          t=50, b=20))),
                                                                              style={'width': '100%',
                                                                                     'height': '100%'})]),
                                                                 html.Div(style={'width': '100%', 'height': '50%'},
                                                                          children=[dcc.Graph(
                                                                              figure=go.Figure(data=[go.Pie(
                                                                                  labels=["Action", "Adventure", "RPG",
                                                                                          "Puzzle",
                                                                                          "Strategy",
                                                                                          "Other"],
                                                                                  values=[0.7, 0.5, 0.1, 0.4, 0.3, 0.7],
                                                                                  sort=False)],
                                                                                  layout=dict(template="plotly_dark",
                                                                                              title="Genre revenue share",
                                                                                              plot_bgcolor=TAB_COLOR,
                                                                                              paper_bgcolor=TAB_COLOR,
                                                                                              margin=dict(l=20, r=20,
                                                                                                          t=50, b=20))),
                                                                              style={'width': '100%',
                                                                                     'height': '100%'})]
                                                                          )

                                                             ], style={'height': '540px'}
                                                             ),
                                                         ]
                                                         )
                                            ]
                                        ),

                                        html.Div(children=[
                                            html.H5("Genre prediction", style={'margin-bottom':'50px'}),
                                            html.Div(children=[
                                                html.Div(children=[
                                                    html.P("Selected genre:", style={'margin-bottom':'10px'}),
                                                    dcc.Dropdown(id="genre_dropdown", value="action",
                                                                 options=[{"label": html.Span([genre],
                                                                                              style={
                                                                                                  'color': WHITE_STEAM}),
                                                                           "value": genre} for genre in
                                                                          ["action"]],
                                                                 style={'color': WHITE_STEAM, 'display': 'inline-block',
                                                                        'width': '50%'},
                                                                 className='dash-dropdown',
                                                                 ),

                                                ],
                                                    style={'width': '100%', 'margin-bottom':'50px'})
                                            ]),
                                            dcc.Graph(figure=go.Figure(layout=dict(template="plotly_dark",
                                                                                   title="Genre prediction plot",
                                                                                   plot_bgcolor=TAB_COLOR,
                                                                                   paper_bgcolor=TAB_COLOR,
                                                                                   margin=dict(l=20, r=20,
                                                                                               t=50, b=20)))),
                                            html.P("""This is an individual regression estimate for the genre that represents
                                        the estimated amount of games to be produced in the next two years""")

                                        ], style=SMALL_PANEL_DICT | {'height': '100%', 'margin-right': '5%',
                                                                     'padding-left': '5%', 'margin-bottom': '5%',
                                                                     'margin-top': '5%', 'background-color': TAB_COLOR})

                                    ],
                                        style={'height': '550px', 'width': '100%', 'margin': '0', 'overflow': 'auto'},
                                        className="scrollable")
                                ]),
                        dcc.Tab(label="Game popularity", value="tab2",
                                style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT),
                        dcc.Tab(label="Market performance", value="tab4",
                                style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT),
                        dcc.Tab(label="Market prediction tool", value="tab5",
                                style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT),
                    ],
                             style=DEFAULT_TABS_DICT),

                ], style=PANEL_DEFAULT_DICT | {'width': '900px',
                                               'margin-right': '100px', 'padding-left': '50px',
                                               'padding-right': '50px', 'padding-bottom': '50px',
                                               'padding-top': '50px', 'margin-bottom': '50px'
                                               }),
                html.Div(children=[
                    dcc.Tabs(id="company_information", value="tab3", children=[
                        dcc.Tab(label="Developer infromation", value="tab3", children=[
                            html.Div(children=[
                                dcc.Dropdown(id=DEVELOPER_DROPDOWN, value="Valve",
                                             options=[{"label": html.Span([developer], style={'color': WHITE_STEAM}),
                                                       "value": developer} for developer in unique_developers],
                                             style={'margin-top': '20px', 'color': WHITE_STEAM},
                                             className='dash-dropdown',
                                             ),
                                html.Div(children=[
                                    html.Div(
                                        children=[
                                            html.Div(
                                                children=[html.P("Revenue", style=SMALL_PANEL_HEADER_DICT)],
                                                style={'margin-bottom': '10%',
                                                       'border-bottom': '2px solid ' + TAB_EDGE}),
                                            html.Div(children=[
                                                html.Div(children=[
                                                    html.P("Game sale revenue estimates"),
                                                    html.Div(children=[
                                                        html.Div(children=[
                                                            html.P(id=DEV_REVENUE_LABEL, children="$524 M",
                                                                   style=LIST_DICT | {'padding-left': '5%'})
                                                        ]),
                                                        html.Div(children=[
                                                            html.P(id=DEV_REV_PER_GAME_LABEL, children="$925 M",
                                                                   style=LIST_DICT | {'padding-left': '5%'})
                                                        ]),
                                                    ],
                                                        style={'margin-bottom': '20px'}),
                                                    html.Div(children=[
                                                        html.P("Top games by revenue:"),
                                                        html.Small(id=DEV_TOP_GAMES, children="Half life 2"),
                                                    ])
                                                ]),
                                            ], style={'padding-left': '5%', 'padding-right': '5%',
                                                      'padding-bottom': '5%'})
                                        ],
                                        style=SMALL_TAB_PANEL_DICT | {'margin-right': '20px', 'margin-left': '0px'}
                                    ),
                                    html.Div(children=[
                                        html.Div(
                                            children=[
                                                html.Div(
                                                    children=[html.P("General information",
                                                                     style=SMALL_PANEL_HEADER_DICT)],
                                                    style={'margin-bottom': '30px',
                                                           'border-bottom': '2px solid ' + TAB_EDGE}),
                                                html.Div(children=[
                                                    html.Div(children=[
                                                        html.P(id=DEV_GAME_COUNT_LABEL, children="5",
                                                               style=LIST_DICT),
                                                    ],
                                                        style={'margin-bottom': '10px'}
                                                    ),
                                                    html.Div(children=[
                                                        html.P(id=DEV_CCU_LABEL, children="",
                                                               style=LIST_DICT),
                                                    ],
                                                        style={'margin-bottom': '10px'}
                                                    ),
                                                    html.Div(children=[
                                                        html.P("Popular game genres:"),
                                                        html.Small(id=DEV_TOP_GENRES_LABEL,
                                                                   children="FPS, Action, Puzzle"),
                                                    ],
                                                        style={'margin-bottom': '10px'}
                                                    ),
                                                    html.Div(children=[
                                                        html.P(id=DEV_AVERAGE_RATING_LABEL,
                                                               children="",
                                                               style=LIST_DICT)
                                                    ])
                                                ])
                                            ])

                                    ], style=SMALL_TAB_PANEL_DICT | {'width': '45%', 'height': '100%',
                                                                     'margin-right': '0px', 'margin-left': '20px'}
                                    )
                                ], style={'height': '100%'})
                            ], style={'margin-left': '20px', 'margin-right': '0px'}
                            )
                        ], style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT),
                        dcc.Tab(label="Publisher information", value="tab4", children=[

                            dcc.Dropdown(id="publisher_dropdown", value="Valve",
                                         options=[{"label": publisher, "value": publisher} for publisher in
                                                  unique_publishers],
                                         ),
                        ], style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT)

                    ],
                             style=DEFAULT_TABS_DICT),
                ],
                    style=PANEL_DEFAULT_DICT | {'width':'700px',
                                                'padding-left': '50px',
                                                'padding-right': '50px', 'padding-bottom': '50px',
                                                'padding-top': '50px', 'margin-bottom': '50px'
                                                })
            ],
                     style={'width': '100%', "padding-top": "30px", 'padding-left': "50px"}),
        ],
        style={"font-family": "Tahoma"}
    )
    APP.run(host=host, **kwargs)
    print("The server has closed!")


if __name__ == "__main__":
    initialize_data()
    initialize_dash(debug=True)

print(csv_path)
