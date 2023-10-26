from time import time

import data_store as ds
from dash_plot_generation.styles_and_handles import GENRE_LIST_PATH, DEVELOPER_LIST_PATH, PUBLISHER_LIST_PATH, \
    FACTORIZED_GAME_DATAFRAME_PATH, OWNER_LIST_PATH
from dash_plot_generation.utils import get_all_genres, load_genres, save_company_name_lists, save_genres_to_file, \
    save_label_encoded_data_to_file, save_owner_ranges_to_file


def save_everything_to_file():
    save_company_name_lists(ds.FULL_DATA,DEVELOPER_LIST_PATH, PUBLISHER_LIST_PATH)
    save_genres_to_file(ds.FULL_DATA,GENRE_LIST_PATH)
    save_label_encoded_data_to_file(ds.FULL_DATA, FACTORIZED_GAME_DATAFRAME_PATH)
    save_owner_ranges_to_file(ds.FULL_DATA, OWNER_LIST_PATH)


if __name__ == "__main__":
    ds.initialize_data()
    save_everything_to_file()

    pass