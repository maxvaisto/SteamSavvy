import numpy
import pandas

import pandas as pd

from main import get_steam_API_response, get_steamspy_API_response, STEAM_SPY_GAME_INFO, STEAM_API_LANGUAGE, \
    STEAM_GAME_INFO_URL, replace_owner_number_with_symbol


def get_dlc_data_steam(id):
    url = STEAM_GAME_INFO_URL + str(id) + STEAM_API_LANGUAGE
    response = get_steam_API_response(url, str(id))
    if not response:
        return pandas.Series({"appid": numpy.NaN, "name": numpy.NaN, "data_type":numpy.NaN, "price_eur": numpy.NaN,
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
    return pandas.Series({"appid": appid, "name": name, "data_type":data_type, "price_eur": price_eur,
                          "category": category, "main_publisher": main_publisher, "main_developer": main_developer,
                          "release_date": release_date})



def get_dlc_data_steamspy(id):
    url = STEAM_SPY_GAME_INFO + str(id)
    response = get_steamspy_API_response(url)
    if not response:
        return pandas.Series({"owners": numpy.NaN})
    owners = response["owners"]

    return pandas.Series({"owners": owners})

def get_dlc_data_for_list(dlc_list):
    return pd.DataFrame([get_dlc_data_steam(id).combine_first(get_dlc_data_steamspy(id)) for id in dlc_list])


def get_dlc_for_df(df):
    dlc_column = df["dlc"].to_list()
    dlc_list = []
    for val in dlc_column:
        if val and (isinstance(val, str) and len(val) > 2):
            entry_str = val[1:-1]
            entries = [int(entry) for entry in entry_str.split(", ")]
            dlc_list += entries

    return get_dlc_data_for_list(dlc_list)
if __name__ == "__main__":
    data = pandas.read_csv("game_data_with_dlc.csv")
    full_df = get_dlc_for_df(data)
    full_df = replace_owner_number_with_symbol(full_df)
    full_df.to_csv("dlc_data.csv")
    pass