import pickle
import re
from collections import Counter
from typing import Sequence, Optional, Any

import numpy
import numpy as np
import pandas
from dash import html

from Project_data_processor_ML import clean_index, label_encoding, replace_owner_str_with_average_number, \
    genre_data_aggregation
from dash_plot_generation.styles_and_handles import SPACE_NORMAL_ENTRY, WHITE_STEAM

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
    flat_array = np.array(
        [company for company_list in nested_companies if isinstance(company_list, list) for company in company_list])
    _, idx = np.unique(flat_array, return_index=True)
    unique_companies = flat_array[np.sort(idx)]
    return unique_companies.tolist()


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
    return value_str


def update_dots(n):
    num_dots = (n % 10) + 1
    dots = "." * num_dots
    return [dots]


def convert_to_numeric_str(value, **kwargs):
    return replace_owner_number_with_symbol_real_numeric(round_to_three_largest_digits(value, **kwargs))


def label_with_rev(label, rev, space, char=".", currency_symbol=""):
    processed_rev = convert_to_numeric_str(int(rev)) if not numpy.isnan(rev) else "0"
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


def get_average_user_rating_label(company_data: pandas.DataFrame, space_amount: int = SPACE_NORMAL_ENTRY):
    value_str = str(round(100 * company_data["Review_rating"].mean())) + "%"
    label = label_with_text("Average game rating", value_str, space_amount, ".")
    return label


def get_game_count_label(company_data: pandas.DataFrame, space_amount: int = SPACE_NORMAL_ENTRY):
    return label_with_text("Number of games", str(company_data.shape[0]), space_amount, ".")


def get_top_revenue_game_labels(data):
    top_games = data.sort_values(by=["game_revenue"], ascending=False).head(3)
    top_games_processed = top_games.apply(lambda x: label_with_rev(x["name"], x["game_revenue"], SPACE_NORMAL_ENTRY,
                                                                   ".", "$"), axis=1)
    dev_top_games_with_dot = [" ".join(["•", game]) for game in top_games_processed]
    dev_top_games_label = html.Div("\n".join(dev_top_games_with_dot),
                                   style={'white-space': 'pre-line', 'padding-left': '5%'})
    return dev_top_games_label


def get_top_revenue_game_names(data):
    top_games = data.sort_values(by=["game_revenue"], ascending=False).head(3)
    top_games_processed = top_games.apply(lambda x: label_with_rev(x["name"], x["game_revenue"], SPACE_NORMAL_ENTRY,
                                                                   ".", "$"), axis=1)
    dev_top_games_with_dot = [" ".join(["•", game]) for game in top_games_processed]
    dev_top_games_label = "\n".join(dev_top_games_with_dot)
    return dev_top_games_label


def get_total_revenue_label(data, space_amount: int = SPACE_NORMAL_ENTRY, add_point: bool = True):
    starting_text = "• Total" if add_point else "Total"
    top_games_processed = label_with_rev(starting_text, numpy.nansum(data["game_revenue"]),
                                         space_amount, ".", "$")
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


def get_ccu_label(data, space_amount: int = SPACE_NORMAL_ENTRY):
    dev_ccu = get_ccu_str(data)
    return label_with_text("Concurrent users", dev_ccu, space_amount, ".")


def get_ccu_str(data):
    ccu = sum(data["ccu"])
    return convert_to_numeric_str(ccu)


def get_genre_popularity_counts(df, group_after_largest=8):
    genre_df = df[["genres", "owner_means", "game_revenue"]]

    genre_df = genre_df.dropna(subset=["genres"])
    genre_df["genres"] = genre_df["genres"].str.split(", ")

    # Give the genres a separate rwo for each genre
    genre_df = genre_df.explode("genres")
    grouped = genre_df.groupby("genres").agg({"owner_means": "sum", "game_revenue": "sum"})

    # Get top values in dfs
    top_owners = grouped.sort_values(by="owner_means", ascending=False).head(group_after_largest)
    top_revenue = grouped.sort_values(by="game_revenue", ascending=False).head(group_after_largest)

    # Sum the values of the remaining genres
    other_owners = grouped.loc[~grouped.index.isin(top_owners.index)].sum()
    other_revenue = grouped.loc[~grouped.index.isin(top_revenue.index)].sum()

    # Add the rest into same column
    top_owners.loc["Other"] = other_owners
    top_revenue.loc["Other"] = other_revenue

    return top_owners["owner_means"].to_dict(), top_revenue["game_revenue"].to_dict()


