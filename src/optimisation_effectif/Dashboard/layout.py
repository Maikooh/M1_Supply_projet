import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_bootstrap_templates import ThemeSwitchAIO

# paramètres par défaut

MOIS_ORDONNES = [
    "Janvier",
    "Fevrier",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Aout",
    "Septembre",
    "Octobre",
    "Novembre",
    "Decembre",
]

BESOINS_DEFAUT = {
    "Mars": 4,
    "Avril": 6,
    "Mai": 7,
    "Juin": 4,
    "Juillet": 6,
    "Aout": 2,
}

IDX_DEBUT_DEFAUT = 0  # Janvier
IDX_FIN_DEFAUT = 8  # Septembre

# components


def param_card(title: str, children) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([html.H6(title, className="text-muted mb-3"), children]),
        className="mb-3 shadow-sm",
    )


def stat_card(label: str, card_id: str) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody(
            [
                html.P(label, className="text-muted small mb-1"),
                html.H4("—", id=card_id, className="fw-bold text-primary mb-0"),
            ]
        ),
        className="text-center shadow-sm h-100",
    )


def number_field(field_id, label: str, value, min_val=0, max_val=500, step=1):
    return html.Div(
        [
            dbc.Label(label, className="small fw-semibold"),
            dbc.Input(
                id=field_id,
                type="number",
                value=value,
                min=min_val,
                max=max_val,
                step=step,
            ),
        ],
        className="mb-2",
    )


# sidebar

SIDEBAR_STYLE = {
    "overflowY": "auto",
    "height": "100vh",
    "padding": "1.25rem 1rem",
}
MAIN_STYLE = {"padding": "1.5rem 2rem", "overflowY": "auto", "height": "100vh"}


