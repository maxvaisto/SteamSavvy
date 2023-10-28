import pandas
from time import time

from dash_plot_generation.styles_and_handles import FACTORIZED_GAME_DATAFRAME_PATH, OWNER_LIST_PATH, MAIN_DATAFRAME_PATH
from dash_plot_generation.utils import convert_owners_to_limits, get_owner_means, load_label_encoded_data, \
    load_owner_ranges_to_list, load_object_from_file

FULL_DATA, OWNER_RANGE_PARTS_SORTED, LABEL_ENCODED_DATASET = None, None, None


def initialize_data():
    print("Initializing data")
    start_time = time()
    global FULL_DATA, OWNER_RANGE_PARTS_SORTED, LABEL_ENCODED_DATASET
    dataframe = load_object_from_file(MAIN_DATAFRAME_PATH)

    # Create a label encoded dataframe
    genre_data = load_label_encoded_data(FACTORIZED_GAME_DATAFRAME_PATH)

    # Get sorted owner list
    sorted_owner_list = load_owner_ranges_to_list(OWNER_LIST_PATH)

    # Set global variables
    FULL_DATA, OWNER_RANGE_PARTS_SORTED, LABEL_ENCODED_DATASET = dataframe, sorted_owner_list, genre_data
    end_time = time()
    print("Initialization took", end_time - start_time, "seconds")


def add_game_revenues_and_owner_means(data):
    data["owner_means"] = data["owners"].apply(lambda x: get_owner_means(convert_owners_to_limits(x)))
    data["game_revenue"] = data.apply(lambda x: x["owner_means"] * x["price"] if
                                      not (pandas.isna(x["owner_means"]) or pandas.isna(x["price"])) else 0, axis=1)
