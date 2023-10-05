import math
import os

import numpy
import pandas
from dash import dash, dcc, html, Output, Input
from collections import Counter
from dash_plot_generation.utils import split_companies, extract_unique_companies, convert_owners_to_limits, \
    get_owner_means

DARK_STEAM = "rgb(23,29,37)"
WHITE_STEAM = "rgb(235,235,235)"
TITLE_WHITE_STEAM = "rgb(197,195,192)"
DARK_BLUE_STEAM = "rgb(27,40,56)"
TAB_COLOR = "rgb(31,46,65)"
TAB_EDGE = "rgb(37,55,77)"
DROPDOWN_COLOR = "rgb(50,70,101"



DEFAULT_TABS_DICT = {'width': 'auto', 'display': 'flex',
                   'background-color': TAB_COLOR, 'border-color': TAB_EDGE}
TAB_HEADER_COLOR = "rgb(45,96,150)"
DEVELOPER_DROPDOWN = "developer_dropdown"
TAB_NORMAL_DICT = {'background-color' : TAB_COLOR, 'color': TITLE_WHITE_STEAM,
                   'border' : '0px solid',
                   'font-size': '15px',
                   'border_bottom' : '2px solid ' + TAB_EDGE}
TAB_HIGHLIGHT_DICT = {'backgroundColor': TAB_HEADER_COLOR, 'color': 'white', "border-color": "transparent",
                      'font-size': '15px'}
PANEL_DEFAULT_DICT = {'display': 'inline-block',
                    'background-color': TAB_COLOR, 'border' : '2px solid', 'border-color': TAB_EDGE,
                    'color': WHITE_STEAM}
DEV_TOP_GENRES_LABEL = "dev_top_genres"

DEV_CCU_LABEL = "dev_ccu"

DEV_GAME_COUNT_LABEL = "dev_game_count"

DEV_REV_PER_GAME_LABEL = "dev_rev_per_game"

DEV_REVENUE_LABEL = "dev_revenue"

DEV_TOP_GAMES = "dev_top_games"

csv_path = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "api_exploration")
split_csv_path = os.path.join(csv_path, "file_segments")

df = None
DASH_ASSETS_PATH = "dash_assets"

APP = dash.Dash(
    name=__name__,
    assets_folder=DASH_ASSETS_PATH,
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
)


def initialize_data():
    global df
    files = os.listdir(split_csv_path)
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
               Output(DEV_TOP_GAMES, "children")],
              inputs=[Input(DEVELOPER_DROPDOWN, "value")])
