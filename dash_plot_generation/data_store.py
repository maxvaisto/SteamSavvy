import os
import pandas

from Project_data_processor_ML import label_encoding, genre_data_aggregation, clean_index, \
    replace_owner_str_with_average_number
from dash_plot_generation.utils import convert_owners_to_limits, get_owner_means

csv_path = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "api_exploration")
split_csv_path = os.path.join(csv_path, "file_segments")


def initialize_data():
    dataframe = None
    for file in os.listdir(split_csv_path):
        file_path = os.path.join(split_csv_path, file)
        dataframe = pandas.concat([dataframe, pandas.read_csv(file_path)]) if dataframe is not None \
            else pandas.read_csv(file_path)

    # Create a label encoded dataframe

    label_encoded_data = clean_index(dataframe.copy())
    label_encoding(label_encoded_data)
    replace_owner_str_with_average_number(label_encoded_data)
    genre_data = genre_data_aggregation(label_encoded_data, 2)

    add_game_revenues_and_owner_means(dataframe)

    # Get sorted owner list
    owner_ranges = {value_range for value_range in dataframe["owners"].unique()}

    ranges_test = [(convert_owners_to_limits(value_range), value_range.split(" .. ")) for value_range in owner_ranges]
    unique_owner_values = {(limits[i], limits_str[i]) for (limits, limits_str)
                           in ranges_test for i in range(2)}
    sorted_owner_list = sorted(unique_owner_values, key=lambda range: range[0])

    # Return values
    return dataframe, sorted_owner_list, genre_data


def add_game_revenues_and_owner_means(data):
    data["owner_means"] = data["owners"].apply(lambda x: get_owner_means(convert_owners_to_limits(x)))
    data["game_revenue"] = data.apply(lambda x: x["owner_means"] * x["price"] if
    not (pandas.isna(x["owner_means"]) or pandas.isna(x["price"]))
    else 0, axis=1)


FULL_DATA, OWNER_RANGE_PARTS_SORTED, LABEL_ENCODED_DATASET = initialize_data()
