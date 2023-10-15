
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

from visual_presentation.Distribution_of_review_rating import get_rating_density_plot

RATING_MIN_REVIEWS = "min_reviews_id"

RATING_SLIDER = "rating_slider"

RATING_TABLE = "rating_data_table"

RATING_DISTRIBUTION_PLOT = "game_popularity_density_plot"

MAIN_PANEL_TAB_DICT = {'height': '550px', 'width': '100%', 'margin': '0', 'overflow': 'auto'}

SPACE_NORMAL_ENTRY = 35

DEV_AVERAGE_RATING_LABEL = "dev_average_rating"

RIGHT_SIDE_TEXT_DICT = {'display': 'inline-block',
                        'float': 'right', 'margin-right': '0%', 'margin-bottom': '0px'}

DEFAULT_PLOT_STYLE_DICT = dict(
    template="plotly_dark",
    plot_bgcolor="rgb(31,46,65)",
    paper_bgcolor="rgb(31,46,65)",
)

DENSITY_LAYOUT_STYLE = DEFAULT_PLOT_STYLE_DICT | dict(
    title='Distribution of Game Review Rating',
    xaxis_title="Game user rating",
    yaxis_title="Proportion"

)

DARK_STEAM = "rgb(23,29,37)"
WHITE_STEAM = "rgb(235,235,235)"
TITLE_WHITE_STEAM = "rgb(197,195,192)"
DARK_BLUE_STEAM = "rgb(27,40,56)"
TAB_COLOR = "rgb(31,46,65)"
TAB_EDGE = "rgb(37,55,77)"
DROPDOWN_COLOR = "rgb(50,70,101"
SMALL_PANEL_COLOR = "rgb(22,32,45)"

layout = dict(template="plotly_dark", plot_bgcolor="rgb(31,46,65)", paper_bgcolor="rgb(31,46,65)")
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

NORMAL_DIVISION_DICT = SMALL_PANEL_DICT | {'width': '60%', 'height': '100%', 'margin-right': '5%', 'padding-left': '5%',
                                           'margin-bottom': '5%', 'background-color': TAB_COLOR}

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

FULL_DATA = None
OWNER_RANGE_PARTS_SORTED = None

DASH_ASSETS_PATH = "dash_assets"

APP = dash.Dash(
    name=__name__,
    assets_folder=DASH_ASSETS_PATH,
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
)


def initialize_data():
    global FULL_DATA, OWNER_RANGE_PARTS_SORTED
    dataframe = None
    for file in os.listdir(split_csv_path):
        file_path = os.path.join(split_csv_path, file)
        dataframe = pandas.concat([dataframe, pandas.read_csv(file_path)]) if dataframe is not None \
            else pandas.read_csv(file_path)

    add_game_revenues_and_owner_means(dataframe)
    owner_ranges = {value_range for value_range in dataframe["owners"].unique()}

    ranges_test = [(convert_owners_to_limits(value_range), value_range.split(" .. ")) for value_range in owner_ranges]
    unique_owner_values = {(limits[i], limits_str[i]) for (limits, limits_str)
                           in ranges_test for i in range(2)}
    sorted_owner_list = sorted(unique_owner_values, key=lambda range: range[0])

    OWNER_RANGE_PARTS_SORTED = sorted_owner_list
    FULL_DATA = dataframe


@APP.callback(Output(RATING_DISTRIBUTION_PLOT, "figure"),
              Output("Game pop bottom_region", 'children'),
              Input(RATING_SLIDER, "value"),
              Input(RATING_MIN_REVIEWS, "value"))
def update_density_filter_plot(rating_range, min_reviews):
    global FULL_DATA, OWNER_RANGE_PARTS_SORTED

    allowed_indexes = [str_val for (val, str_val) in OWNER_RANGE_PARTS_SORTED[rating_range[0]:rating_range[1] + 1]]
    allowed_ratings = [" .. ".join([val, allowed_indexes[i + 1]]) for (i, val) in enumerate(allowed_indexes)
                       if i < len(allowed_indexes) - 1]

    output = get_rating_density_plot(FULL_DATA, allowed_ratings, min_reviews, layout=DENSITY_LAYOUT_STYLE)
    table = html.Div(dash.dash_table.DataTable(output['top_games']['non_free'].to_dict('records'),
                                               id=RATING_TABLE,

                                               style_data={'backgroundColor': TAB_COLOR,
                                                           'color': WHITE_STEAM,
                                                           'border': '1px solid ' + TAB_EDGE},
                                               style_header={'backgroundColor': TAB_HEADER_COLOR,
                                                             'color': WHITE_STEAM,
                                                             'border': '1px solid ' + TAB_EDGE}))
    return output['fig'], [table]


