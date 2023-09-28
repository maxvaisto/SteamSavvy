import os

import pandas
from dash import dash, dcc, html, ctx, callback
csv_path = os.path.normpath(os.getcwd() + os.sep + os.pardir + os.sep + "api_exploration")
split_csv_path = os.path.join(csv_path, "file_segments")

df = None
APP = None
DASH_ASSETS_PATH = "dash_assets"
def initialize_data():
    global df
    files = os.listdir(split_csv_path)
    dataframe = None
    for file in os.listdir(split_csv_path):
        file_path = os.path.join(split_csv_path, file)
        dataframe = pandas.concat([dataframe, pandas.read_csv(file_path)]) if dataframe is not None \
        else pandas.read_csv(file_path)
    df = dataframe


def initialize_dash(host: str = "0.0.0.0", **kwargs):
    """
    Runs the Dash server.
    Args:
        host: IP address of the server
        kwargs: Variables which are passed down to APP.run function as named arguments.
    Note:
        The server IP is not actually 0.0.0.0; if the dash app is not accessible via this address, use the same port
        number but replace the IP address with your local network IP instead.
    """

    global APP, df

    unique_developers = [dev for dev_list in df["developer"].fillna("Valve").unique() for dev in dev_list.split(",")]
    unique_publishers = df["developer"].fillna("Valve").unique()

    # This is ok but the results are still unsatisfactory due to the game company names containing a comma
    # unique_publishers = [publisher for publisher_list in df["developer"].fillna("Valve").unique() for publisher
    # unique_developers = [dev for dev_list in df["developer"].fillna("Valve").unique() for dev in dev_list.split(",")]

    APP = dash.Dash(
        name=__name__,
        assets_folder=DASH_ASSETS_PATH,
        external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
    )
    APP.layout = html.Div(children=[
        html.Nav(className="nav nav-pills", children=[
            html.H6("STEAM-SAVVY", style={"margin-left": "30px", "width": "20%", "display": "inline-block"}),
            html.A('About', className="nav-item nav-link btn", href='/apps/App1',
                   style={"margin-left": "300px"}),
            html.A('Process paper', className="nav-item nav-link active btn", href='/apps/App2',
                   style={"margin-left": "150px"})
        ],
         style={"background-color": "rgb(30,30,30)", "color": "rgb(255,255,255)"}),

        html.H6("TEXT"),
        html.Div(className="row", children=[
            html.Div(children = [
            dcc.Tabs(id="tabs_main_plots1", value="tab1", children=[
                dcc.Tab(label="Genre performance", value="tab1"),
                dcc.Tab(label="Game popularity", value="tab2"),
                dcc.Tab(label="Company revenues", value="tab3"),
                dcc.Tab(label="Market performance", value="tab4"),
            ],
            style={'width': '80%', 'display': 'inline-block', "outline": "2px dotted black"}),
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div(children=[
            dcc.Tabs(id="tabs_main_plots2", value="tab3", children=[
                dcc.Tab(label="Developer infromation", value="Valve", children=[
                    dcc.Dropdown(id="developer_dropdown",
                                 options=[{"label": developer, "value": developer} for developer in unique_developers]
                                 )
                ]),
                dcc.Tab(label="Publisher information", value="tab4", children= [

                    dcc.Dropdown(id="publisher_dropdown",
                                 options=[{"label": publisher, "value": publisher} for publisher in unique_publishers]
                                 ),
                ])

            ],
            style={'width': '48%', 'display': 'inline-block'}),
            ],
            style={'width': '48%', 'display': 'inline-block', "outline": "2px dotted black"})
        ],
        style={'width': '100%'}),
        ])
    APP.run(host=host, **kwargs)
    print("The server has closed!")





if __name__ == "__main__":
    initialize_data()
    initialize_dash()

print(csv_path)