def get_average_game_rev_label(data, space_amount: int = SPACE_NORMAL_ENTRY, add_point: bool = True):
    game_revenue = data["game_revenue"]

    # Check if the game_revenue list contains only NaN values
    if all(numpy.isnan(game_revenue)):
        game_revenue = [0.0] * len(game_revenue)  # Replace all NaN values with zeros

    # Calculate the average
    game_revenue_per_game_raw = numpy.nanmean(game_revenue)
    dev_game_revenue_per_game_row = label_with_rev("Average", game_revenue_per_game_raw, space_amount, ".", "$")

    dev_game_revenue_per_game = " ".join(["•", dev_game_revenue_per_game_row]) if add_point \
        else dev_game_revenue_per_game_row

    return dev_game_revenue_per_game


def get_all_genres(df):
    genres_column = df['genres'].dropna().values
    unique_genres = set(np.concatenate([genres.split(", ") for genres in genres_column]))
    return unique_genres


def get_cumulative_owner_game_count_limits_for_dev_and_pub(df):
    owner_cum_sums_dev = df[["developer"]].value_counts()
    min_owner_dev = 1
    max_owner_dev = owner_cum_sums_dev.iloc[0]
    owner_cum_sums_pub = df[["publisher"]].value_counts()
    min_owner_pub = 1
    max_owner_pub = owner_cum_sums_pub.iloc[0]
    return {"developer": {"min": min_owner_dev, "max": max_owner_dev},
            "publisher": {"min": min_owner_pub, "max": max_owner_pub}}


def save_owner_ranges_to_file(dataframe, filepath):
    # Get sorted owner list
    owner_ranges = {value_range for value_range in dataframe["owners"].unique()}

    ranges_test = [(convert_owners_to_limits(value_range), value_range.split(" .. ")) for value_range in owner_ranges]
    unique_owner_values = {(limits[i], limits_str[i]) for (limits, limits_str)
                           in ranges_test for i in range(2)}
    sorted_owner_list = sorted(unique_owner_values, key=lambda range: range[0])

    save_object_to_file(sorted_owner_list, filepath)


def load_owner_ranges_to_list(filepath):
    return load_object_from_file(filepath)


def save_label_encoded_data_to_file(dataframe, filepath):
    data, _ = setup_label_encoded_data(dataframe)
    save_object_to_file(data, filepath)


def load_label_encoded_data(filepath):
    return load_object_from_file(filepath)


def setup_label_encoded_data(data: pandas.DataFrame):
    data_copy = data.copy()
    full_data_df = clean_index(data_copy)
    label_encoding(full_data_df)
    full_data_df = replace_owner_str_with_average_number(full_data_df)
    owners_genre_data, number_genre_data = genre_data_aggregation(full_data_df, 2)
    return owners_genre_data, number_genre_data


def save_genres_to_file(dataframe, filepath):
    # Get unique_genres
    unique_genres = get_all_genres(dataframe)
    save_object_to_file(unique_genres, filepath)


def load_genres(filepath):
    return load_object_from_file(filepath)


def save_company_name_lists(dataframe, file_name_dev, file_name_pub, add_labels=False):
    unique_publishers = extract_unique_companies(dataframe["publisher"].apply(lambda x: split_companies(x)))
    unique_developers = extract_unique_companies(dataframe["developer"].apply(lambda x: split_companies(x)))
    if add_labels:
        developer_labels = [{"label": html.Span([developer], style={'color': WHITE_STEAM}),
                             "value": developer} for developer in unique_developers]
        publisher_labels = [{"label": html.Span([publisher], style={'color': WHITE_STEAM}),
                             "value": publisher} for publisher in
                            unique_publishers]
        save_object_to_file(developer_labels, file_name_dev + "_labels")
        save_object_to_file(publisher_labels, file_name_pub + "_labels")

    save_object_to_file(unique_publishers, file_name_pub)
    save_object_to_file(unique_developers, file_name_dev)


def load_company_names(file_name_dev, file_name_pub):
    return load_object_from_file(file_name_dev), load_object_from_file(file_name_pub)


def load_company_name_labels(file_name_dev, file_name_pub):
    return load_object_from_file(file_name_dev), load_object_from_file(file_name_pub)


def save_object_to_file(object, file_path):
    with open(file_path, "wb") as fp:
        pickle.dump(object, fp)


def load_object_from_file(file_path):
    with open(file_path, "rb") as fp:
        object = pickle.load(fp)
    return object


def save_game_popularity_filter_data_to_file(dataframe, owner_range_parts, filepath):
    # Calculate max_reviews
    max_reviews = np.nanmax(dataframe.apply(lambda x: x["positive"] + x["negative"], axis=1))
    # Calculate owner_range_dict
    owner_range_dict = {index: val_str for (index, (val, val_str)) in enumerate(owner_range_parts)}
    min_owner = min(owner_range_dict.keys())
    max_owner = max(owner_range_dict.keys())

    # Create a dictionary to store the calculated values
    data_to_save = {
        "max_reviews": max_reviews,
        "owner_range_dict": owner_range_dict,
        "min_owner": min_owner,
        "max_owner": max_owner
    }
    save_object_to_file(data_to_save, filepath)
