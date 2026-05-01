import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback, ctx, html, no_update
from dash_bootstrap_templates import ThemeSwitchAIO

from optimisation_effectif import ProblemeDeploiement, resoudre

from .layout import BESOINS_DEFAUT, MOIS_ORDONNES


@callback(
    Output("periode-label", "children"),
    Output("besoins-container", "children"),
    Input("mois-slider", "value"),
)
def render_besoins_inputs(slider_value: list[int]):
    debut, fin = slider_value
    mois_selectionnes = MOIS_ORDONNES[debut : fin + 1]
    label = (
        f"{MOIS_ORDONNES[debut]}→{MOIS_ORDONNES[fin]}({len(mois_selectionnes)} mois)"
    )
    rows = []
    for i in range(0, len(mois_selectionnes), 2):
        pair = mois_selectionnes[i : i + 2]
        cols = [
            dbc.Col(
                html.Div(
                    [
                        dbc.Label(m, className="small fw-semibold"),
                        dbc.Input(
                            id={"type": "besoin-input", "mois": m},
                            type="number",
                            value=BESOINS_DEFAUT.get(m, 0),
                            min=0,
                            max=200,
                            step=1,
                        ),
                    ],
                    className="mb-2",
                )
            )
            for m in pair
        ]
        rows.append(dbc.Row(cols, className="g-2"))
    return label, html.Div(rows)


@callback(
    Output("limite-heures-sup", "value"),
    Output("limite-heures-sup-pct", "value"),
    Input("limite-heures-sup", "value"),
    Input("limite-heures-sup-pct", "value"),
    prevent_initial_call=True,
)
def sync_limite_heures_sup(slider_val: float | None, pct_val: float | None):
    if ctx.triggered_id == "limite-heures-sup":
        pct = round(float(slider_val) * 100, 2) if slider_val is not None else no_update
        return no_update, pct
    ratio = max(0.01, min(0.99, float(pct_val) / 100)) if pct_val is not None else 0.25
    return ratio, no_update


@callback(
    Output("fraction-echanges", "value"),
    Output("fraction-echanges-pct", "value"),
    Input("fraction-echanges", "value"),
    Input("fraction-echanges-pct", "value"),
    prevent_initial_call=True,
)
def sync_fraction_echanges(slider_val: float | None, pct_val: float | None):
    if ctx.triggered_id == "fraction-echanges":
        pct = round(float(slider_val) * 100, 2) if slider_val is not None else no_update
        return no_update, pct
    ratio = max(0.05, min(1.0, float(pct_val) / 100)) if pct_val is not None else 1 / 3
    return ratio, no_update


@callback(
    Output("effectif-initial", "disabled"),
    Output("effectif-final", "disabled"),
    Input("libre-initial", "value"),
    Input("libre-final", "value"),
)
def toggle_effectif_inputs(libre_initial: bool, libre_final: bool):
    return libre_initial, libre_final


