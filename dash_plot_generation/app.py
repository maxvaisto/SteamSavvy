import dash
import pandas
from dash import html, dash, Output, Input
from dash.exceptions import PreventUpdate

from dash_plot_generation.data_store import initialize_data, OWNER_RANGE_PARTS_SORTED, FULL_DATA
from dash_plot_generation.utils import get_average_user_rating_label, get_game_count_label, get_top_revenue_game_labels, \
    get_total_revenue_label, get_top_genre_labels, get_ccu_label, get_average_game_rev_label
from dash_plot_generation.styles_and_handles import RATING_MIN_REVIEWS, RATING_SLIDER, RATING_TABLE, \
    RATING_DISTRIBUTION_PLOT, DEV_AVERAGE_RATING_LABEL, DENSITY_LAYOUT_STYLE, WHITE_STEAM, TAB_COLOR, TAB_EDGE, \
    TAB_HEADER_COLOR, DEVELOPER_DROPDOWN, DEV_TOP_GENRES_LABEL, DEV_CCU_LABEL, DEV_GAME_COUNT_LABEL, \
    DEV_REV_PER_GAME_LABEL, DEV_REVENUE_LABEL, DEV_TOP_GAMES
from visual_presentation.Distribution_of_review_rating import get_rating_density_plot

APP = dash.Dash(
    name=__name__,
    use_pages=True,
    external_stylesheets=['/assets/styles.css',
                          'https://codepen.io/chriddyp/pen/bWLwgP.css']
)

# APP.css.append_css({
#    'external_url': 'styles.css'
# })

APP.layout = html.Div([
    html.Nav(className="navbar", children=[
        html.H6("SteamSavvy - Steam game data insights",
                style={"margin-left": "60px", "display": "inline-block"},
                className="nav-item-1"),
        html.A('About', className="nav-item nav-link btn", href='/about',
               style={"margin-left": "150px"},),
        html.A('Dashboard', className="nav-item nav-link btn", href='/dashboard',
               style={"margin-left": "150px"}),
        html.A('Technical report', className="nav-item nav-link active btn", href='/Documentation/Report',
               style={"margin-left": "150px"})
    ]),

    dash.page_container
], className="body")


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


@APP.callback(Output(RATING_DISTRIBUTION_PLOT, "figure"),
              Output("Game pop bottom_region", 'children'),
              Input(RATING_SLIDER, "value"),
              Input(RATING_MIN_REVIEWS, "value"))
def update_density_filter_plot(rating_range, min_reviews):
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


if __name__ == "__main__":
    initialize_data()
    APP.run_server(debug=True, host="0.0.0.0")
