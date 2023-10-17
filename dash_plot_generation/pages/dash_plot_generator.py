import numpy
import dash
from dash import html, dcc
from plotly import graph_objects as go

from dash_plot_generation.styles_and_handles import RATING_MIN_REVIEWS, RATING_SLIDER, RATING_TABLE, \
    RATING_DISTRIBUTION_PLOT, MAIN_PANEL_TAB_DICT, DEV_AVERAGE_RATING_LABEL, \
    DEFAULT_PLOT_STYLE_DICT, WHITE_STEAM, TAB_COLOR, TAB_EDGE, DEFAULT_TABS_DICT, DEVELOPER_DROPDOWN, TAB_NORMAL_DICT, \
    TAB_HIGHLIGHT_DICT, PANEL_DEFAULT_DICT, SMALL_PANEL_DICT, SMALL_TAB_PANEL_DICT, SMALL_PANEL_HEADER_DICT, \
    DEV_TOP_GENRES_LABEL, LIST_DICT, NORMAL_DIVISION_DICT, DEV_CCU_LABEL, DEV_GAME_COUNT_LABEL, DEV_REV_PER_GAME_LABEL, \
    DEV_REVENUE_LABEL, DEV_TOP_GAMES, RATING_TABS, RATING_TABS_OUTPUT_AREA

from dash_plot_generation.data_store import FULL_DATA, OWNER_RANGE_PARTS_SORTED

global APP

# unique_publishers = extract_unique_companies(df["publisher"].apply(lambda x: split_companies(x)))
# unique_developers = extract_unique_companies(df["developer"].iloc[0:10].apply(lambda x: split_companies(x)))
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

# Game popularity filter values
max_reviews = numpy.nanmax(FULL_DATA.apply(lambda x: x["positive"] + x["negative"], axis=1))
owner_range_dict = {index: val_str for (index, (val, val_str)) in enumerate(OWNER_RANGE_PARTS_SORTED)}
min_owner = min(owner_range_dict.keys())
max_owner = max(owner_range_dict.keys())

