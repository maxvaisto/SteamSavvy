import datetime
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Union, List, Tuple

import requests
import json
import pandas
import time
import numpy
import matplotlib.pyplot as plt
from pandas.core.dtypes.common import is_numeric_dtype

from dash_plot_generation.utils import replace_owner_number_with_symbol_real_numeric

STEAMSPY_ALL_GAMES_URL = "https://steamspy.com/api.php?request=all&page="
STEAM_GAME_INFO_URL = "https://store.steampowered.com/api/appdetails?appids="
STEAM_API_LANGUAGE = "&l=english"
STEAM_SPY_GAME_INFO = "https://steamspy.com/api.php?request=appdetails&appid="


# There are 67 pages of data but for the heck of it,
# we're going try to load 100 pages
def get_all_data(iterations: Optional[Union[int, List[int]]] = 100, num_threads: int = 4,
                 capped: Optional[Union[int, Tuple[int]]] = None) -> pandas.DataFrame:
    """
    Retreives game data from steamspy and steam API.
    :param iterations: Contains the logic for choosing the page numbers for steamspy api of game pages to read. Each
    page contains 1000 games. The value can be an integer n which means that all pages from 0 to n-1 will be read. If
    the value is a list, only the indexes contained in that list will be read.
    :param num_threads: This value decides how many parallel threads are used for API queries. This can make the API
    query process faster.
    :param capped: This is for testing purposes. Either the value is an integer n in which case only the first n values
    of the (full) steamspy game list will be read and processed for further parsing. If it value is a tuple (a, b), the
    values will be read and further processed from a to b-1.
    :return: Returns a pandas dataframe containing game data.
    """
    def get_api_data_for_game_threaded(game_id):
        steam_api_data = get_additional_game_data_steam(str(game_id))
        steamspy_api_data = get_additional_game_data_steamspy(str(game_id))
        return steam_api_data, steamspy_api_data

    iteration_list = iterations if isinstance(iterations, list) else range(iterations)
    game_dataframe = None
    for index in iteration_list:
        print(f"Loading the game list page: {str(index)}")
        url = STEAMSPY_ALL_GAMES_URL + str(index)
        try:
            response = json.loads(requests.get(url).text)
        except Exception as some_shit:
            print(some_shit)
            break
        games = [value for (key, value) in response.items()]
        game_dataframe = pandas.DataFrame(games) if not game_dataframe \
            else pandas.concat([game_dataframe, pandas.DataFrame(games)], ignore_index=True, sort=False)

    if capped:
        if isinstance(capped, list):
            game_dataframe = game_dataframe.loc[capped[0]:capped[1]]
        elif isinstance(capped, int):
            game_dataframe = game_dataframe.iloc[0:capped]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        combined_results = list(executor.map(get_api_data_for_game_threaded, game_dataframe["appid"]))

    steam_results = [result[0] for result in combined_results]
    steamspy_results = [result[1] for result in combined_results]

    game_dataframe = pandas.concat([game_dataframe,
                                    pandas.DataFrame(steam_results),
                                    pandas.DataFrame(steamspy_results)], axis=1)

    return game_dataframe


def get_steam_API_response(url, game_id: str):
    fails = 0
    base_wait = 60
    response = None
    json_load_error = False
    try:
        payload = requests.get(url)
        response = json.loads(payload.text)
    except Exception as ex:
        print("Error occurred while parsing json from Steam:", ex)
        json_load_error = True
    print(datetime.datetime.now())

    while (not response or response[game_id]["success"] is False) or json_load_error:
        # This part is meant to catch errors in the loading process
        if (response and response[game_id]["success"] is False) or json_load_error:
            fails += 1
            json_load_error = False
            if fails >= 10:
                return None
        else:
            print("Failed queries for", game_id, "is", fails)
            time.sleep(base_wait)
            try:
                response = json.loads(requests.get(url).text)
            except Exception as ex:
                print("Error occurred while parsing json from Steam:", ex)
                json_load_error = True
    return response


def get_steamspy_API_response(url):
    response = None
    fails = 0
    while not response:
        try:
            response = json.loads(requests.get(url).text)
            return response
        except Exception as ex:
            print("Error occurred while parsing json from Steam:", ex)
            fails += 1
            if fails >= 10:
                return None


