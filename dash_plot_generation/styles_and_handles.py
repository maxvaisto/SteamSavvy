# html handles
import os

RATING_MIN_REVIEWS = "min_reviews_id"
RATING_SLIDER = "rating_slider"
RATING_TABLE = "rating_data_table"


DEV_CCU_LABEL = "dev_ccu"
DEV_GAME_COUNT_LABEL = "dev_game_count"
DEV_REV_PER_GAME_LABEL = "dev_rev_per_game"
DEV_REVENUE_LABEL = "dev_revenue"
DEV_TOP_GAMES = "dev_top_games"
DEVELOPER_DROPDOWN = "developer_dropdown"
DEV_TOP_GENRES_LABEL = "dev_top_genres"

PUB_TOP_GENRES_LABEL = "pub_top_genres"
PUB_CCU_LABEL = "pub_ccu"
PUB_GAME_COUNT_LABEL = "pub_game_count"
PUB_REV_PER_GAME_LABEL = "pub_rev_per_game"
PUB_REVENUE_LABEL = "pub_revenue"
PUB_TOP_GAMES = "pub_top_games"
PUB_AVERAGE_RATING_LABEL = "pub_average_rating"
GAMES_BY_PUB_GRAPH = "game_releases_by_pub_graph"

DEV_AVERAGE_RATING_LABEL = "dev_average_rating"
RATING_DISTRIBUTION_PLOT = "game_popularity_density_plot"
RATING_TABS = "rating_tabs"
RATING_TABS_OUTPUT_AREA = "table-area"
GENRE_DROPDOWN = "genre_dropdown"
GENRE_PREDICTION_GRAPH = "Genre_prediction_graph"
GAMES_BY_DEV_GRAPH = "game_releases_by_dev_graph"

SPACE_NORMAL_ENTRY = 35

# Colors
DARK_STEAM = "rgb(23,29,37)"
WHITE_STEAM = "rgb(235,235,235)"
TITLE_WHITE_STEAM = "rgb(197,195,192)"
DARK_BLUE_STEAM = "rgb(27,40,56)"
TAB_COLOR = "rgb(31,46,65)"
TAB_EDGE = "rgb(37,55,77)"
DROPDOWN_COLOR = "rgb(50,70,101"
SMALL_PANEL_COLOR = "rgb(22,32,45)"
TAB_HEADER_COLOR = "rgb(45,96,150)"

# Plot defaults

DEFAULT_PLOT_STYLE_DICT = dict(
    template="plotly_dark",
    plot_bgcolor=TAB_COLOR,
    paper_bgcolor=TAB_COLOR,
    margin=dict(l=20, r=20, t=50, b=20)
)

DENSITY_LAYOUT_STYLE = DEFAULT_PLOT_STYLE_DICT | dict(
    title='Distribution of Game Review Rating',
    xaxis_title="Game User Rating",
    yaxis_title="Proportion"
)

MARKET_PERFORMANCE_SCATTER = "Market_performance_scatter"
MP_COMPANY_TYPE_DROPDOWN = "market_performance_company_type_dropdown"


def create_market_scatter_plot_style(company_type):
    return {
        **DEFAULT_PLOT_STYLE_DICT,
        'title': f'Market Performance for {company_type} companies',
        "xaxis_title": "Revenue",
        "yaxis_title": "Number of Game Owners",

    }


REVENUE_COMPANY_GAME_COUNT = "revenue_slider_company_popularity"
PUBLISHER_DROPDOWN = "publisher_dropdown"
TOP_REVENUE_COMPANIES = "top_companies_tabs"
TOP_COMPANY_TABLE_AREA = "top_company_area"
PRECALCULATED_DATA_PATH = os.path.normpath(os.getcwd() + os.sep + "precalculated_data")
OWNER_LIST_PATH = os.path.join(PRECALCULATED_DATA_PATH, "sorted_owner_list")
DEVELOPER_LIST_PATH = os.path.join(PRECALCULATED_DATA_PATH, "developer_list")
PUBLISHER_LIST_PATH = os.path.join(PRECALCULATED_DATA_PATH, "publisher_list")
FACTORIZED_GAME_DATAFRAME_PATH = os.path.join(PRECALCULATED_DATA_PATH, "encoded_game_dataframe")
GENRE_LIST_PATH = os.path.join(PRECALCULATED_DATA_PATH, "genre_list")
MAIN_DATAFRAME_PATH = os.path.join(PRECALCULATED_DATA_PATH, "main_dataframe")
GAME_POPULARITY_FILTERS_PATH = os.path.join(PRECALCULATED_DATA_PATH, "game_popularity_filters")

