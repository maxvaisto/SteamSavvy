from typing import Sequence, Optional, Any
import pandas as pd
import plotly.express as px


# Three functions by Max, to get the mean value of game owner and split the company names.

DEFAULT_ILLEGAL_CONTINUATIONS = {"INC.", "LLC", "CO.", "LTD.", "S.R.O."}


def get_owner_means(owner_limits: Sequence[Any]):
    if not isinstance(owner_limits, list):
        return owner_limits
    else:
        return (owner_limits[0] + owner_limits[1]) / 2


def convert_owners_to_limits(owner_limit):
    if not isinstance(owner_limit, str):
        return owner_limit
    owners_raw = [rev.replace(" ", "") for rev in owner_limit.split(" .. ")]
    owners_clean = []
    for owner_limit in owners_raw:
        owner_limit = owner_limit.replace("M", "0" * 6)
        owner_limit = owner_limit.replace("k", "0" * 3)
        owners_clean.append(int(owner_limit))
    return owners_clean


def split_companies(arr, illegal_continuations: Optional[Sequence[str]] = None):
    """
    Splits the given string at comma sign as long as following the comma none of the illegal
    continuations happen. In such a case, the string split does not happen that said comma.
    :param arr: Array containing the developers/publishers for a single game
    :param illegal_continuations: A list of illegal continuations. Must be uppercase.
    :return: Returns the given split input string as a list.
    :note: If the arr is numpy.NaN, this value is returned instead of a list.
    """
    if illegal_continuations is None:
        illegal_continuations = DEFAULT_ILLEGAL_CONTINUATIONS
    if pd.isna(arr):
        return arr

    results_list = []
    start_index = 0
    split_char = ", "

    for index in range(len(arr)):
        if index < len(arr) - 1:
            txt = arr[index:index + 2]
            if txt == split_char:
                found_illegal = False
                min_continuation = min([len(continuation) for continuation in illegal_continuations])
                max_continuation = max([len(continuation) for continuation in illegal_continuations])
                next_chars = arr[index + min_continuation:index + min_continuation + max_continuation]
                for i in range(index + min_continuation, index + len(next_chars) + 2):
                    comp_txt = arr[index + 2:i + 2].upper()
                    if comp_txt in illegal_continuations:
                        found_illegal = True
                        break
                if not found_illegal:
                    results_list.append(arr[start_index:index].strip())
                    start_index = index + 1
        elif index == len(arr) - 1:
            results_list.append(arr[start_index:index + 1].strip())

    return results_list


# The function to plot the bubble chart of market performance

def plot_market_performance(df, company_type: str, game_number_max: int, game_number_min: int):
    
    """
    This function creates a bubble chart of market performance.
    The variable company_type could only be developer or publisher.
    The bubble size is game number, which is filtered by the range [game_number_min, game_number_max].
    """

    df["owner_means"] = df["owners"].apply(lambda x: get_owner_means(convert_owners_to_limits(x)))

    # Calulate the revenue
    df["revenue"] = df["owner_means"]*df["price"]

    # Split the companies
    df["company_split"] = df[company_type].apply(lambda x: split_companies(x))
    df_split = df.assign(developer=df['company_split'].str.split(', ')).explode('company_split')

    # Calculate revenue and game number
    company_stats = df_split.groupby('company_split').agg(revenue=('revenue', 'sum'), game_number=('company_split', 'count'), owner_number=('owner_means', 'sum')).reset_index()

    # Filter the Game number
    filter_company_stats = company_stats[(company_stats['game_number'] >= game_number_min) & (company_stats['game_number'] <= game_number_max)]

    # Bubble chart
    fig = px.scatter(filter_company_stats, x='revenue', y='owner_number', size='game_number', log_y=True, log_x=True,size_max = 40,
                 hover_name='company_split', title=f'Market Performance of {company_type}')

    return fig



if __name__ == "__main__":
    # Read data and calulate owner means
    df = pd.read_csv("full_game_data.csv")
    game_number_min = 1
    game_number_max = 10
    fig = plot_market_performance(df, 'developer', game_number_max, game_number_min)
    fig.show()










