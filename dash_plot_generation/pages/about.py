import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div(children=[
        html.Div(className="w-layout-blockcontainer container-5 w-container",
                 children=[
                     html.H1("SteamSavvy - Steam game data insights")
                 ]),
        html.Div(
            className="w-layout-blockcontainer container-5 w-container",
            children=[
                html.P(["SteamSavvy started as a simple project for a data science course: analyze and present the results "
                       "in a simple manner. However, the project blossomed into a full-blown dashboard with a "
                       "handmade UI, and style components.",
                       html.Br(),
                       html.Br(),
                       "The core idea behind the project has always remained the "
                       "same: to utilize Steam gaming platform data to provide insightful information to users, "
                       "offering practical insights into the gaming industry. Whether you're an investor, developer, "
                       "marketer, or stakeholder, the challenge is the same - how do you make sense of the wealth of "
                       "available data? Which metrics truly matter? Where do you even begin?",
                       html.Br(),
                       html.Br(),
                       "That's where our project "
                       "comes in. We recognized the need for a straightforward analytics tool tailored for the video "
                       "game industry, with a focus on platforms like Steam, a major player in the PC gaming market."],
                       className="paragraph"),
                html.H3("Our Approach & Why steam"),
                html.P("Steam, with its extensive library of over 50,000 games and 45,000 developers, is a central "
                       "hub in the gaming distribution world. It's a treasure trove of data, including game revenues, "
                       "ownership statistics, and player reviews."
                       ""
                       "Our approach revolves around two core elements:",
                       className="paragraph"),
                html.Div(className="w-layout-blockcontainer w-container side-listing",
                         children=[
                             html.Div(className="w-layout-blockcontainer w-container small_listing",
                                      children=[
                                          html.P("Genre Comparison", className="bold-text"),
                                          html.P(className="paragraph small",
                                                 children="We aim to demystify the gaming world by analyzing which genres are on "
                                                          "the rise, which are declining, and which are holding steady. Our "
                                                          "insights empower developers to create in-demand games and help "
                                                          "investors make informed decisions.")
                                      ]),
                             html.Div(className="w-layout-blockcontainer w-container small_listing",
                                      children=[
                                          html.P("Company Performance Metrics", className="bold-text"),
                                          html.P(className="paragraph small",
                                                 children="In the gaming industry, not all creators are equal. We "
                                                          "assess how different game developers and publishers "
                                                          "perform on Steam, offering insights into both industry "
                                                          "leaders and emerging talents.")
                                      ])

                         ])

            ],
        ),
        html.Div(className="w-layout-blockcontainer w-container container-6",
                 children=[
                     html.H2(className="centered-heading",
                             children="Project developers"),
                     html.P(className="centered-subheading",
                            children="This project was not build in a day nor by just one person. Everyone "
                                     "contributed and focused on a unique aspect of the project."),
                     html.Div(className="w-layout-blockcontainer w-container team-grid",
                              children=[
                                  html.Div(className="w-layout-blockcontainer w-container team-card",
                                           children=[
                                               html.A(
                                                   html.Img(className="team-member-image", alt="",
                                                            src="assets/team/Linsen_G.jpg"),
                                                   href="https://www.linkedin.com/in/linsen-gao-036452298/",
                                                   target="_blank"
                                               ),
                                               html.P(className="team-member-name", children="Linsen Gao"),
                                               html.P(className="team-member-position", children="Master's Data "
                                                                                                 "Science "
                                                                                                 "StudentUniversity "
                                                                                                 "of Helsinki"),
                                               html.A(
                                                   html.Img(alt="",
                                                            src="assets/team/logo.png",
                                                            sizes="40px", width="40", height=""),
                                                   href="https://www.linkedin.com/in/linsen-gao-036452298/",
                                                   target="_blank"
                                               ),
                                           ]),
                                  html.Div(className="w-layout-blockcontainer w-container team-card",
                                           children=[
                                               html.A(
                                                   html.Img(className="team-member-image", alt="",
                                                            src="assets/team/Sergei_P.jpg"),
                                                   href="https://www.linkedin.com/in/panarin97/",
                                                   target="_blank"
                                               ),
                                               html.P(className="team-member-name", children="Sergei Panarin"),
                                               html.P(className="team-member-position", children="Master's Data "
                                                                                                 "Science "
                                                                                                 "StudentUniversity "
                                                                                                 "of Helsinki"),

                                               html.A(
                                                   html.Img(alt="",
                                                            src="assets/team/logo.png",
                                                            sizes="40px", width="40", height=""),
                                                   href="https://www.linkedin.com/in/panarin97/",
                                                   target="_blank"
                                               ),
                                           ]),
                                  html.Div(className="w-layout-blockcontainer w-container team-card",
                                           children=[
                                               html.A(
                                               html.Img(className="team-member-image", alt="",
                                                        src="assets/team/Max_V.jpg"),
                                                   href="https://www.linkedin.com/in/max-v%C3%A4ist%C3%B6-2985a9263/",
                                                   target="_blank"
                                               ),
                                               html.P(className="team-member-name", children="Max Väistö"),
                                               html.P(className="team-member-position", children="Master's Data "
                                                                                                 "Science "
                                                                                                 "StudentUniversity "
                                                                                                 "of Helsinki"),

                                               html.A(
                                               html.Img(alt="",
                                                        src="assets/team/logo.png",
                                                        sizes="40px", width="40", height=""),
                                                   href="https://www.linkedin.com/in/max-v%C3%A4ist%C3%B6-2985a9263/",
                                                   target="_blank"
                                               ),
                                           ])

                              ])
                 ]),

    ],
    ),

], className="body scrollable")

dash.register_page(
    __name__,
    title="Dashboard",
    description="Main dashboard",
    path="/about",
)