@callback(
    Output("stat-cout", "children"),
    Output("stat-echanges", "children"),
    Output("stat-effectif", "children"),
    Output("alert-zone", "children"),
    Output("graph-effectif", "figure"),
    Output("graph-couts", "figure"),
    Output("table-zone", "children"),
    Input("mois-slider", "value"),
    Input({"type": "besoin-input", "mois": ALL}, "value"),
    Input("effectif-initial", "value"),
    Input("effectif-final", "value"),
    Input("libre-initial", "value"),
    Input("libre-final", "value"),
    Input("effectif-max", "value"),
    Input("cout-changement", "value"),
    Input("cout-ecart", "value"),
    Input("echanges-max", "value"),
    Input("limite-heures-sup", "value"),
    Input("fraction-echanges", "value"),
    Input(ThemeSwitchAIO.ids.switch("theme-switch"), "value"),
    State({"type": "besoin-input", "mois": ALL}, "id"),
)
def solve(
    mois_values,
    besoins_values,
    effectif_initial,
    effectif_final,
    libre_initial,
    libre_final,
    effectif_max,
    cout_changement,
    cout_ecart,
    echanges_max,
    limite_heures_sup,
    fraction_echanges,
    is_dark: bool,
    besoins_ids,
):
    tpl = "flatly" if is_dark else "darkly"

    empty_fig = go.Figure().update_layout(
        template=tpl,
        height=350,
        margin=dict(l=40, r=20, t=40, b=40),
    )

    debut, fin = mois_values
    mois_ordonnes = MOIS_ORDONNES[debut : fin + 1]

    if len(mois_ordonnes) < 2:
        alert = dbc.Alert("Sélectionnez au moins deux mois.", color="warning")
        return "—", "—", "—", alert, empty_fig, empty_fig, None

    besoins_dict = {
        id_obj["mois"]: int(val)
        for id_obj, val in zip(besoins_ids, besoins_values)
        if val is not None and int(val) > 0
    }

    try:
        eff_max = int(effectif_max) if effectif_max and int(effectif_max) > 0 else None
        eff_initial = None if libre_initial else int(effectif_initial or 0)
        eff_final = None if libre_final else int(effectif_final or 0)

        fraction = float(fraction_echanges or (1 / 3))
        if abs(fraction - 0.33) < 0.01:
            fraction = 1 / 3

        probleme = ProblemeDeploiement(
            mois=mois_ordonnes,
            besoins=besoins_dict,
            effectif_initial=eff_initial,
            effectif_final=eff_final,
            effectif_max=eff_max,
            cout_changement=float(cout_changement or 0),
            cout_ecart=float(cout_ecart or 0),
            limite_heures_sup=float(limite_heures_sup or 0.25),
            echanges_max_absolu=int(echanges_max or 3),
            fraction_echanges_max=fraction,
        )
        solution = resoudre(probleme)
    except Exception as e:
        alert = dbc.Alert([html.Strong("Erreur : "), str(e)], color="danger")
        return "—", "—", "—", alert, empty_fig, empty_fig, None

    # ── Stats ──────────────────────────────────────────────────────────────
    nb_echanges = sum(e.ajouts_suppressions for e in solution.lignes)
    eff_vals = [e.effectif for e in solution.lignes]
    debut_label = f"début={eff_vals[0]}" if libre_initial else ""
    fin_label = f"fin={eff_vals[-1]}" if libre_final else ""
    libre_info = " · ".join(x for x in [debut_label, fin_label] if x)
    stat_eff_caption = f"({libre_info})" if libre_info else ""

    # ── Graph 1 : effectif vs besoins ──────────────────────────────────────
    labels = [e.mois for e in solution.lignes]
    effectifs = [e.effectif for e in solution.lignes]
    besoins_plot = [
        e.besoin_minimal if e.besoin_minimal is not None else 0 for e in solution.lignes
    ]

    c_besoin = "rgba(231, 76, 60, 0.55)" if not is_dark else "rgba(239, 154, 154, 0.75)"
    c_ecart = "rgba(231, 76, 60, 0.65)" if not is_dark else "rgba(239, 154, 154, 0.85)"
    c_cumul = "#7f1d1d" if not is_dark else "#ff8a8a"

    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            x=labels,
            y=besoins_plot,
            name="Besoin minimal",
            marker_color=c_besoin,
        )
    )
    fig1.add_trace(
        go.Scatter(
            x=labels,
            y=effectifs,
            mode="lines+markers",
            name="Effectif optimal",
            line=dict(color="#2a9d8f", width=3),
            marker=dict(size=10),
        )
    )
    fig1.update_layout(
        title="Effectif optimal vs besoins minimaux",
        xaxis_title="Mois",
        yaxis_title="Personnes",
        template=tpl,
        height=350,
        legend=dict(orientation="h", y=1.1, x=0),
        margin=dict(l=40, r=20, t=70, b=40),
    )
    # ── Graph 2 : décomposition des coûts ─────────────────────────────────
    cout_ajust = [e.cout_ajustement for e in solution.lignes]
    cout_ecart_vals = [e.cout_ecart for e in solution.lignes]
    cout_cumule = [e.cout_cumule for e in solution.lignes]

    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=labels,
            y=cout_ajust,
            name="Coût ajustement",
            marker_color="rgba(42, 157, 143, 0.75)",
        )
    )
    fig2.add_trace(
        go.Bar(
            x=labels,
            y=cout_ecart_vals,
            name="Coût écart",
            marker_color=c_ecart,
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=labels,
            y=cout_cumule,
            mode="lines+markers",
            name="Coût cumulé",
            line=dict(color=c_cumul, width=2, dash="dot"),
            marker=dict(size=7),
            yaxis="y2",
        )
    )
    fig2.update_layout(
        title="Décomposition des coûts mensuels",
        xaxis_title="Mois",
        yaxis_title="Coût mensuel (€)",
        yaxis2=dict(title="Coût cumulé (€)", overlaying="y", side="right"),
        barmode="stack",
        template=tpl,
        height=350,
        legend=dict(orientation="h", y=1.1, x=0),
        margin=dict(l=40, r=60, t=70, b=40),
    )
    # ── Table ──────────────────────────────────────────────────────────────
    rows = [
        {
            "Mois": e.mois,
            "Effectif": e.effectif,
            "Besoin min.": e.besoin_minimal if e.besoin_minimal is not None else "—",
            "Échanges": e.ajouts_suppressions,
            "Coût ajust. (€)": f"{e.cout_ajustement:,.0f}",
            "Surnuméraires": e.surnumeraires,
            "Manquants": e.manquants,
            "Coût écart (€)": f"{e.cout_ecart:,.0f}",
            "Coût cumulé (€)": f"{e.cout_cumule:,.0f}",
        }
        for e in solution.lignes
    ]
    table = html.Div(
        [
            html.H6("Plan de déploiement détaillé", className="fw-bold mb-2"),
            dbc.Table.from_dataframe(  # type: ignore
                pd.DataFrame(rows),
                striped=True,
                bordered=False,
                hover=True,
                size="sm",
                className="small",
            ),
        ]
    )

    return (
        f"{solution.cout_total:,.0f} €",
        str(nb_echanges),
        f"{max(eff_vals)} / {min(eff_vals)}"
        + (f"  {stat_eff_caption}" if stat_eff_caption else ""),
        None,
        fig1,
        fig2,
        table,
    )


def init() -> None:
    """Call to ensure all callbacks are registered with Dash."""
