import numpy
import dash
from dash import html, dcc
from plotly import graph_objects as go
import dash_plot_generation.data_store as ds
from dash_plot_generation.styles_and_handles import RATING_MIN_REVIEWS, RATING_SLIDER, \
    DEV_AVERAGE_RATING_LABEL, \
    DEFAULT_PLOT_STYLE_DICT, WHITE_STEAM, TAB_COLOR, TAB_EDGE, DEVELOPER_DROPDOWN, \
    DEV_TOP_GENRES_LABEL, DEV_CCU_LABEL, DEV_GAME_COUNT_LABEL, DEV_REV_PER_GAME_LABEL, \
    DEV_REVENUE_LABEL, DEV_TOP_GAMES, RATING_TABS, RATING_TABS_OUTPUT_AREA, GENRE_DROPDOWN, GENRE_PREDICTION_GRAPH, \
    GAMES_BY_DEV_GRAPH, MARKET_PERFORMANCE_SCATTER, MP_COMPANY_TYPE_DROPDOWN, REVENUE_COMPANY_GAME_COUNT, \
    PUB_AVERAGE_RATING_LABEL, PUB_TOP_GENRES_LABEL, PUB_CCU_LABEL, PUB_GAME_COUNT_LABEL, PUB_TOP_GAMES, \
    PUB_REV_PER_GAME_LABEL, PUB_REVENUE_LABEL, GAMES_BY_PUB_GRAPH, PUBLISHER_DROPDOWN, TOP_REVENUE_COMPANIES, \
    TOP_COMPANY_TABLE_AREA

from dash_plot_generation.utils import get_cumulative_owner_game_count_limits_for_dev_and_pub

global APP

# unique_publishers = extract_unique_companies(FULL_DATA["publisher"].apply(lambda x: split_companies(x)))
# unique_developers = extract_unique_companies(FULL_DATA["developer"].apply(lambda x: split_companies(x)))
unique_publishers = ["Valve"]
unique_developers = ["Valve"]

# Genre performance table_values
# genre_owners, genre_revenue = get_genre_popularity_counts(FULL_DATA, 6)
genre_owners = {key: val for (key, val) in
                zip(["Action", "Adventure", "RPG", "Puzzle", "Strategy", "Other"],
                    [0.7, 0.5, 0.1, 0.4, 0.3, 0.7])}
genre_revenue = {key: val for (key, val) in
                 zip(["Action", "Adventure", "RPG", "Puzzle", "Strategy", "Other"],
                     [0.5, 0.4, 0.3, 0.4, 0.6, 0.7])}

# unique_genres = get_all_genres(FULL_DATA)
unique_genres = ["Action", "Adventure"]
# Game popularity filter values
max_reviews = numpy.nanmax(ds.FULL_DATA.apply(lambda x: x["positive"] + x["negative"], axis=1))
owner_range_dict = {index: val_str for (index, (val, val_str)) in enumerate(ds.OWNER_RANGE_PARTS_SORTED)}
min_owner = min(owner_range_dict.keys())
max_owner = max(owner_range_dict.keys())
cumulative_owner_ranges = get_cumulative_owner_game_count_limits_for_dev_and_pub(ds.FULL_DATA)
cum_range_limits = {
    "min": min(cumulative_owner_ranges["developer"]["min"], cumulative_owner_ranges["publisher"]["max"]),
    "max": max(cumulative_owner_ranges["developer"]["max"], cumulative_owner_ranges["publisher"]["max"])}

