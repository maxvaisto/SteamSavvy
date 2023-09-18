import itertools
import datetime
from concurrent.futures import ThreadPoolExecutor

import requests
import json
import pandas
import time
import matplotlib.pyplot as plt
from pandas.core.dtypes.common import is_numeric_dtype

STEAMSPY_ALL_GAMES_URL = "https://steamspy.com/api.php?request=all&page="
STEAM_GAME_INFO_URL = "https://store.steampowered.com/api/appdetails?appids="
STEAM_API_LANGUAGE = "&l=english"
STEAM_SPY_GAME_INFO = "https://steamspy.com/api.php?request=appdetails&appid="


# There are 67 pages of data but for the heck of it,
# we're going try to load 100 pages
def get_all_data(iterations: int = 100, num_threads: int = 4):
    def get_api_data_for_game_threaded(id):
        steam_api_data = get_additional_game_data_steam(str(id))
        steamspy_api_data = get_additional_game_data_steamspy(str(id))
        return steam_api_data, steamspy_api_data
    # def get_additional_game_data_steam_threaded(id):
    #     return get_additional_game_data_steam(str(id))
    # def get_additional_game_data_steamspy_threaded(id):
    #     return get_additional_game_data_steamspy(str(id))
    for i in range(iterations):
        print(i)
        url = STEAMSPY_ALL_GAMES_URL + str(i)
        try:
            response = json.loads(requests.get(url).text)
        except Exception as some_shit:
            print(some_shit)
            break
        games = [value for (key, value) in response.items()]
        if i == 0:
            df = pandas.DataFrame(games)
        else:
            df = pandas.concat([df, pandas.DataFrame(games)], ignore_index=True, sort=False)

    # df = df.iloc[0:10]
    # with ThreadPoolExecutor(max_workers=num_threads) as executor:
    #     steam_results = list(executor.map(get_additional_game_data_steam_threaded, df["appid"]))
    #
    # with ThreadPoolExecutor(max_workers=num_threads) as executor:
    #     steamspy_results = list(executor.map(get_additional_game_data_steamspy_threaded, df["appid"]))
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        combined_results = list(executor.map(get_api_data_for_game_threaded, df["appid"]))

    steam_results = [result[0] for result in combined_results]
    steamspy_results = [result[1] for result in combined_results]

    df = pandas.concat([df, pandas.DataFrame(steam_results), pandas.DataFrame(steamspy_results)], axis=1)

    # steam_api_data = df["appid"].iloc[:].apply(lambda x: get_additional_game_data_steam(str(x)))
    # df = pandas.concat([df, steam_api_data], axis=1)
    return df


def get_additional_game_data_steam(id):
    url = STEAM_GAME_INFO_URL + id + STEAM_API_LANGUAGE

    response = json.loads(requests.get(url).text)
    print(datetime.datetime.now())
    fails = 0
    base_wait = 60
    while not response or response[id]["success"] == False:
        # This part is meant to catch
        if response and response[id]["success"] == False:
            fails += 1
            if fails >= 10:
                return pandas.Series({'platforms': [], 'release_date': "", 'categories': []})
        print("Failed queries for", id, "is", fails)
        time.sleep(base_wait)
        response = json.loads(requests.get(url).text)


    data = response[id]["data"]
    if data["type"] != "game":
        print("Non game found", data["name"])
    platforms = [platform for (platform, enabled) in data["platforms"].items() if enabled]
    release_date = data["release_date"]["date"]
    categories = [category_data["description"] for category_data in data["categories"]] if "categories" in data.keys() else []
    return_values = pandas.Series({'platforms': platforms, 'release_date': release_date, 'categories': categories})
    return return_values


def get_additional_game_data_steamspy(id):
    url = STEAM_SPY_GAME_INFO + id
    response = json.loads(requests.get(url).text)
    # tags = [tag for (tag,tag_id) in response["tags"]]
    languages = response["languages"].split(", ")
    genres = response["genre"]
    ccu = response["ccu"]
    tags = [tag for (tag, tag_id) in response["tags"].items()] if response["tags"] else []

    return_values = dict(ccu=ccu, languages=languages, genres=genres, tags=tags)
    return return_values


def add_user_rating(df):
    def user_rating_function(pos, neg):
        if pos == neg == 0:
            return 0
        return pos / (pos + neg)

    df["Review_rating"] = df.apply(lambda row: user_rating_function(row.positive, row.negative), axis=1)
    return df


def create_hist_plots(df):
    for col_name in df.columns:
        if is_numeric_dtype(df[col_name]):
            fig = plt.figure()
            plt.hist(df[col_name], log=True)
            title = " ".join([col_name, "log histogram"])
            plt.title(title)
            fig.savefig("".join(["images\\", title, ".png"]))
            plt.show()


def replace_owner_number_with_symbol(df):
    def owner_strip(user_range: str):
        user_range = user_range.replace(",000,000", " M")
        user_range = user_range.replace(",000", " k")
        return user_range

    df["owners"] = df["owners"].apply(lambda name: owner_strip((name)))
    return df


def create_heat_maps(df, plot_pairs):
    for (x, y) in plot_pairs:
        plt.figure()  # Create a new figure for each heatmap
        heatmap = plt.imshow(df[[x, y]].values, cmap='hot', interpolation='nearest', aspect='auto')
        plt.colorbar(heatmap)  # Add a colorbar
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"Heatmap of {x} vs {y}")
        plt.show()


def price_to_dollars(convert_df):
    convert_df["price"] = convert_df["price"].apply(lambda val: int(val) / 100 if int(val) != 0 else 0)
    return convert_df


if __name__ == "__main__":
    df = get_all_data()
    df = add_user_rating(df)
    df = replace_owner_number_with_symbol(df)
    df = price_to_dollars(df)
    df.to_csv("game_data_experimental.csv")
    h = df.describe()
    j = df.isna().sum()
    c = df["userscore"].value_counts()

    numeric_cols = [col for col in df.columns if is_numeric_dtype(df[col])]
    plot_pairs = list(itertools.combinations(numeric_cols, 2))
    print(df.columns)
    print("price", df["price"].unique())
    print("discount", df["discount"].unique())
    print("owners", df["owners"].unique())
    create_hist_plots(df)
    plt.hist(df["owners"], log=True)
    plt.xticks(rotation='vertical')
    plt.title("Histogram of game playerbase sizes with log scale")
    plt.tight_layout()
    plt.show()
    df.to_csv("game_data_full.csv")
    pass
