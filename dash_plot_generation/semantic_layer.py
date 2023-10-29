from time import time

import data_store as ds
from dash_plot_generation.styles_and_handles import GENRE_LIST_PATH, DEVELOPER_LIST_PATH, PUBLISHER_LIST_PATH, \
    FACTORIZED_GAME_DATAFRAME_PATH, OWNER_LIST_PATH, MAIN_DATAFRAME_PATH, GAME_POPULARITY_FILTERS_PATH, \
    OWNER_PREDICTIONS_PATH, OWNER_LINES_PATH, OPPORTUNITIES_PATH, AVERAGE_VALUE_PATH, INTERPOLATED_COLORS_PATH
from dash_plot_generation.utils import get_all_genres, load_genres, save_company_name_lists, save_genres_to_file, \
    save_label_encoded_data_to_file, save_owner_ranges_to_file, save_object_to_file, load_object_from_file, \
    save_game_popularity_filter_data_to_file


def save_everything_to_file():
    save_company_name_lists(ds.FULL_DATA,DEVELOPER_LIST_PATH, PUBLISHER_LIST_PATH)
    save_genres_to_file(ds.FULL_DATA,GENRE_LIST_PATH)
    save_label_encoded_data_to_file(FACTORIZED_GAME_DATAFRAME_PATH, OWNER_PREDICTIONS_PATH, OWNER_LINES_PATH,
                                    OPPORTUNITIES_PATH, AVERAGE_VALUE_PATH, INTERPOLATED_COLORS_PATH)
    save_owner_ranges_to_file(ds.FULL_DATA, OWNER_LIST_PATH)
    save_object_to_file(ds.FULL_DATA, MAIN_DATAFRAME_PATH)
    save_game_popularity_filter_data_to_file(ds.FULL_DATA, ds.OWNER_RANGE_PARTS_SORTED, GAME_POPULARITY_FILTERS_PATH)

if __name__ == "__main__":
    ds.initialize_data()
    save_everything_to_file()
    start_time = time()
    first_time = time()
    second_time = time()

    print(first_time-start_time)
    print(second_time-first_time)

    pass