import dash
import numpy
import numpy as np
import pandas
from dash import html, dash, Output, Input, dcc
from dash.exceptions import PreventUpdate
import datetime as dt
import dash_plot_generation.data_store as ds

from visual_presentation.Annual_release_games import get_game_release_figure
from visual_presentation.Distribution_of_review_rating import get_rating_density_plot
from visual_presentation.Market_performance_function import plot_market_performance
from dash_plot_generation.utils import get_average_user_rating_label, get_game_count_label, get_top_revenue_game_labels, \
    get_total_revenue_label, get_top_genre_labels, get_ccu_label, get_average_game_rev_label, get_ccu_str, \
    get_top_revenue_game_names, convert_to_numeric_str, load_object_from_file
from Project_data_processor_ML import get_data_interval, get_genre_plot_full
from dash_plot_generation.styles_and_handles import RATING_MIN_REVIEWS, RATING_SLIDER, RATING_TABLE, \
    DEV_AVERAGE_RATING_LABEL, DENSITY_LAYOUT_STYLE, WHITE_STEAM, TAB_COLOR, TAB_EDGE, \
    TAB_HEADER_COLOR, DEVELOPER_DROPDOWN, DEV_TOP_GENRES_LABEL, DEV_CCU_LABEL, DEV_GAME_COUNT_LABEL, \
    DEV_REV_PER_GAME_LABEL, DEV_REVENUE_LABEL, DEV_TOP_GAMES, RATING_TABS, RATING_TABS_OUTPUT_AREA, \
    GENRE_PREDICTION_GRAPH, GENRE_DROPDOWN, DEFAULT_PLOT_STYLE_DICT, GAMES_BY_DEV_GRAPH, MARKET_PERFORMANCE_SCATTER, \
    MP_COMPANY_TYPE_DROPDOWN, create_market_scatter_plot_style, REVENUE_COMPANY_GAME_COUNT, PUB_REVENUE_LABEL, \
    PUB_TOP_GENRES_LABEL, PUB_CCU_LABEL, PUB_GAME_COUNT_LABEL, PUB_REV_PER_GAME_LABEL, PUB_TOP_GAMES, \
    PUB_AVERAGE_RATING_LABEL, PUBLISHER_DROPDOWN, GAMES_BY_PUB_GRAPH, TOP_COMPANY_TABLE_AREA, TOP_REVENUE_COMPANIES, \
    OWNER_PREDICTIONS_PATH, OWNER_LINES_PATH

ds.initialize_data()


app = dash.Dash(
    name=__name__,
    use_pages=True,
    external_stylesheets=['/assets/styles.css',
                          'https://codepen.io/chriddyp/pen/bWLwgP.css']
)

