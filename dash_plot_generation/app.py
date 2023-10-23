import dash
import pandas
from dash import html, dash, Output, Input, dcc
from dash.exceptions import PreventUpdate

from Project_data_processor_ML import get_genre_plot
from dash_plot_generation.data_store import initialize_data, FULL_DATA, OWNER_RANGE_PARTS_SORTED, LABEL_ENCODED_DATASET
from dash_plot_generation.styles_and_handles import RATING_MIN_REVIEWS, RATING_SLIDER, RATING_TABLE, \
    DEV_AVERAGE_RATING_LABEL, DENSITY_LAYOUT_STYLE, WHITE_STEAM, TAB_COLOR, TAB_EDGE, \
    TAB_HEADER_COLOR, DEVELOPER_DROPDOWN, DEV_TOP_GENRES_LABEL, DEV_CCU_LABEL, DEV_GAME_COUNT_LABEL, \
    DEV_REV_PER_GAME_LABEL, DEV_REVENUE_LABEL, DEV_TOP_GAMES, RATING_TABS, RATING_TABS_OUTPUT_AREA, \
    GENRE_PREDICTION_GRAPH, GENRE_DROPDOWN, DEFAULT_PLOT_STYLE_DICT, GAMES_BY_DEV_GRAPH, MARKET_PERFORMANCE_SCATTER, \
    MP_COMPANY_TYPE_DROPDOWN, create_market_scatter_plot_style, REVENUE_COMPANY_GAME_COUNT, PUB_REVENUE_LABEL, \
    PUB_TOP_GENRES_LABEL, PUB_CCU_LABEL, PUB_GAME_COUNT_LABEL, PUB_REV_PER_GAME_LABEL, PUB_TOP_GAMES, \
    PUB_AVERAGE_RATING_LABEL, PUBLISHER_DROPDOWN, GAMES_BY_PUB_GRAPH
from dash_plot_generation.utils import get_average_user_rating_label, get_game_count_label, get_top_revenue_game_labels, \
    get_total_revenue_label, get_top_genre_labels, get_ccu_label, get_average_game_rev_label
from visual_presentation.Annual_release_games import get_game_release_figure
from visual_presentation.Distribution_of_review_rating import get_rating_density_plot
from visual_presentation.Market_performance_function import plot_market_performance

APP = dash.Dash(
    name=__name__,
    use_pages=True,
    external_stylesheets=['/assets/styles.css',
                          'https://codepen.io/chriddyp/pen/bWLwgP.css']
)

APP.layout = html.Div([
    html.Nav(className="navbar", children=[
        html.A("SteamSavvy - Steam game data insights", href="/",
               style={"margin-left": "60px", "display": "inline-block"},
               className="nav-item-1"),
        html.A('About', className="nav-item nav-link btn", href='/about',
               style={"margin-left": "150px"}, ),
        html.A('Dashboard', className="nav-item nav-link btn", href='/dashboard',
               style={"margin-left": "150px"}),
        html.A('Technical report', className="nav-item nav-link active btn",
               href="", download='dark city.jpg', style={"margin-left": "150px"})
    ]),

    dash.page_container
], className="body")


def update_company_info(filtered_dataframe: pandas.DataFrame):
    # Top games
    company_top_games_label = get_top_revenue_game_labels(filtered_dataframe)

    # Dev total revenue
    company_revenue = get_total_revenue_label(filtered_dataframe)

    # Dev revenue per game
    company_game_revenue_per_game = get_average_game_rev_label(filtered_dataframe)

    # Top genres
    company_top_genre_labels = get_top_genre_labels(filtered_dataframe)

    # CCU
    company_ccu = get_ccu_label(filtered_dataframe)

    # Game count
    company_game_count = get_game_count_label(filtered_dataframe)

    user_rating_value = get_average_user_rating_label(filtered_dataframe)
    return company_revenue, company_top_genre_labels, company_ccu, company_game_count, company_game_revenue_per_game, \
        company_top_games_label, user_rating_value


@APP.callback([Output(DEV_REVENUE_LABEL, "children"),
               Output(DEV_TOP_GENRES_LABEL, "children"),
               Output(DEV_CCU_LABEL, "children"),
               Output(DEV_GAME_COUNT_LABEL, "children"),
               Output(DEV_REV_PER_GAME_LABEL, "children"),
               Output(DEV_TOP_GAMES, "children"),
               Output(DEV_AVERAGE_RATING_LABEL, "children")],
              inputs=[Input(DEVELOPER_DROPDOWN, "value")])
def update_dev_info(dev_name):
    if not (dev_name and isinstance(FULL_DATA, pandas.DataFrame)):
        raise PreventUpdate

    # Remove empty rows
    mask = FULL_DATA.developer.apply(lambda x: dev_name in x if isinstance(x, str) else False)
    dev_data = FULL_DATA[mask]

    return update_company_info(dev_data)


