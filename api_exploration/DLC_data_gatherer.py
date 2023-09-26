import os
from concurrent.futures import ThreadPoolExecutor

import numpy
import pandas

import pandas as pd

from main import get_steam_API_response, get_steamspy_API_response, STEAM_SPY_GAME_INFO, STEAM_API_LANGUAGE, \
    STEAM_GAME_INFO_URL, replace_owner_number_with_symbol


def get_dlc_data_steam(id):
    url = STEAM_GAME_INFO_URL + str(id) + STEAM_API_LANGUAGE
    response = get_steam_API_response(url, str(id))
    if not response:
        return pandas.Series({"appid": numpy.NaN, "name": numpy.NaN, "data_type": numpy.NaN, "price_eur": numpy.NaN,
                              "category": numpy.NaN, "main_publisher": numpy.NaN, "main_developer": numpy.NaN,
                              "release_date": numpy.NaN})
    data = response[str(id)]["data"]
    data_type = data["type"]
    name = data["name"]
    appid = data["steam_appid"]
    price_eur = data["price_overview"]["final"] if "price_overview" in data.keys() else ""
    category = [category["description"] for category in data["categories"]] if "categories" in data.keys() else []
    main_developer = data["developers"][0] if "developers" in data.keys() else ""
    main_publisher = data["publishers"][0] if "publishers" in data.keys() else ""
    release_date = data["release_date"]["date"] if "release_date" in data.keys() and "date" \
                                                   in data["release_date"].keys() else ""
    pass
    return pandas.Series({"appid": appid, "name": name, "data_type": data_type, "price_eur": price_eur,
                          "category": category, "main_publisher": main_publisher, "main_developer": main_developer,
                          "release_date": release_date})


def get_dlc_data_steamspy(id):
    url = STEAM_SPY_GAME_INFO + str(id)
    response = get_steamspy_API_response(url)
    if not response:
        return pandas.Series({"owners": numpy.NaN})
    owners = response["owners"]

    return pandas.Series({"owners": owners})


def get_dlc_data_for_list(dlc_list, num_threads=4):
    def get_combined_dlc_data(id):
        return get_dlc_data_steam(id).combine_first(get_dlc_data_steamspy(id))

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        combined_results = list(executor.map(get_combined_dlc_data, [id for id in dlc_list]))
    df = pandas.concat(combined_results, axis=1, ignore_index=True).T
    return df


def get_dlc_for_df(df, **kwargs):
    dlc_column = df["dlc"].to_list()
    dlc_list = []
    for val in dlc_column:
        if val and (isinstance(val, str) and len(val) > 2):
            entry_str = val[1:-1]
            entries = [int(entry) for entry in entry_str.split(", ")]
            dlc_list += entries

    return get_dlc_data_for_list(dlc_list, **kwargs)


# def get_dlc_for_files_in_dir(path):
#     files = os.listdir(path)
#     df = None
#     for file_name in files:
#         # new_df = pandas.read_csv(os.path.join(os.getcwd(), path, os))
#         df = pandas.concat([df, pandas.read_csv(os.path.join(os.getcwd(), path, file_name), index_col=0)], axis=0,
#                            ignore_index=True) if df is not None \
#             else pandas.read_csv(os.path.join(os.getcwd(), path, file_name), index_col=0)
#
#     print(files)
#     return df


if __name__ == "__main__":

    dlc_path = "dlc_segments"
    path = "file_segments"
    files = os.listdir(path)
    for i, file_name in enumerate(files):
        data = pandas.read_csv(os.path.join(os.getcwd(), path, file_name), index_col=0)
        # data = data.iloc[0:10] # for testing
        full_df = get_dlc_for_df(data)
        full_df = replace_owner_number_with_symbol(full_df)
        file_name = "".join(["dlc_data", "_", str(i), ".csv"])
        file_path = os.path.join(os.getcwd(), dlc_path, file_name)

        full_df.to_csv(file_path)
        print(f"Saved file {file_name}!")
    pass