layout = html.Div(
    children=[
        html.Div(className="row", children=[
            html.Div(children=[
                dcc.Tabs(id="main_plots", value="tab1", className="panel-2", children=[
                    dcc.Tab(label="Genre performance", value="tab1",
                            className="custom-tab", selected_className="custom-tab--selected",
                            children=[
                                html.Div(children=[
                                    html.Div(
                                        children=[
                                            html.Div(className="panel_division",
                                                     children=[dcc.Graph(
                                                         figure=go.Figure(data=[
                                                             {'x': ["Action", "Adventure", "RPG", "Puzzle",
                                                                    "Strategy"],
                                                              'y': [0.7, 0.4, 0.8, 1.2, 1.3],
                                                              'type': 'bar'},
                                                         ],
                                                             layout=DEFAULT_PLOT_STYLE_DICT |
                                                                    dict(title="Relative genre perfomance")
                                                         ),

                                                     ),
                                                         html.P(f"""Genre performance measures the assessed 
                                                         exploitability of the specific game genre. The assessment 
                                                         is done by estimating the genre popularity, and games 
                                                         developed in the next two years and showing the relative 
                                                         differences between the genres.""")]),
                                            html.Div(className="small_panel",
                                                     style={'width': '35%', 'height': '100%',
                                                            'background-color': TAB_COLOR},
                                                     children=[
                                                         html.Div(children=[
                                                             html.Div(style={'width': '100%', 'height': '50%'},
                                                                      children=[dcc.Graph(
                                                                          figure=go.Figure(data=[go.Pie(
                                                                              labels=list(genre_owners.keys()),
                                                                              values=list(genre_owners.values()),
                                                                              sort=False)],
                                                                              layout=DEFAULT_PLOT_STYLE_DICT |
                                                                                     dict(title="Genre popularity",
                                                                                          margin=dict(l=20, r=20,
                                                                                                      t=50, b=20))),
                                                                          style={'width': '100%',
                                                                                 'height': '100%'})]),
                                                             html.Div(style={'width': '100%', 'height': '50%'},
                                                                      children=[dcc.Graph(
                                                                          figure=go.Figure(data=[go.Pie(
                                                                              labels=list(genre_revenue.keys()),
                                                                              values=list(genre_revenue.values()),
                                                                              sort=False)],
                                                                              layout=DEFAULT_PLOT_STYLE_DICT |
                                                                                     dict(
                                                                                         title="Genre revenue share",
                                                                                         margin=dict(l=20, r=20,
                                                                                                     t=50, b=20))),
                                                                          style={'width': '100%',
                                                                                 'height': '100%'})]
                                                                      )

                                                         ], style={'height': '540px'}
                                                         ),
                                                     ]
                                                     )
                                        ]
                                    ),

                                    html.Div(children=[
                                        html.H5("Genre prediction", style={'margin-bottom': '50px'}),
                                        html.Div(children=[
                                            html.Div(children=[
                                                html.P("Selected genre:", style={'margin-bottom': '10px'}),
                                                dcc.Dropdown(id=GENRE_DROPDOWN, value="Action",
                                                             options=[{"label": html.Span([genre],
                                                                                          style={
                                                                                              'color': WHITE_STEAM}),
                                                                       "value": genre} for genre in
                                                                      unique_genres],
                                                             style={'color': WHITE_STEAM, 'display': 'inline-block',
                                                                    'width': '50%'},
                                                             className='dash-dropdown',
                                                             ),

                                            ],
                                                style={'width': '100%', 'margin-bottom': '50px'})
                                        ]),
                                        dcc.Graph(id=GENRE_PREDICTION_GRAPH,
                                                  figure=go.Figure(layout=DEFAULT_PLOT_STYLE_DICT |
                                                                          dict(title="Genre prediction plot",
                                                                               margin=dict(l=20, r=20,
                                                                                           t=50, b=20)))),
                                        html.P("""This is an individual regression estimate for the genre that represents
                                    the estimated amount of games to be produced in the next two years""")

                                    ], className="panel_division",
                                        style={'width': '90%'})

                                ],
                                    className="custom-div-main-panel scrollable")
                            ]),
                    dcc.Tab(label="Free vs Non-free analysis", value="tab2",
                            className="custom-tab", selected_className="custom-tab--selected",
                            children=[
                                html.Div(id="Game pop general layout",
                                         className="custom-div-main-panel scrollable",
                                         children=[
                                             html.Div(id="Game pop top div",
                                                      children=[

                                                          html.Div(children=[html.P("""The free to play market has taken the 
                                                          video game market by storm. It is, however, not clear
                                                          which games in each category are performing the best in terms 
                                                          of user rating. This section contains tools to analyze the
                                                          distribution of user ratings for both free and non-free games
                                                          based on the game amount of owners the games have and on a
                                                          minimum review amount criteria.""",
                                                                                    className="text-note-text")],
                                                                   className='text-note-div'),
                                                          html.Div(id="game popularity filters",
                                                                   className="panel_division",
                                                                   style={'width': '100%', 'height': '100%',
                                                                          'margin_left': '0px', 'margin_right': '0px',
                                                                          'background-color': TAB_COLOR,
                                                                          'margin-bottom': '10px'},

                                                                   children=[
                                                                       html.P("Filters"),
                                                                       html.Small("Number of game owners"),
                                                                       dcc.RangeSlider(id=RATING_SLIDER,
                                                                                       min=min_owner, max=max_owner,
                                                                                       marks=owner_range_dict,
                                                                                       step=None,
                                                                                       value=[min_owner,
                                                                                              max_owner]),
                                                                       html.Small("Minimum amount of reviews"
                                                                                  , style={'vertical-align': 'middle'}),
                                                                       dcc.Input(id=RATING_MIN_REVIEWS,
                                                                                 type="number", min=1,
                                                                                 max=max_reviews, step=1, value=10,
                                                                                 style={'background-color': TAB_COLOR,
                                                                                        'color': WHITE_STEAM,
                                                                                        'border': '2px solid ' + WHITE_STEAM,
                                                                                        'width': '80px',
                                                                                        'height': '20px',
                                                                                        'vertical-align': 'middle',
                                                                                        'margin-left': '10px',
                                                                                        'padding-right': '2px',
                                                                                        'padding-left': '5px'})

                                                                   ]
                                                                   ),

                                                      ]
                                                      ),

                                             html.Div(id="Game pop bottom_region",
                                                      className="panel_division",
                                                      style={'width': '90%'},
                                                      children=[
                                                          dcc.Tabs(
                                                              id=RATING_TABS,
                                                              value="plot",
                                                              className="panel-2",
                                                              children=[
                                                                  dcc.Tab(value="plot",
                                                                          label="Distribution figure",
                                                                          className="custom-tab-sub",
                                                                          selected_className="custom-tab-sub--selected"),
                                                                  dcc.Tab(label="Top non-free games",
                                                                          value="non-free",
                                                                          className="custom-tab sub",
                                                                          selected_className="custom-tab-sub--selected"),
                                                                  dcc.Tab(label="Top free games",
                                                                          value="free",
                                                                          className="custom-tab sub",
                                                                          selected_className="custom-tab-sub--selected")
                                                              ]
                                                          ),
                                                          html.Div(className="scrollable div-with_scroll",
                                                                   children=[html.Div(id=RATING_TABS_OUTPUT_AREA)])

                                                      ])
                                         ]
                                         ),
                            ]
                            ),
                    dcc.Tab(label="Market performance", value="tab4",
                            className="custom-tab", selected_className="custom-tab--selected",
                            children=[
                                html.Div(
                                    children=[
                                        html.Div(children=[
                                            html.Div(children=[dcc.Graph(id=MARKET_PERFORMANCE_SCATTER,
                                                                         figure=go.Figure(
                                                                             layout=DEFAULT_PLOT_STYLE_DICT |
                                                                                    dict(
                                                                                        title="Market performance",
                                                                                        margin=dict(l=20, r=20,
                                                                                                    t=50,
                                                                                                    b=20)))
                                                                         )],
                                                     style={"width": "80%", "vertical-align": "top",
                                                            "display": "inline-block", "margin-right": "5%"}),
                                            html.Div(children=[html.H5("Filters"),
                                                               dcc.Dropdown(id=MP_COMPANY_TYPE_DROPDOWN,
                                                                            className='dash-dropdown',
                                                                            value="developer",
                                                                            options=["developer", "publisher"]),
                                                               dcc.RangeSlider(id=REVENUE_COMPANY_GAME_COUNT,
                                                                               min=cum_range_limits["min"],
                                                                               max=cum_range_limits["max"],
                                                                               step=cum_range_limits["min"],
                                                                               value=[cum_range_limits["min"],
                                                                                      cum_range_limits["max"]],
                                                                               marks=None,
                                                                               tooltip={"placement": "right",
                                                                                        "always_visible": True},
                                                                               vertical=True,
                                                                               verticalHeight=200),
                                                               ],
                                                     style={"width": "15%", "vertical-align": "top",
                                                            "display": "inline-block"})
                                        ], style={"display": "flex", "align-items": "flex-start",
                                                  "margin-bottom": "50px"}
                                        ),
                                        html.Div(id="Market performance_second",
                                                 children=[
                                                     html.H5("Top companies"),
                                                     dcc.Tabs(
                                                         id=TOP_REVENUE_COMPANIES,
                                                         value="developer",
                                                         className="panel-2",
                                                         children=[
                                                             dcc.Tab(value="developer",
                                                                     label="Developers",
                                                                     className="custom-tab-sub",
                                                                     selected_className="custom-tab-sub--selected"),
                                                             dcc.Tab(label="Publishers",
                                                                     value="publisher",
                                                                     className="custom-tab sub",
                                                                     selected_className="custom-tab-sub--selected")
                                                         ]
                                                     ),
                                                     html.Div(className="scrollable div-with_scroll",
                                                              children=[html.Div(id=TOP_COMPANY_TABLE_AREA)])
                                                 ]
                                        )
                                    ],
                                    className="custom-div-main-panel scrollable"
                                )

                            ],
                            ),
                ]),

            ],
                className="panel-1",
                style={'width': '900px'}),
            html.Div(children=[
                dcc.Tabs(id="company_information", value="tab3", className="panel-2", children=[
                    dcc.Tab(label="Developer infromation",
                            className="custom-tab", selected_className="custom-tab--selected",
                            value="tab3", children=[
                            html.Div(children=[
                                dcc.Dropdown(id=DEVELOPER_DROPDOWN, value="Valve",
                                             options=[{"label": html.Span([developer], style={'color': WHITE_STEAM}),
                                                       "value": developer} for developer in unique_developers],
                                             style={'margin-top': '20px'},
                                             className='dash-dropdown',
                                             ),
                                html.Div(children=[
                                    html.Div(
                                        children=[
                                            html.Div(
                                                children=[html.P("Revenue", className="small_header")],
                                                style={'margin-bottom': '10px',
                                                       'border-bottom': '2px solid ' + TAB_EDGE}),
                                            html.Div(children=[
                                                html.Div(children=[
                                                    html.P("Game sale revenue estimates"),
                                                    html.Div(children=[
                                                        html.Div(children=[
                                                            html.P(id=DEV_REVENUE_LABEL, children="$524 M",
                                                                   className="list", style={'padding-left': '5%'})
                                                        ]),
                                                        html.Div(children=[
                                                            html.P(id=DEV_REV_PER_GAME_LABEL, children="$925 M",
                                                                   className="list", style={'padding-left': '5%'})
                                                        ]),
                                                    ],
                                                        style={'margin-bottom': '20px'}),
                                                    html.Div(children=[
                                                        html.P("Top games by revenue:"),
                                                        html.Small(id=DEV_TOP_GAMES, children="Half life 2"),
                                                    ])
                                                ]),
                                            ])
                                        ],
                                        className="small_panel_tab_div",
                                        style={'margin-right': '20px'}
                                    ),
                                    html.Div(children=[
                                        html.Div(
                                            children=[
                                                html.Div(
                                                    children=[html.P("General information",
                                                                     className="small_header")],
                                                    style={'margin-bottom': '10px',
                                                           'border-bottom': '2px solid ' + TAB_EDGE}),
                                                html.Div(children=[
                                                    html.Div(children=[
                                                        html.P(id=DEV_GAME_COUNT_LABEL, children="5",
                                                               className="list"),
                                                    ],
                                                        style={'margin-bottom': '10px'}
                                                    ),
                                                    html.Div(children=[
                                                        html.P(id=DEV_CCU_LABEL, children="",
                                                               className="list"),
                                                    ],
                                                        style={'margin-bottom': '10px'}
                                                    ),
                                                    html.Div(children=[
                                                        html.P("Popular game genres:"),
                                                        html.Small(id=DEV_TOP_GENRES_LABEL,
                                                                   children="FPS, Action, Puzzle"),
                                                    ],
                                                        style={'margin-bottom': '10px'}
                                                    ),
                                                    html.Div(children=[
                                                        html.P(id=DEV_AVERAGE_RATING_LABEL,
                                                               children="",
                                                               className="list")
                                                    ])
                                                ])
                                            ])

                                    ], className="small_panel_tab_div",
                                        style={'margin-left': '20px'}
                                    )
                                ], style={'height': '300px', 'overflow': 'auto', 'margin-bottom': '20px'},
                                ),
                                html.Div(
                                    children=[dcc.Graph(id=GAMES_BY_DEV_GRAPH,
                                                        style=DEFAULT_PLOT_STYLE_DICT | {'height': '250px',
                                                                                         'width': '100%'})
                                              ]
                                )
                            ],
                                style={'margin-left': '0px', 'margin-right': '0px'},
                                className="scrollable"
                            )
                        ]),
                    dcc.Tab(label="Publisher information", value="tab4",
                            className="custom-tab", selected_className="custom-tab--selected",
                            children=[

                                dcc.Dropdown(id=PUBLISHER_DROPDOWN, value="Valve",
                                             options=[{"label": html.Span([publisher], style={'color': WHITE_STEAM}),
                                                       "value": publisher} for publisher in
                                                      unique_publishers],
                                             style={'margin-top': '20px'},
                                             className='dash-dropdown',
                                             ),
                                html.Div(children=[
                                    html.Div(
                                        children=[
                                            html.Div(
                                                children=[html.P("Revenue", className="small_header")],
                                                style={'margin-bottom': '10px',
                                                       'border-bottom': '2px solid ' + TAB_EDGE}),
                                            html.Div(children=[
                                                html.Div(children=[
                                                    html.P("Game sale revenue estimates"),
                                                    html.Div(children=[
                                                        html.Div(children=[
                                                            html.P(id=PUB_REVENUE_LABEL, children="$524 M",
                                                                   className="list", style={'padding-left': '5%'})
                                                        ]),
                                                        html.Div(children=[
                                                            html.P(id=PUB_REV_PER_GAME_LABEL, children="$925 M",
                                                                   className="list", style={'padding-left': '5%'})
                                                        ]),
                                                    ],
                                                        style={'margin-bottom': '20px'}),
                                                    html.Div(children=[
                                                        html.P("Top games by revenue:"),
                                                        html.Small(id=PUB_TOP_GAMES, children="Half life 2"),
                                                    ])
                                                ]),
                                            ])
                                        ],
                                        className="small_panel_tab_div",
                                        style={'margin-right': '20px'}
                                    ),
                                    html.Div(children=[
                                        html.Div(
                                            children=[
                                                html.Div(
                                                    children=[html.P("General information",
                                                                     className="small_header")],
                                                    style={'margin-bottom': '10px',
                                                           'border-bottom': '2px solid ' + TAB_EDGE}),
                                                html.Div(children=[
                                                    html.Div(children=[
                                                        html.P(id=PUB_GAME_COUNT_LABEL, children="5",
                                                               className="list"),
                                                    ],
                                                        style={'margin-bottom': '10px'}
                                                    ),
                                                    html.Div(children=[
                                                        html.P(id=PUB_CCU_LABEL, children="",
                                                               className="list"),
                                                    ],
                                                        style={'margin-bottom': '10px'}
                                                    ),
                                                    html.Div(children=[
                                                        html.P("Popular game genres:"),
                                                        html.Small(id=PUB_TOP_GENRES_LABEL,
                                                                   children="FPS, Action, Puzzle"),
                                                    ],
                                                        style={'margin-bottom': '10px'}
                                                    ),
                                                    html.Div(children=[
                                                        html.P(id=PUB_AVERAGE_RATING_LABEL,
                                                               children="",
                                                               className="list")
                                                    ])
                                                ])
                                            ])

                                    ], className="small_panel_tab_div",
                                        style={'margin-left': '20px'}
                                    )
                                ], style={'height': '300px', 'overflow': 'auto', 'margin-bottom': '20px'},
                                ),
                                html.Div(
                                    children=[dcc.Graph(id=GAMES_BY_PUB_GRAPH,
                                                        style=DEFAULT_PLOT_STYLE_DICT | {'height': '250px',
                                                                                         'width': '100%'})
                                              ]
                                )
                            ])

                ]),
            ],
                className="panel-1",
                style={'width': '700px'})
        ],
                 style={'width': '100%', "padding-top": "30px", 'padding-left': "50px"}),
    ],
    style={"font-family": "Tahoma"},
    className="body"
)
dash.register_page(
    __name__,
    title="Dashboard",
    description="Main dashboard",
    path="/dashboard",
)
