import os

import pandas
import pandas as pd
import plotly as py
import plotly.figure_factory as ff
import plotly.graph_objects as go


def get_rating_density_plot(df: pd.DataFrame, owner_value_list, min_user_ratings: int = 0,
                            **layout_arguments):
    if min_user_ratings is None:
        min_user_ratings = 0

    filtered_user_rating_df = df.loc[(df.positive + df.negative >= min_user_ratings)]

    target_columns_free = ["name", "Review_rating", "developer", "publisher", "owners"]
    target_columns_non_free = target_columns_free + ["price"]
    renamed_target_columns_free = {"name": "Game", "Review_rating": "Rating", "developer": "Developer",
                                   "publisher": "Publisher", "owners": "Game owners"}
    renamed_target_columns_non_free = renamed_target_columns_free | {"price": "Price"}
    filtered_games_free = filtered_user_rating_df[
        (filtered_user_rating_df['owners'].isin(owner_value_list)) & (filtered_user_rating_df['price'] == 0) & (
                filtered_user_rating_df['Review_rating'] >= 0) & (filtered_user_rating_df['Review_rating'] <= 1)]
    filtered_games_free = filtered_games_free.sort_values(by='Review_rating', ascending=False)

    # Filter and sort Non-Free games by Review Rating
    filtered_games_non_free = filtered_user_rating_df[
        (filtered_user_rating_df['owners'].isin(owner_value_list)) & (filtered_user_rating_df['price'] != 0) & (
                filtered_user_rating_df['Review_rating'] >= 0) & (filtered_user_rating_df['Review_rating'] <= 1)]
    filtered_games_non_free = filtered_games_non_free.sort_values(by='Review_rating', ascending=False)

    # Top 10 non-free games by Review_rating
    top_10_non_free = filtered_games_non_free.head(10)[
        target_columns_non_free]
    top_10_non_free = top_10_non_free.rename(columns=renamed_target_columns_non_free)

    # Top 10 free games by Review_rating
    top_10_free = filtered_games_free.head(10)[target_columns_free]
    top_10_free = top_10_free.rename(columns=renamed_target_columns_free)

    # Make data more visually presentable

    # Round to 3
    top_10_free["Rating"] = top_10_free["Rating"].apply(lambda x: round(x, 3))
    top_10_non_free["Rating"] = top_10_non_free["Rating"].apply(lambda x: round(x, 3))

    # Add dollar sign to price
    top_10_non_free["Price"] = top_10_non_free["Price"].apply(lambda x: "".join(["$", str(x)]))

    # Add histogram data
    x1 = filtered_games_non_free['Review_rating']
    x2 = filtered_games_free['Review_rating']

    # Select only non-null rows
    val = {'free': {'data': x1, 'label': 'Free', 'color': '#FF5733', 'bin_size': .1},
           'non-free': {'data': x2, 'label': 'Non-free', 'color': '#33FF57', 'bin_size': .1}}

    valid_values = {key: value for (key, value) in val.items() if len(value['data']) >= 2}

    hist_data = [value['data'] for (key, value) in valid_values.items()]
    group_labels = [value['label'] for (key, value) in valid_values.items()]
    colors = [value['color'] for (key, value) in valid_values.items()]
    bin_size = [value['bin_size'] for (key, value) in valid_values.items()]

    if not valid_values:
        fig = go.Figure()
    else:
        fig = ff.create_distplot(hist_data, group_labels, bin_size=bin_size, histnorm="probability", show_hist=False,
                                 colors=colors)
    fig.update(**layout_arguments
    )
    return {'fig': fig, 'top_games': {'non_free': top_10_non_free, 'free': top_10_free}}


if __name__ == "__main__":
    path = os.path.normpath(
        os.getcwd() + os.sep + os.pardir + os.sep + "api_exploration" + os.sep + "full_game_data.csv")
    FULL_DATA = pd.read_csv(path)
    top_owners = FULL_DATA['owners'].unique()
    output = get_rating_density_plot(df=FULL_DATA, owner_value_list=top_owners, min_user_ratings=10)

    fig = output['fig']
    py.offline.iplot(fig)