@APP.callback([Output(PUB_REVENUE_LABEL, "children"),
               Output(PUB_TOP_GENRES_LABEL, "children"),
               Output(PUB_CCU_LABEL, "children"),
               Output(PUB_GAME_COUNT_LABEL, "children"),
               Output(PUB_REV_PER_GAME_LABEL, "children"),
               Output(PUB_TOP_GAMES, "children"),
               Output(PUB_AVERAGE_RATING_LABEL, "children")],
              inputs=[Input(PUBLISHER_DROPDOWN, "value")])
def update_pub_info(pub_name):
    if not (pub_name and isinstance(FULL_DATA, pandas.DataFrame)):
        raise PreventUpdate
    # Remove empty rows
    mask = FULL_DATA.publisher.apply(lambda x: pub_name in x if isinstance(x, str) else False)
    pub_data = FULL_DATA[mask]

    return update_company_info(pub_data)


@APP.callback(Output(GAMES_BY_PUB_GRAPH, "figure"),
              Input(PUBLISHER_DROPDOWN, "value"))
def get_games_by_pub_table(pub_name):
    if not (pub_name and isinstance(FULL_DATA, pandas.DataFrame)):
        raise PreventUpdate

    layout_arguments = DEFAULT_PLOT_STYLE_DICT | dict(margin=dict(l=20, r=20, t=50, b=20))

    return get_game_release_figure(FULL_DATA, pub_name, "publisher", **layout_arguments)


@APP.callback(Output(GAMES_BY_DEV_GRAPH, "figure"),
              Input(DEVELOPER_DROPDOWN, "value"))
def get_games_by_dev_table(dev_name):
    if not (dev_name and isinstance(FULL_DATA, pandas.DataFrame)):
        raise PreventUpdate

    layout_arguments = DEFAULT_PLOT_STYLE_DICT | dict(margin=dict(l=20, r=20, t=50, b=20))

    return get_game_release_figure(FULL_DATA, dev_name, "developer", **layout_arguments)


@APP.callback(Output(RATING_TABS_OUTPUT_AREA, 'children'),
              Input(RATING_SLIDER, "value"),
              Input(RATING_MIN_REVIEWS, "value"),
              Input(RATING_TABS, "value"))
def update_density_filter_plot(rating_range, min_reviews, active_tab):
    allowed_indexes = [str_val for (val, str_val) in OWNER_RANGE_PARTS_SORTED[rating_range[0]:rating_range[1] + 1]]
    allowed_ratings = [" .. ".join([val, allowed_indexes[i + 1]]) for (i, val) in enumerate(allowed_indexes)
                       if i < len(allowed_indexes) - 1]
    data = get_rating_density_plot(FULL_DATA, allowed_ratings, min_reviews, layout=DENSITY_LAYOUT_STYLE)
    table_data_key = None
    output_table = False
    output = None
    match active_tab:
        case "free":
            table_data_key = "free"
            output_table = True
        case "plot":
            output = html.Div(dcc.Graph(figure=data['fig']))
        case "non-free":
            table_data_key = "non_free"
            output_table = True
        case _:
            raise KeyError("Invalid tab name")
    if output_table:
        output = html.Div(dash.dash_table.DataTable(data['top_games'][table_data_key].to_dict('records'),
                                                    id=RATING_TABLE,
                                                    style_data={'backgroundColor': TAB_COLOR,
                                                                'color': WHITE_STEAM,
                                                                'border': '1px solid ' + TAB_EDGE},
                                                    style_header={'backgroundColor': TAB_HEADER_COLOR,
                                                                  'color': WHITE_STEAM,
                                                                  'border': '1px solid ' + TAB_EDGE}))

    return [output]


@APP.callback(Output(GENRE_PREDICTION_GRAPH, "figure"),
              Input(GENRE_DROPDOWN, "value")
              )
def get_genre_prediction_table(genre, **kwargs):
    if "layout" not in kwargs.keys():
        kwargs["layout"] = DEFAULT_PLOT_STYLE_DICT | dict(
            title="Genre future prediction",
            margin=dict(l=20, r=20,
                        t=50, b=20)

        )
    fig = get_genre_plot(LABEL_ENCODED_DATASET, genre, **kwargs)
    return fig


@APP.callback(Output(MARKET_PERFORMANCE_SCATTER, "figure"),
              Input(MP_COMPANY_TYPE_DROPDOWN, "value"),
              Input(REVENUE_COMPANY_GAME_COUNT, "value"))
def get_market_performance_scatter(company_type, company_game_onwer_range):
    style = create_market_scatter_plot_style(company_type)
    return plot_market_performance(df=FULL_DATA, company_type=company_type, game_number_min=company_game_onwer_range[0],
                                   game_number_max=company_game_onwer_range[1], **style)


if __name__ == "__main__":
    initialize_data()
    APP.run_server(debug=True, host="0.0.0.0")
