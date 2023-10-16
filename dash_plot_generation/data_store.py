import os
import pandas

from dash_plot_generation.utils import convert_owners_to_limits, get_owner_means

csv_path = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "api_exploration")
split_csv_path = os.path.join(csv_path, "file_segments")


def initialize_data():
    global FULL_DATA, OWNER_RANGE_PARTS_SORTED
    dataframe = None
    for file in os.listdir(split_csv_path):
        file_path = os.path.join(split_csv_path, file)
        dataframe = pandas.concat([dataframe, pandas.read_csv(file_path)]) if dataframe is not None \
            else pandas.read_csv(file_path)

    add_game_revenues_and_owner_means(dataframe)
    owner_ranges = {value_range for value_range in dataframe["owners"].unique()}

    ranges_test = [(convert_owners_to_limits(value_range), value_range.split(" .. ")) for value_range in owner_ranges]
    unique_owner_values = {(limits[i], limits_str[i]) for (limits, limits_str)
                           in ranges_test for i in range(2)}
    sorted_owner_list = sorted(unique_owner_values, key=lambda range: range[0])

    OWNER_RANGE_PARTS_SORTED = sorted_owner_list
    FULL_DATA = dataframe
    return dataframe, sorted_owner_list


def add_game_revenues_and_owner_means(data):
    data["owner_means"] = data["owners"].apply(lambda x: get_owner_means(convert_owners_to_limits(x)))
    data["game_revenue"] = data.apply(lambda x: x["owner_means"] * x["price"] if
    not (pandas.isna(x["owner_means"]) or pandas.isna(x["price"]))
    else 0, axis=1)


FULL_DATA, OWNER_RANGE_PARTS_SORTED = initialize_data()
