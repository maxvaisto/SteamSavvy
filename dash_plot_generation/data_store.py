import os
import pandas
from time import time

from dash_plot_generation.styles_and_handles import FACTORIZED_GAME_DATAFRAME_PATH, OWNER_LIST_PATH
from dash_plot_generation.utils import convert_owners_to_limits, get_owner_means, setup_label_encoded_data, \
    load_label_encoded_data, load_owner_ranges_to_list

csv_path = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "api_exploration")
split_csv_path = os.path.join(csv_path, "file_segments")

FULL_DATA, OWNER_RANGE_PARTS_SORTED, LABEL_ENCODED_DATASET = None, None, None


def initialize_data():
    print("Initializing data")
    start_time = time()
    global FULL_DATA, OWNER_RANGE_PARTS_SORTED, LABEL_ENCODED_DATASET
    dataframe = setup_main_dataframe_full()

    # Create a label encoded dataframe
    genre_data = load_label_encoded_data(FACTORIZED_GAME_DATAFRAME_PATH)

    add_game_revenues_and_owner_means(dataframe)

    # Get sorted owner list
    sorted_owner_list = load_owner_ranges_to_list(OWNER_LIST_PATH)

    # Set global variables
    FULL_DATA, OWNER_RANGE_PARTS_SORTED, LABEL_ENCODED_DATASET = dataframe, sorted_owner_list, genre_data
    end_time = time()
    print("Initialization took", end_time-start_time, "seconds")


def setup_main_dataframe():
    dataframe = None
    for file in os.listdir(split_csv_path):
        file_path = os.path.join(split_csv_path, file)
        dataframe = pandas.concat([dataframe, pandas.read_csv(file_path)]) if dataframe is not None \
            else pandas.read_csv(file_path)
    return dataframe


def setup_main_dataframe_full():
    file_path = os.path.join(csv_path, "full_game_data.csv")
    dataframe = pandas.read_csv(file_path, index_col=0)
    return dataframe


def add_game_revenues_and_owner_means(data):
    data["owner_means"] = data["owners"].apply(lambda x: get_owner_means(convert_owners_to_limits(x)))
    data["game_revenue"] = data.apply(lambda x: x["owner_means"] * x["price"] if
    not (pandas.isna(x["owner_means"]) or pandas.isna(x["price"]))
    else 0, axis=1)