server = app.server
app.layout = html.Div([
    html.Nav(className="navbar", children=[
        html.A("SteamSavvy - Steam Game Data Insights", href="/",
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


@app.callback([Output(DEV_REVENUE_LABEL, "children"),
               Output(DEV_TOP_GENRES_LABEL, "children"),
               Output(DEV_CCU_LABEL, "children"),
               Output(DEV_GAME_COUNT_LABEL, "children"),
               Output(DEV_REV_PER_GAME_LABEL, "children"),
               Output(DEV_TOP_GAMES, "children"),
               Output(DEV_AVERAGE_RATING_LABEL, "children")],
              inputs=[Input(DEVELOPER_DROPDOWN, "value")])
def update_dev_info(dev_name):
    if not (dev_name and isinstance(ds.FULL_DATA, pandas.DataFrame)):
        raise PreventUpdate

    # Remove empty rows
    mask = ds.FULL_DATA.developer.apply(lambda x: dev_name in x if isinstance(x, str) else False)
    dev_data = ds.FULL_DATA[mask]

    return update_company_info(dev_data)


@app.callback([Output(PUB_REVENUE_LABEL, "children"),
               Output(PUB_TOP_GENRES_LABEL, "children"),
               Output(PUB_CCU_LABEL, "children"),
               Output(PUB_GAME_COUNT_LABEL, "children"),
               Output(PUB_REV_PER_GAME_LABEL, "children"),
               Output(PUB_TOP_GAMES, "children"),
               Output(PUB_AVERAGE_RATING_LABEL, "children")],
              inputs=[Input(PUBLISHER_DROPDOWN, "value")])
def update_pub_info(pub_name):
    if not (pub_name and isinstance(ds.FULL_DATA, pandas.DataFrame)):
        raise PreventUpdate
    # Remove empty rows
    mask = ds.FULL_DATA.publisher.apply(lambda x: pub_name in x if isinstance(x, str) else False)
    pub_data = ds.FULL_DATA[mask]

    return update_company_info(pub_data)


@app.callback(Output(GAMES_BY_PUB_GRAPH, "figure"),
              Input(PUBLISHER_DROPDOWN, "value"))
def get_games_by_pub_table(pub_name):
    if not (pub_name and isinstance(ds.FULL_DATA, pandas.DataFrame)):
        raise PreventUpdate

    layout_arguments = DEFAULT_PLOT_STYLE_DICT | dict(margin=dict(l=20, r=20, t=50, b=20))

    return get_game_release_figure(ds.FULL_DATA, pub_name, "publisher", **layout_arguments)


@app.callback(Output(GAMES_BY_DEV_GRAPH, "figure"),
              Input(DEVELOPER_DROPDOWN, "value"))
def get_games_by_dev_table(dev_name):
    if not (dev_name and isinstance(ds.FULL_DATA, pandas.DataFrame)):
        raise PreventUpdate

    layout_arguments = DEFAULT_PLOT_STYLE_DICT | dict(margin=dict(l=20, r=20, t=50, b=20))

    return get_game_release_figure(ds.FULL_DATA, dev_name, "developer", **layout_arguments)


@app.callback(Output(RATING_TABS_OUTPUT_AREA, 'children'),
              Input(RATING_SLIDER, "value"),
              Input(RATING_MIN_REVIEWS, "value"),
              Input(RATING_TABS, "value"))
def update_density_filter_plot(rating_range, min_reviews, active_tab):
    allowed_indexes = [str_val for (val, str_val) in ds.OWNER_RANGE_PARTS_SORTED[rating_range[0]:rating_range[1] + 1]]
    allowed_ratings = [" .. ".join([val, allowed_indexes[i + 1]]) for (i, val) in enumerate(allowed_indexes)
                       if i < len(allowed_indexes) - 1]
    data = get_rating_density_plot(ds.FULL_DATA, allowed_ratings, min_reviews, layout=DENSITY_LAYOUT_STYLE)
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


@app.callback(Output(GENRE_PREDICTION_GRAPH, "figure"),
              Input(GENRE_DROPDOWN, "value")
              )
def get_genre_prediction_table(genre, **kwargs):
    if "layout" not in kwargs.keys():
        kwargs["layout"] = DEFAULT_PLOT_STYLE_DICT | dict(
            title="Genre future prediction",
            margin=dict(l=20, r=20,
                        t=50, b=20)

        )
    dates = np.array(get_data_interval(730))
    dates = dates.reshape(len(dates), 1)
    owner_predictions = load_object_from_file(OWNER_PREDICTIONS_PATH)
    owner_lines = load_object_from_file(OWNER_LINES_PATH)
    vectorized_from_ordinal = np.vectorize(dt.datetime.fromordinal)
    dates = vectorized_from_ordinal(dates)
    fig = get_genre_plot_full(ds.LABEL_ENCODED_DATASET, genre, owner_predictions, owner_lines, dates, **kwargs)
    return fig


@app.callback(Output(MARKET_PERFORMANCE_SCATTER, "figure"),
              Input(MP_COMPANY_TYPE_DROPDOWN, "value"),
              Input(REVENUE_COMPANY_GAME_COUNT, "value"))
def get_market_performance_scatter(company_type, company_game_onwer_range):
    style = create_market_scatter_plot_style(company_type)
    return plot_market_performance(df=ds.FULL_DATA, company_type=company_type,
                                   game_number_min=company_game_onwer_range[0],
                                   game_number_max=company_game_onwer_range[1], **style)


def top_revenue_company_infromation_for_company(data, company_name):
    ccu_str = get_ccu_str(data)
    game_count_str = data.shape[0]
    top_games = get_top_revenue_game_names(data)
    total_revenue = "".join(["$", convert_to_numeric_str(int(numpy.nansum(data["game_revenue"])))])
    return {"Company": company_name, "Revenue": total_revenue, "Concurrent users": ccu_str,
            "Number of games": game_count_str, "Top games": top_games}


def get_company_information_for_company_list(company_list, company_type):
    company_information_list = []
    for company, value in company_list.iterrows():
        mask = ds.FULL_DATA[company_type].apply(lambda x: company in x if isinstance(x, str) else False)
        company_data = ds.FULL_DATA[mask]
        company_information = top_revenue_company_infromation_for_company(company_data, company)
        company_information_list.append(company_information)
    table_data = pandas.DataFrame(company_information_list)
    return table_data


@app.callback(Output(TOP_COMPANY_TABLE_AREA, 'children'),
              Input(TOP_REVENUE_COMPANIES, "value"))
def get_top_companies_table(company_type, get_largest_to=50):
    data = ds.FULL_DATA[[company_type, "game_revenue"]].groupby(company_type).sum()

    top_n_companies = data.nlargest(get_largest_to, 'game_revenue')

    data = get_company_information_for_company_list(top_n_companies, company_type)

    output = html.Div(dash.dash_table.DataTable(data.to_dict('records'),
                                                id=RATING_TABLE,
                                                style_data={'backgroundColor': TAB_COLOR,
                                                            'color': WHITE_STEAM,
                                                            'border': '1px solid ' + TAB_EDGE},
                                                style_header={'backgroundColor': TAB_HEADER_COLOR,
                                                              'color': WHITE_STEAM,
                                                              'border': '1px solid ' + TAB_EDGE}))

    return [output]


def start_server():
    app.run_server(debug=True, host="0.0.0.0")


if __name__ == "__main__":
    start_server()
