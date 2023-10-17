
# html handles
RATING_MIN_REVIEWS = "min_reviews_id"
RATING_SLIDER = "rating_slider"
RATING_TABLE = "rating_data_table"
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
DEV_TOP_GENRES_LABEL = "dev_top_genres"
DEVELOPER_DROPDOWN = "developer_dropdown"
RATING_DISTRIBUTION_PLOT = "game_popularity_density_plot"
DEV_AVERAGE_RATING_LABEL = "dev_average_rating"


MAIN_PANEL_TAB_DICT = {'height': '550px', 'width': '100%', 'margin': '0', 'overflow': 'auto'}
SPACE_NORMAL_ENTRY = 35
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
TAB_HEADER_COLOR = "rgb(45,96,150)"

DEFAULT_TABS_DICT = {'width': 'auto', 'display': 'flex',
                     'background-color': TAB_COLOR, 'border-color': TAB_EDGE}
TAB_NORMAL_DICT = {'background-color': TAB_COLOR, 'color': TITLE_WHITE_STEAM,
                   'border': '0px solid',
                   'font-size': '15px'}
TAB_HIGHLIGHT_DICT = {'backgroundColor': TAB_HEADER_COLOR, 'color': 'white', "border-color": "transparent",
                      'font-size': '15px'}
PANEL_DEFAULT_DICT = {'display': 'inline-block',
                      'background-color': TAB_COLOR, 'border': '2px solid', 'border-color': TAB_EDGE,
                      'color': WHITE_STEAM, 'height': '720px'}
SMALL_PANEL_DICT = {'float': 'left', 'background-color': 'transparent', 'box-sizing': 'border-box',
                    'padding': '10px'}
SMALL_TAB_PANEL_DICT = SMALL_PANEL_DICT | {'width': '48%', 'height': '75%',
                                           'margin-bottom': '0px',
                                           'padding-top': '4%', 'padding-bottom': '0%', 'padding-left': '5%',
                                           'padding-right': '5%',
                                           'margin-top': '0px',
                                           'overflow': 'auto'
                                           }
SMALL_PANEL_HEADER_DICT = {'text-align': 'center', 'padding-top': '2%', 'padding-bottom': '2%'}
LIST_DICT = {'display': 'inline-block', 'margin-bottom': '0px', 'padding-right': '0px'}
NORMAL_DIVISION_DICT = SMALL_PANEL_DICT | {'width': '60%', 'height': '100%', 'margin-right': '5%', 'padding-left': '5%',
                                           'margin-bottom': '5%', 'background-color': TAB_COLOR}
RATING_TABS = "rating_tabs"
RATING_TABS_OUTPUT_AREA = "table-area"