def update_dev_info(dev_name):
    global df
    mask = df.developer.apply(lambda x: dev_name in x if isinstance(x, str) else False)
    dev_data = df[mask]
    ccu = sum(dev_data["ccu"])
    dev_data["owner_means"] = dev_data["owners"].apply(lambda x: get_owner_means(convert_owners_to_limits(x)))
    dev_data["game_prices"] = dev_data["price"]
    dev_data["game_revenue"] = pandas.Series([owner_count * game_price for (owner_count, game_price) in
                                              zip(dev_data["owner_means"], dev_data["game_prices"]) if
                                              not (pandas.isna(game_price) or pandas.isna(owner_count))])
    genre_totals = [genre for genre_list in dev_data["genres"] if isinstance(genre_list, str)
                    for genre in genre_list.split(", ")]
    genre_counts = Counter(genre_totals).most_common(3)
    top_games = dev_data.sort_values(by=["game_revenue"], ascending=False)["name"].head(3)
    # top_genres = dict(sorted(genre_totals.items(), key=lambda x: x[1], reverse=True)[:4])
    return str(numpy.nansum(dev_data["game_revenue"])), \
        ", ".join([genre_c[0] for genre_c in genre_counts]), \
        str(ccu), \
        str(dev_data.shape[0]), \
        str(round(numpy.nansum(dev_data["game_revenue"]) / len(dev_data["game_revenue"]))), \
        "\n".join(top_games)


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

    global APP, df

    # unique_publishers = extract_unique_companies(df["publisher"].apply(lambda x: split_companies(x)))
    unique_developers = extract_unique_companies(df["developer"].apply(lambda x: split_companies(x)))
    unique_publishers = ["Valve"]
    #unique_developers = ["Valve"]

    APP.css.append_css({
        'external_url': 'styles.css'
    })
    APP.layout = html.Div(
        children=[
            html.Div(
                # style={'background-image': 'url("/assets/background_image.jpg")',
                style={'background-color': 'rgb(27,40,56)',
                       'background-size': 'cover',
                       #'background-repeat': 'no-repeat',
                       #'background-position': 'center',
                       'height': '100vh',  # Adjust this to set the desired height
                       #'filter': 'blur(5px)',  # Adjust the blur intensity as needed,
                       'position': 'absolute',  # Position the background div absolutely
                       'width': '100%',  # Make the background div cover the entire width
                       'z-index': '-1'  # Place the background div behind other content
                       },
            ),
            html.Nav(className="nav nav-pills", children=[
                html.H6("STEAM-SAVVY", style={"margin-left": "30px", "width": "20%", "display": "inline-block"}),
                html.A('About', className="nav-item nav-link btn", href='/apps/App1',
                       style={"margin-left": "300px"}),
                html.A('Technical report', className="nav-item nav-link active btn", href='/apps/App2',
                       style={"margin-left": "150px"})
            ],
                     style={"background-color": "rgb(23,29,37)", "color": "rgb(197,195,192)"}),
            html.Div(className="row", children=[
                html.Div(children=[
                    dcc.Tabs(id="tabs_main_plots1", value="tab1", children=[
                        dcc.Tab(label="Genre performance", value="tab1",
                                style = TAB_NORMAL_DICT, selected_style= TAB_HIGHLIGHT_DICT),
                        dcc.Tab(label="Game popularity", value="tab2",
                                style = TAB_NORMAL_DICT, selected_style= TAB_HIGHLIGHT_DICT),
                        dcc.Tab(label="Company revenues", value="tab3",
                                style = TAB_NORMAL_DICT, selected_style= TAB_HIGHLIGHT_DICT),
                        dcc.Tab(label="Market performance", value="tab4",
                                style = TAB_NORMAL_DICT, selected_style= TAB_HIGHLIGHT_DICT),
                    ],
                             style=DEFAULT_TABS_DICT),
                ], style= PANEL_DEFAULT_DICT | {'width': 'calc(50% - 10px)', 'height': '600px',
                                                'margin-right': '200px'}),
                html.Div(children=[
                    dcc.Tabs(id="tabs_main_plots2", value="tab3", children=[
                        dcc.Tab(label="Developer infromation", value="tab3", children=[
                            html.Div(children=[
                                dcc.Dropdown(id=DEVELOPER_DROPDOWN, value="Valve",
                                             options=[{"label": developer, "value": developer} for developer in
                                                      unique_developers],
                                             style={'margin-top': '5px'},
                                             className='dash-dropdown'
                                             ),
                                html.Div(children=[
                                    html.H6("General statistics"),
                                    html.Div(  # Revenue
                                        children=[html.P("Revenue"),
                                                  html.Div(children=[
                                                      html.P("Total game sale revenue"),
                                                      html.Small(id=DEV_REVENUE_LABEL, children="524.245.000€"),
                                                      html.P("Total game sale revenue per game"),
                                                      html.Small(id=DEV_REV_PER_GAME_LABEL, children="92.625.000€"),
                                                      html.P("Highest game sale revenue games:"),
                                                      html.Small(id=DEV_TOP_GAMES, children="Half life 2"),

                                                  ])
                                                  ],
                                        style={'width': '48%', 'height': '100%', 'float': 'left', 'outline': '2px dotted black'}
                                    ),
                                    html.Div(children=[
                                        html.Div(children=[
                                            html.P("Number of games", style={"margin-top": "0"}),
                                            html.Small(id=DEV_GAME_COUNT_LABEL, children="5"),
                                            html.P("Number of concurrent users"),
                                            html.Small(id=DEV_CCU_LABEL, children="92.625.000€"),
                                            html.P("Most common game genres"),
                                            html.Small(id=DEV_TOP_GENRES_LABEL, children="FPS, Action, Puzzle"),
                                            html.P("Average game rating"),
                                        ])

                                    ], style={'width': '48%', 'height': '100%', 'float': 'left', 'outline': '2px dotted black'}
                                    )
                                ])
                            ], style={'margin-left': '20px', 'margin-right': '20px'}
                            )
                        ], style = TAB_NORMAL_DICT, selected_style= TAB_HIGHLIGHT_DICT),
                        dcc.Tab(label="Publisher information", value="tab4", children=[

                            dcc.Dropdown(id="publisher_dropdown", value="Valve",
                                         options=[{"label": publisher, "value": publisher} for publisher in
                                                  unique_publishers],
                                         ),
                        ],style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT)

                    ],
                             style=DEFAULT_TABS_DICT),
                ],
                    style=PANEL_DEFAULT_DICT | {'width': 'calc(30% - 10px)', 'height': '600px'})
            ],
                     style={'width': '100%', "padding-top": "15px", 'padding-left': "50px"}),
        ],
        style={"font-family": "Tahoma"}
        )
    APP.run(host=host, **kwargs)
    print("The server has closed!")


if __name__ == "__main__":
    initialize_data()
    initialize_dash(debug=True)

print(csv_path)
