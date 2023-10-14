import os

import pandas
import pandas as pd
import plotly as py
import plotly.figure_factory as ff


def get_rating_density_plot(df: pd.DataFrame, owner_value_list, min_user_ratings: int = 0):

    filtered_user_rating_df = df.loc[(df.positive + df.negative >= min_user_ratings)]

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
    top_10_non_free = filtered_games_non_free.sort_values(by='Review_rating', ascending=False).head(10)

    # Top 10 free games by Review_rating
    top_10_free = filtered_games_free.sort_values(by='Review_rating', ascending=False).head(10)

    # Add histogram data
    x1 = filtered_games_non_free['Review_rating']
    x2 = filtered_games_free['Review_rating']

    # Group data together
    hist_data = [x1, x2]
    group_labels = ['Non-free', 'Free']

    fig = ff.create_distplot(hist_data, group_labels, bin_size=[.1, .1], histnorm="probability", show_hist=False,
                             )
    fig.update(layout=dict(
        title='Distribution of Game Review Rating',
        template="plotly_dark",
        plot_bgcolor="rgb(31,46,65)",
        paper_bgcolor="rgb(31,46,65)",
        xaxis_title="User rating",
        yaxis_title="Proportion"

    ))
    return {'fig': fig, 'top_games': {'non_free': top_10_non_free, 'free': top_10_free}}


if __name__ == "__main__":
    path = os.path.normpath(
        os.getcwd() + os.sep + os.pardir + os.sep + "api_exploration" + os.sep + "full_game_data.csv")
    FULL_DATA = pd.read_csv(path)
    top_owners = FULL_DATA['owners'].unique()
    output = get_rating_density_plot(df=FULL_DATA, owner_value_list=top_owners, min_user_ratings=10)

    fig = output['fig']
    py.offline.iplot(fig)