layout = html.Div(
    children=[
        html.Div(className="row", children=[
            html.Div(children=[
                dcc.Tabs(id="main_plots", value="tab1", children=[
                    dcc.Tab(label="Genre performance", value="tab1",
                            style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT,
                            children=[
                                html.Div(children=[
                                    html.Div(
                                        children=[
                                            html.Div(style=NORMAL_DIVISION_DICT,
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
                                            html.Div(style=SMALL_PANEL_DICT | {'width': '35%', 'height': '100%',
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
                                                dcc.Dropdown(id="genre_dropdown", value="action",
                                                             options=[{"label": html.Span([genre],
                                                                                          style={
                                                                                              'color': WHITE_STEAM}),
                                                                       "value": genre} for genre in
                                                                      ["action"]],
                                                             style={'color': WHITE_STEAM, 'display': 'inline-block',
                                                                    'width': '50%'},
                                                             className='dash-dropdown',
                                                             ),

                                            ],
                                                style={'width': '100%', 'margin-bottom': '50px'})
                                        ]),
                                        dcc.Graph(figure=go.Figure(layout=DEFAULT_PLOT_STYLE_DICT |
                                                                          dict(title="Genre prediction plot",
                                                                               margin=dict(l=20, r=20,
                                                                                           t=50, b=20)))),
                                        html.P("""This is an individual regression estimate for the genre that represents
                                    the estimated amount of games to be produced in the next two years""")

                                    ], style=NORMAL_DIVISION_DICT | {'width': '90%'})

                                ],
                                    style=MAIN_PANEL_TAB_DICT,
                                    className="scrollable")
                            ]),
                    dcc.Tab(label="Game popularity", value="tab2",
                            style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT,
                            children=[
                                html.Div(id="Game pop general layout",
                                         style=MAIN_PANEL_TAB_DICT,
                                         className="scrollable",
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
                                                                   style=NORMAL_DIVISION_DICT | {'width': '100%',
                                                                                                 'height': '100%',
                                                                                                 'margin_left': '0px',
                                                                                                 'margin_right': '0px',
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
                                                      style=NORMAL_DIVISION_DICT | {'width': '90%'},
                                                      children=[
                                                          dcc.Tabs(
                                                              id=RATING_TABS,
                                                              value="plot",
                                                              style=DEFAULT_TABS_DICT,
                                                              children=[
                                                                  dcc.Tab(value="plot",
                                                                          label="Distribution figure",
                                                                          style=TAB_NORMAL_DICT,
                                                                          selected_style=TAB_HIGHLIGHT_DICT | {
                                                                                         'background-color': 'rgb(50, 70, 101)'}),
                                                                  dcc.Tab(label="Top non-free games",
                                                                          value="non-free",
                                                                          style=TAB_NORMAL_DICT,
                                                                          selected_style=TAB_HIGHLIGHT_DICT | {
                                                                              'background-color': 'rgb(50, 70, 101)'}),
                                                                  dcc.Tab(label="Top free games",
                                                                          value="free",
                                                                          style=TAB_NORMAL_DICT,
                                                                          selected_style=TAB_HIGHLIGHT_DICT | {
                                                                              'background-color': 'rgb(50, 70, 101)'})
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
                            style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT),
                    dcc.Tab(label="Market prediction tool", value="tab5",
                            style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT),
                ],
                         style=DEFAULT_TABS_DICT),

            ], style=PANEL_DEFAULT_DICT | {'width': '900px',
                                           'margin-right': '100px', 'padding-left': '50px',
                                           'padding-right': '50px', 'padding-bottom': '50px',
                                           'padding-top': '50px', 'margin-bottom': '50px'
                                           }),
            html.Div(children=[
                dcc.Tabs(id="company_information", value="tab3", children=[
                    dcc.Tab(label="Developer infromation", value="tab3", children=[
                        html.Div(children=[
                            dcc.Dropdown(id=DEVELOPER_DROPDOWN, value="Valve",
                                         options=[{"label": html.Span([developer], style={'color': WHITE_STEAM}),
                                                   "value": developer} for developer in unique_developers],
                                         style={'margin-top': '20px', 'color': WHITE_STEAM},
                                         className='dash-dropdown',
                                         ),
                            html.Div(children=[
                                html.Div(
                                    children=[
                                        html.Div(
                                            children=[html.P("Revenue", style=SMALL_PANEL_HEADER_DICT)],
                                            style={'margin-bottom': '10px',
                                                   'border-bottom': '2px solid ' + TAB_EDGE}),
                                        html.Div(children=[
                                            html.Div(children=[
                                                html.P("Game sale revenue estimates"),
                                                html.Div(children=[
                                                    html.Div(children=[
                                                        html.P(id=DEV_REVENUE_LABEL, children="$524 M",
                                                               style=LIST_DICT | {'padding-left': '5%'})
                                                    ]),
                                                    html.Div(children=[
                                                        html.P(id=DEV_REV_PER_GAME_LABEL, children="$925 M",
                                                               style=LIST_DICT | {'padding-left': '5%'})
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
                                    style=SMALL_TAB_PANEL_DICT | {'margin-right': '20px', 'margin-left': '0px',
                                                                  'border': '1px solid black',
                                                                  'margin-bottom': '0px', 'height':'100%'}
                                ),
                                html.Div(children=[
                                    html.Div(
                                        children=[
                                            html.Div(
                                                children=[html.P("General information",
                                                                 style=SMALL_PANEL_HEADER_DICT)],
                                                style={'margin-bottom': '10px',
                                                       'border-bottom': '2px solid ' + TAB_EDGE}),
                                            html.Div(children=[
                                                html.Div(children=[
                                                    html.P(id=DEV_GAME_COUNT_LABEL, children="5",
                                                           style=LIST_DICT),
                                                ],
                                                    style={'margin-bottom': '10px'}
                                                ),
                                                html.Div(children=[
                                                    html.P(id=DEV_CCU_LABEL, children="",
                                                           style=LIST_DICT),
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
                                                           style=LIST_DICT)
                                                ])
                                            ])
                                        ])

                                ], style=SMALL_TAB_PANEL_DICT | {'width': '45%', 'height': '100%',
                                                                 'margin-right': '0px', 'margin-left': '20px',
                                                                 'border': '1px solid black'}
                                )
                            ], style={'height': '300px', 'overflow':'auto', 'margin-bottom':'20px', 'border': '1px solid black'},
                            ),
                            html.Div(
                                children=[dcc.Graph(style=DEFAULT_PLOT_STYLE_DICT |{'height': '250px', 'width':'100%'})
                                          ]
                            )
                        ],
                        style={'margin-left': '0px', 'margin-right': '0px'},
                        className="scrollable"
                        )
                    ], style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT),
                    dcc.Tab(label="Publisher information", value="tab4", children=[

                        dcc.Dropdown(id="publisher_dropdown", value="Valve",
                                     options=[{"label": publisher, "value": publisher} for publisher in
                                              unique_publishers],
                                     ),
                    ], style=TAB_NORMAL_DICT, selected_style=TAB_HIGHLIGHT_DICT)

                ],
                         style=DEFAULT_TABS_DICT),
            ],
                style=PANEL_DEFAULT_DICT | {'width': '700px',
                                            'padding-left': '50px',
                                            'padding-right': '50px', 'padding-bottom': '50px',
                                            'padding-top': '50px', 'margin-bottom': '50px'
                                            })
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
