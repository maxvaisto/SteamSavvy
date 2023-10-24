from dash import dash

import dash_plot_generation.data_store as ds

ds.initialize_data()

from dash_plot_generation.app import start_server


if __name__ == "__main__":

    start_server()