@APP.callback([Output(DEV_REVENUE_LABEL, "children"),
               Output(DEV_TOP_GENRES_LABEL, "children"),
               Output(DEV_CCU_LABEL, "children"),
               Output(DEV_GAME_COUNT_LABEL, "children"),
               Output(DEV_REV_PER_GAME_LABEL, "children"),
               Output(DEV_TOP_GAMES, "children"),
               Output(DEV_AVERAGE_RATING_LABEL, "children")],
              inputs=[Input(DEVELOPER_DROPDOWN, "value")])
def update_dev_info(dev_name):
    global FULL_DATA, OWNER_RANGE_PARTS_SORTED
    if not (dev_name and isinstance(FULL_DATA, pandas.DataFrame)):
        raise PreventUpdate

    # Remove empty rows
    mask = FULL_DATA.developer.apply(lambda x: dev_name in x if isinstance(x, str) else False)
    dev_data = FULL_DATA[mask]

    # Engineer revenue data into the dataframe
    # add_game_revenues_and_owner_means(dev_data)

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


def get_genre_popularity_counts(df, group_after_largest=8):
    genre_df = df[["genres", "owner_means", "game_revenue"]]
    genre_owners = {}
    genre_revenue = {}

    for index, row in genre_df.iterrows():
        if not isinstance(row.genres, str):
            continue
        genre_list = row.genres.split(", ")
        for genre in genre_list:
            if genre in genre_owners.keys():
                genre_owners[genre] += row["owner_means"]
                genre_revenue[genre] += row["game_revenue"]
            else:
                genre_owners[genre] = row["owner_means"]
                genre_revenue[genre] = row["game_revenue"]
    top_owners = dict(Counter(genre_owners).most_common(group_after_largest))
    top_revenue = dict(Counter(genre_revenue).most_common(group_after_largest))
    top_owners["Other"] = sum([val for (key, val) in genre_owners.items()
                               if key not in top_owners.keys()])
    top_revenue["Other"] = sum([val for (key, val) in genre_revenue.items()
                                if key not in top_revenue.keys()])

    return top_owners, top_revenue


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

    global APP, FULL_DATA, DEMO_PLOT_COLORS, DEMO_PLOT_LABELS, OWNER_RANGE_PARTS_SORTED

    # unique_publishers = extract_unique_companies(df["publisher"].apply(lambda x: split_companies(x)))
    # unique_developers = extract_unique_companies(df["developer"].iloc[0:10].apply(lambda x: split_companies(x)))
    unique_publishers = ["Valve"]
    unique_developers = ["Valve"]

    # Genre performance table_values
    # genre_owners, genre_revenue = get_genre_popularity_counts(FULL_DATA, 6)
    genre_owners = {key: val for (key, val) in
                    zip(["Action", "Adventure", "RPG", "Puzzle", "Strategy", "Other"],
                        [0.7, 0.5, 0.1, 0.4, 0.3, 0.7])}
    genre_revenue = {key: val for (key, val) in
                     zip(["Action", "Adventure", "RPG", "Puzzle", "Strategy", "Other"],
                         [0.5, 0.4, 0.3, 0.4, 0.6, 0.7])}

    # Game popularity filter values
    max_reviews = numpy.nanmax(FULL_DATA.apply(lambda x: x["positive"] + x["negative"], axis=1))
    owner_range_dict = {index: val_str for (index, (val, val_str)) in enumerate(OWNER_RANGE_PARTS_SORTED)}
    min_owner = min(owner_range_dict.keys())
    max_owner = max(owner_range_dict.keys())

    APP.css.append_css({
        'external_url': 'styles.css'
    })
    APP.layout = html.Div(
        children=[
            html.Nav(className="nav nav-pills", children=[
                html.H6("SteamSavvy - Steam game data insights",
                        style={"margin-left": "60px", "width": "20%", "display": "inline-block"}),
                html.A('About', className="nav-item nav-link btn", href='/Documentation/About',
                       style={"margin-left": "300px"}),
                html.A('Technical report', className="nav-item nav-link active btn", href='/Documentation/Report',
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
                                                html.Div(style=NORMAL_DIVISION_DICT,
                                                         children=[dcc.Graph(
                                                             figure=go.Figure(data=[
                                                                 {'x': ["Action", "Adventure", "RPG", "Puzzle",
                                                                        "Strategy"],
                                                                  'y': [0.7, 0.4, 0.8, 1.2, 1.3],
                                                                  'type': 'bar'},
                                                             ],
                                                                 layout=DEFAULT_PLOT_STYLE_DICT |
                                                                        dict(title="Relative genre perfomance")
                                                             ),

                                                         ),
                                                             html.P(f"""Genre performance measures the assessed 
                                                             exploitability of the specific game genre. The assessment 
                                                             is done by estimating the genre popularity, and games 
                                                             developed in the next two years and showing the relative 
                                                             differences between the genres.""")]),
                                                html.Div(style=SMALL_PANEL_DICT | {'width': '35%', 'height': '100%',
                                                                                   'background-color': TAB_COLOR},
                                                         children=[
                                                             html.Div(children=[
                                                                 html.Div(style={'width': '100%', 'height': '50%'},
                                                                          children=[dcc.Graph(
                                                                              figure=go.Figure(data=[go.Pie(
                                                                                  labels=list(genre_owners.keys()),
                                                                                  values=list(genre_owners.values()),
                                                                                  sort=False)],
                                                                                  layout=DEFAULT_PLOT_STYLE_DICT |
                                                                                         dict(title="Genre popularity",
                                                                                              margin=dict(l=20, r=20,
                                                                                                          t=50, b=20))),
                                                                              style={'width': '100%',
                                                                                     'height': '100%'})]),
                                                                 html.Div(style={'width': '100%', 'height': '50%'},
                                                                          children=[dcc.Graph(
                                                                              figure=go.Figure(data=[go.Pie(
                                                                                  labels=list(genre_revenue.keys()),
                                                                                  values=list(genre_revenue.values()),
                                                                                  sort=False)],
                                                                                  layout=DEFAULT_PLOT_STYLE_DICT |
                                                                                         dict(
                                                                                             title="Genre revenue share",
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
                                            html.H5("Genre prediction", style={'margin-bottom': '50px'}),
                                            html.Div(children=[
                                                html.Div(children=[
                                                    html.P("Selected genre:", style={'margin-bottom': '10px'}),
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
                                                    style={'width': '100%', 'margin-bottom': '50px'})
                                            ]),
                                            dcc.Graph(figure=go.Figure(layout=DEFAULT_PLOT_STYLE_DICT |
                                                                              dict(title="Genre prediction plot",
                                                                                   margin=dict(l=20, r=20,
                                                                                               t=50, b=20)))),
                                            html.P("""This is an individual regression estimate for the genre that represents
                                        the estimated amount of games to be produced in the next two years""")

                                        ], style=NORMAL_DIVISION_DICT | {'width': '90%'})

                                    ],
                                        style=MAIN_PANEL_TAB_DICT,
                                        className="scrollable")
                                ]),
                        dcc.Tab(label="Game popularity", value="tab2",
                                style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT,
                                children=[
                                    html.Div(id="Game pop general layout",
                                             style=MAIN_PANEL_TAB_DICT,
                                             className="scrollable",
                                             children=[
                                                 html.Div(id="Game pop top div",
                                                          children=[
                                                              html.Div(id="game popularity filters",
                                                                       style=NORMAL_DIVISION_DICT | {'width': '100%',
                                                                                                     'height': '100%',
                                                                                                     'margin_left': '0px',
                                                                                                     'margin_right': '0px',
                                                                                                     'background-color': TAB_COLOR,
                                                                                                     'display': 'inline-block'},

                                                                       children=[
                                                                           html.P("Filters"),
                                                                           html.Small("Number of game owners"),
                                                                           dcc.RangeSlider(id=RATING_SLIDER,
                                                                                           min=min_owner, max=max_owner,
                                                                                           marks=owner_range_dict,
                                                                                           step=None,
                                                                                           value=[min_owner,
                                                                                                  max_owner]),
                                                                           html.Small("Minimum amount of reviews"),
                                                                           dcc.Input(id=RATING_MIN_REVIEWS,
                                                                                     type="number", min=0,
                                                                                     max=max_reviews, step=1, value=0)
                                                                       ]
                                                                       ),
                                                              html.Div(
                                                                  children=[dcc.Graph(id=RATING_DISTRIBUTION_PLOT)],
                                                                  style=NORMAL_DIVISION_DICT | {'width': '100%',
                                                                                                'display': 'inline-block'}
                                                              )
                                                          ]
                                                          ),
                                                 html.Div(id="Game pop bottom_region",
                                                          style=NORMAL_DIVISION_DICT | {'width': '90%',
                                                                                        'overflow': 'auto',
                                                                                        'height': '70%'},
                                                          className="scrollable",
                                                          children=[
                                                              html.Div(dash.dash_table.DataTable(id=RATING_TABLE
                                                                                                 ))
                                                          ])
                                             ]
                                             ),
                                ]
                                ),
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
                    style=PANEL_DEFAULT_DICT | {'width': '700px',
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
