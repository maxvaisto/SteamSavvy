import math
import re
from collections import Counter
from typing import Sequence, Optional, Any

import numpy
import pandas
from dash import html

from dash_plot_generation.styles_and_handles import SPACE_NORMAL_ENTRY

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
    if pandas.isna(arr):
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


def extract_unique_companies(nested_companies):
    full_company_list = [dev for company_list in nested_companies
                         if isinstance(company_list, list) for dev in company_list]
    unique_companies = []
    for company in full_company_list:
        if company not in unique_companies:
            unique_companies.append(company)
    return unique_companies


def replace_owner_number_with_symbol(df):
    def owner_strip(user_range: str):
        if isinstance(user_range, str):
            user_range = user_range.replace(",000,000", " M")
            user_range = user_range.replace(",000", " k")
        return user_range

    df["owners"] = df["owners"].apply(lambda name: owner_strip((name)))
    return df


def replace_owner_number_with_symbol_real_numeric(value):
    value_str = str(value)
    value_str = re.sub("0" * 9 + "$", " billion", value_str)
    value_str = re.sub("0" * 6 + "$", " million", value_str)
    # value_str = re.sub("0" * 3 + "$", " thousand", value_str)
    return value_str


def update_dots(n):
    num_dots = (n % 10) + 1
    dots = "." * num_dots
    return [dots]


def convert_to_numeric_str(value, **kwargs):
    return replace_owner_number_with_symbol_real_numeric(round_to_three_largest_digits(value, **kwargs))


def label_with_rev(label, rev, space, char=".", currency_symbol=""):
    processed_rev = convert_to_numeric_str(int(rev))
    return_val = label_with_text(label, "".join([currency_symbol, processed_rev]), space, char)
    return return_val


def label_with_text(first_str, second_str, space, char="."):
    white_space_filler = char * (space - (len(first_str) + len(second_str)) - 2)
    return_val = " ".join([first_str, white_space_filler, second_str])
    return return_val


def round_to_three_largest_digits(number, accuracy=2):
    round_val = -(len(str(round(number))) - accuracy)
    return_val = round(round(number), min(round_val, 0))
    return return_val


def get_average_user_rating_label(dev_data):
    value_str = str(round(100 * dev_data["Review_rating"].mean())) + "%"
    label = label_with_text("Average game rating", value_str, SPACE_NORMAL_ENTRY, ".")
    return label


def get_game_count_label(dev_data):
    return label_with_text("Number of games", str(dev_data.shape[0]), SPACE_NORMAL_ENTRY, ".")


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

def get_all_genres(df):
    unique_genres = set()
    try:
        for index, row in df.iterrows():
                if not isinstance(row.genres, str):
                    continue
                fully_split = row.genres.split(", ")
                unique_genres.update(fully_split)
    except Exception as ex:
        pass
    return unique_genres