# Layout final
def create_layout() -> dbc.Container:
    sidebar = html.Div(
        [
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.H5("Paramètres", className="fw-bold mb-0"),
                                className="d-flex align-items-center",
                            ),
                            dbc.Col(
                                ThemeSwitchAIO(
                                    aio_id="theme-switch",
                                    themes=[dbc.themes.FLATLY, dbc.themes.DARKLY],
                                ),
                                width="auto",
                            ),
                        ],
                        className="align-items-center justify-content-between g-0",
                    ),
                    html.Hr(className="my-2"),
                ]
            ),
            param_card(
                "Période",
                html.Div(
                    [
                        html.Div(
                            id="periode-label",
                            className="small text-center mb-2 fw-semibold",
                        ),
                        dcc.RangeSlider(
                            id="mois-slider",
                            min=0,
                            max=len(MOIS_ORDONNES) - 1,
                            step=1,
                            value=[IDX_DEBUT_DEFAUT, IDX_FIN_DEFAUT],
                            marks={
                                i: {"label": m[:3], "style": {"fontSize": "11px"}}
                                for i, m in enumerate(MOIS_ORDONNES)
                            },
                            allowCross=False,
                            pushable=1,
                        ),
                    ]
                ),
            ),
            param_card("Besoins minimaux (pers.)", html.Div(id="besoins-container")),
            param_card(
                "Effectifs",
                html.Div(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        [
                                            dbc.Label(
                                                "Initial", className="small fw-semibold"
                                            ),
                                            dbc.InputGroup(
                                                [
                                                    dbc.Input(
                                                        id="effectif-initial",
                                                        type="number",
                                                        value=3,
                                                        min=0,
                                                        max=500,
                                                        step=1,
                                                        size="sm",
                                                    ),
                                                    dbc.InputGroupText(
                                                        dbc.Switch(
                                                            id="libre-initial",
                                                            label="Libre",
                                                            value=False,
                                                            className="mb-0",
                                                        ),
                                                        style={
                                                            "background": "none",
                                                            "border": "none",
                                                        },
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mb-2",
                                    )
                                ),
                                dbc.Col(
                                    html.Div(
                                        [
                                            dbc.Label(
                                                "Final", className="small fw-semibold"
                                            ),
                                            dbc.InputGroup(
                                                [
                                                    dbc.Input(
                                                        id="effectif-final",
                                                        type="number",
                                                        value=3,
                                                        min=0,
                                                        max=500,
                                                        step=1,
                                                        size="sm",
                                                    ),
                                                    dbc.InputGroupText(
                                                        dbc.Switch(
                                                            id="libre-final",
                                                            label="Libre",
                                                            value=False,
                                                            className="mb-0",
                                                        ),
                                                        style={
                                                            "background": "none",
                                                            "border": "none",
                                                        },
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mb-2",
                                    )
                                ),
                            ],
                            className="g-2",
                        ),
                        number_field("effectif-max", "Maximum (0 = auto)", 10),
                    ]
                ),
            ),
            param_card(
                "Coûts (€)",
                html.Div(
                    [
                        number_field(
                            "cout-changement", "Par changement (€/pers.)", 160
                        ),
                        number_field("cout-ecart", "Par écart (€/pers./mois)", 200),
                    ]
                ),
            ),
            param_card(
                "Contraintes",
                html.Div(
                    [
                        number_field(
                            "echanges-max",
                            "Échanges maximum par mois",
                            3,
                            min_val=1,
                            max_val=100,
                        ),
                        html.Div(
                            [
                                dbc.Label(
                                    "Limite heures supp. (ratio du besoin)",
                                    className="small fw-semibold",
                                ),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(
                                            id="limite-heures-sup-pct",
                                            type="number",
                                            value=25,
                                            min=1,
                                            max=99,
                                            step=0.5,
                                        ),
                                        dbc.InputGroupText("%"),
                                    ],
                                    size="sm",
                                    className="mb-2",
                                ),
                                dcc.Slider(
                                    id="limite-heures-sup",
                                    min=0.01,
                                    max=0.99,
                                    step=0.01,
                                    value=0.25,
                                    marks={
                                        0.1: {"label": "10%", "style": {"color": "#adb5bd", "fontWeight": "600"}},
                                        0.25: {"label": "25%", "style": {"color": "#adb5bd", "fontWeight": "600"}},
                                        0.5: {"label": "50%", "style": {"color": "#adb5bd", "fontWeight": "600"}},
                                        0.75: {"label": "75%", "style": {"color": "#adb5bd", "fontWeight": "600"}},
                                    },
                                ),
                            ],
                            className="mb-3",
                        ),
                        html.Div(
                            [
                                dbc.Label(
                                    "Fraction échanges max (ratio effectif actuel)",
                                    className="small fw-semibold",
                                ),
                                dbc.InputGroup(
                                    [
                                        dbc.Input(
                                            id="fraction-echanges-pct",
                                            type="number",
                                            value=33.3,
                                            min=5,
                                            max=100,
                                            step=0.5,
                                        ),
                                        dbc.InputGroupText("%"),
                                    ],
                                    size="sm",
                                    className="mb-2",
                                ),
                                dcc.Slider(
                                    id="fraction-echanges",
                                    min=0.05,
                                    max=1.0,
                                    step=0.01,
                                    value=1 / 3,
                                    marks={
                                        0.25: {"label": "25%", "style": {"color": "#adb5bd", "fontWeight": "600"}},
                                        0.5: {"label": "50%", "style": {"color": "#adb5bd", "fontWeight": "600"}},
                                        0.75: {"label": "75%", "style": {"color": "#adb5bd", "fontWeight": "600"}},
                                        1.0: {"label": "100%", "style": {"color": "#adb5bd", "fontWeight": "600"}},
                                    },
                                ),
                            ]
                        ),
                    ]
                ),
            ),
        ],
        id="sidebar",
        className="border-end",
        style=SIDEBAR_STYLE,
    )

    main_content = html.Div(
        [
            html.H4("Déploiement Optimal de Personnel", className="fw-bold mb-1"),
            html.P(
                "Les résultats se recalculent automatiquement à chaque modification.",
                className="text-muted small mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(stat_card("Coût total optimal", "stat-cout"), md=4),
                    dbc.Col(
                        stat_card("Total échanges de personnel", "stat-echanges"), md=4
                    ),
                    dbc.Col(stat_card("Effectif max / min", "stat-effectif"), md=4),
                ],
                className="mb-4 g-3",
            ),
            html.Div(id="alert-zone", className="mb-3"),
            dcc.Graph(
                id="graph-effectif", config={"displayModeBar": False}, className="mb-3"
            ),
            dcc.Graph(
                id="graph-couts", config={"displayModeBar": False}, className="mb-4"
            ),
            html.Div(id="table-zone", className="mb-4"),
        ],
        id="main-content",
        style=MAIN_STYLE,
    )

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(sidebar, md=3, style={"padding": 0}),
                    dbc.Col(main_content, md=9, style={"padding": 0}),
                ],
                className="g-0",
            ),
        ],
        id="root-container",
        fluid=True,
        style={"height": "100vh", "overflow": "hidden"},
    )