def get_additional_game_data_steam(game_id):
    url = STEAM_GAME_INFO_URL + game_id + STEAM_API_LANGUAGE
    response = get_steam_API_response(url, str(game_id))
    if not response:
        return pandas.Series({"platforms": numpy.NaN, "release_date": numpy.NaN, "categories": numpy.NaN,
                              "dlc": numpy.NaN})

    data = response[game_id]["data"]
    if data["type"] != "game":
        print("Non game found", data["name"])
    platforms = [platform for (platform, enabled) in data["platforms"].items() if enabled]
    release_date = data["release_date"]["date"]
    categories = [category_data["description"] for category_data in
                  data["categories"]] if "categories" in data.keys() else []
    dlc = [dlc for dlc in data["dlc"]] if "dlc" in data.keys() else []
    return_values = pandas.Series({"platforms": platforms, "release_date": release_date, "categories": categories,
                                   "dlc": dlc})
    return return_values


def get_additional_game_data_steamspy(game_id):
    url = STEAM_SPY_GAME_INFO + game_id
    response = get_steamspy_API_response(url)
    if not response:
        return pandas.Series({"ccu": numpy.NaN, 'languages': numpy.NaN, 'genres': numpy.NaN, "tags": numpy.NaN})

    languages = response["languages"].split(", ") if response["languages"] else []
    genres = response["genre"]
    ccu = response["ccu"]
    tags = [tag for (tag, tag_id) in response["tags"].items()] if response["tags"] else []

    return_values = pandas.Series({"ccu": ccu, "languages": languages, "genres": genres, "tags": tags})
    return return_values


def add_user_rating(df):
    def user_rating_function(pos, neg):
        if pos == neg == 0:
            return 0
        return pos / (pos + neg)

    df["Review_rating"] = df.apply(lambda row: user_rating_function(row.positive, row.negative), axis=1)
    return df


def price_to_dollars(convert_df):

    convert_df["price"] = convert_df["price"].apply(lambda val: int(val) / 100 if (val and int(val) != 0) else 0)
    return convert_df


def create_hist_plots(df):
    for col_name in df.columns:
        if is_numeric_dtype(df[col_name]):
            fig = plt.figure()
            plt.hist(df[col_name], log=True)
            title = " ".join([col_name, "log histogram"])
            plt.title(title)
            fig.savefig("".join(["images\\", title, ".png"]))
            plt.show()


def create_heat_maps(df, plot_pairs):
    for (x, y) in plot_pairs:
        plt.figure()  # Create a new figure for each heatmap
        heatmap = plt.imshow(df[[x, y]].values, cmap='hot', interpolation='nearest', aspect='auto')
        plt.colorbar(heatmap)  # Add a color bar
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"Heatmap of {x} vs {y}")
        plt.show()


def plot_statistics_data(df):
    create_hist_plots(df)

    # Create owners histogram
    plt.hist(df["owners"], log=True)
    plt.xticks(rotation='vertical')
    plt.title("Histogram of game playerbase sizes with log scale")
    plt.tight_layout()
    plt.show()


def combine_and_save_dataframes_in_dir(path, output_file_name):
    files = os.listdir(path)
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    df = None
    for file_name in files:
        df = pandas.concat([df, pandas.read_csv(os.path.join(os.getcwd(), path, file_name), index_col=0)], axis=0,
                           ignore_index=True) if df is not None \
            else pandas.read_csv(os.path.join(os.getcwd(), path, file_name), index_col=0)
    df.to_csv(output_file_name + ".csv")
    df.to_json(output_file_name + ".json")

if __name__ == "__main__":

    path = "file_segments"

    for i in range(0, 68):
        df = get_all_data(iterations=[i])
        df = add_user_rating(df)
        df = replace_owner_number_with_symbol_real_numeric(df)
        df = price_to_dollars(df)
        file_name = "".join(["game_data", "_", str(i), ".csv"])
        file_path = os.path.join(os.getcwd(), path, file_name)

        df.to_csv(file_path)
        print(f"Saved file {file_name}!")

    # plot_statistics_data(df)
    pass
