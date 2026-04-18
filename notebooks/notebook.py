import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    from dataclasses import asdict, dataclass

    import math
    import marimo as mo
    import networkx as nx
    import pandas as pd
    import plotly.graph_objects as go

    return asdict, dataclass, go, math, mo, nx, pd


@app.cell
def _(mo):
    mo.md(r"""
    # Sujet 10 — Déploiement optimal de personnel

    Une compagnie de travaux publics doit décider du déploiement de personnel sur un site sur la période de janvier à septembre.

    ## Données du problème

    **Besoins minimaux en personnel :**

    | Mois | Personnes requises |
    |------|--------------------|
    | Mars | 4 |
    | Avril | 6 |
    | Mai | 7 |
    | Juin | 4 |
    | Juillet | 6 |
    | Août | 2 |

    **Contraintes et coûts :**

    - Effectif initial (janvier) : **3 personnes**
    - Effectif final (septembre) : **3 personnes**
    - Ajouter ou retirer une personne : **160 €**
    - Au plus **3 échanges par mois**, et au plus **1/3 de l'effectif présent**
    - Frais de personnel surnuméraire : **200 € / personne / mois**
    - Frais de personnel manquant : **200 € / personne / mois**, dans la limite de **25 % d'heures supplémentaires**

    ## Méthode

    Le problème est modélisé comme un plus court chemin dans un graphe orienté acyclique (DAG).
    Chaque nœud représente un état *(mois, effectif)* et chaque arc un passage d'un mois au suivant.
    L'algorithme de **Bellman-Ford** est utilisé pour trouver le chemin de coût minimal.
    """)
    return


@app.cell
def _(dataclass):
    @dataclass
    class Configuration:
        cout_changement: int = 160
        cout_ecart: int = 200
        limite_heures_sup: float = 0.25
        effectif_max: int = 10
        effectif_initial: int = 3
        effectif_final: int = 3

    cfg = Configuration()
    return (cfg,)


@app.cell
def _(cfg):
    mois = [
        "Janvier",
        "Fevrier",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Aout",
        "Septembre",
    ]

    besoins = {
        "Mars": 4,
        "Avril": 6,
        "Mai": 7,
        "Juin": 4,
        "Juillet": 6,
        "Aout": 2,
    }

    niveaux_effectif = range(cfg.effectif_max + 1)
    return besoins, mois, niveaux_effectif


@app.cell
def _(dataclass):
    @dataclass
    class LignePlan:
        mois:                str
        effectif:            int
        besoin_minimal:      int | str
        ajouts_suppressions: int
        cout_ajustement:     float
        surnumeraires:       int
        manquants:           int
        cout_ecart:          float
        cout_cumule:         float

        LABELS = [
            "Mois",
            "Effectif",
            "Besoin minimal",
            "Ajouts / Suppressions",
            "Coût ajustement (EUR)",
            "Surnuméraires",
            "Manquants",
            "Coût écart (EUR)",
            "Coût cumulé (EUR)",
        ]

    return (LignePlan,)


@app.cell
def _(besoins, cfg):
    def calculer_cout_ecart(mois_nom: str, effectif: int):
        """
        Retourne (coût total écart, surnuméraires, manquants)
        ou None si le dépassement d'heures supplémentaires est hors limite.
        """
        besoin = besoins.get(mois_nom)
        if besoin is None:
            return 0, 0, 0

        surnumeraires = max(effectif - besoin, 0)
        manquants = max(besoin - effectif, 0)

        if manquants > cfg.limite_heures_sup * besoin:
            return None

        return cfg.cout_ecart * (surnumeraires + manquants), surnumeraires, manquants

    return (calculer_cout_ecart,)


@app.cell
def _(math):
    def est_effectif_valide(indice_mois: int, effectif: int, nb_mois: int, cfg) -> bool:
        if indice_mois == 0:
            return effectif == cfg.effectif_initial
        if indice_mois == nb_mois - 1:
            return effectif == cfg.effectif_final
        return True


    def echange_autorise(effectif_actuel: int, effectif_suivant: int) -> bool:
        echanges = abs(effectif_suivant - effectif_actuel)
        echanges_max = min(3, math.floor(effectif_actuel / 3))
        return echanges <= echanges_max

    return echange_autorise, est_effectif_valide


@app.cell
def _(echange_autorise, est_effectif_valide):
    def ajouter_noeuds(G, mois, niveaux_effectif, cfg, calculer_cout_ecart):
        for indice_mois, nom_mois in enumerate(mois):
            for effectif in niveaux_effectif:
                if not est_effectif_valide(indice_mois, effectif, len(mois), cfg):
                    continue
                resultat = calculer_cout_ecart(nom_mois, effectif)
                if resultat is None:
                    continue
                cout_ecart_val, surnumeraires, manquants = resultat
                G.add_node(
                    (indice_mois, effectif),
                    mois=nom_mois,
                    effectif=effectif,
                    cout_ecart=cout_ecart_val,
                    surnumeraires=surnumeraires,
                    manquants=manquants,
                )

    def ajouter_arcs(G, mois, niveaux_effectif, cfg):
        for indice_mois in range(len(mois) - 1):
            for effectif_actuel in niveaux_effectif:
                source = (indice_mois, effectif_actuel)
                if source not in G:
                    continue
                for effectif_suivant in niveaux_effectif:
                    destination = (indice_mois + 1, effectif_suivant)
                    if destination not in G:
                        continue
                    if not echange_autorise(effectif_actuel, effectif_suivant):
                        continue
                    echanges = abs(effectif_suivant - effectif_actuel)
                    poids = (
                        cfg.cout_changement * echanges
                        + G.nodes[destination]["cout_ecart"]
                    )
                    G.add_edge(source, destination, poids=poids, echanges=echanges)

    return ajouter_arcs, ajouter_noeuds


@app.cell
def _(
    ajouter_arcs,
    ajouter_noeuds,
    calculer_cout_ecart,
    cfg,
    mois,
    niveaux_effectif,
    nx,
):
    G_complet = nx.DiGraph()
    ajouter_noeuds(G_complet, mois, niveaux_effectif, cfg, calculer_cout_ecart)
    ajouter_arcs(G_complet, mois, niveaux_effectif, cfg)

    source = (0, cfg.effectif_initial)
    cible = (len(mois) - 1, cfg.effectif_final)

    try:
        ancetres_cible = nx.ancestors(G_complet, cible) | {cible}
        descendants_source = nx.descendants(G_complet, source) | {source}

        noeuds_utiles = ancetres_cible.intersection(descendants_source)
        G = G_complet.subgraph(noeuds_utiles).copy()
    except Exception:
        G = G_complet
    return (G,)


@app.cell
def _(G, cfg, mois, nx):
    noeud_depart = (0, cfg.effectif_initial)
    noeud_arrivee = (len(mois) - 1, cfg.effectif_final)

    chemin_optimal = nx.bellman_ford_path(
        G, noeud_depart, noeud_arrivee, weight="poids"
    )
    cout_total_minimal = nx.path_weight(G, chemin_optimal, weight="poids")
    arcs_optimaux = set(zip(chemin_optimal, chemin_optimal[1:]))
    return arcs_optimaux, chemin_optimal, cout_total_minimal


@app.cell
def _(mo):
    mo.md("""
    ## Résultats
    """)
    return


@app.cell
def _(G, cout_total_minimal, mo):
    mo.stat(
        value=f"{cout_total_minimal:,.0f} €",
        label="Coût total minimal",
        caption=f"{G.number_of_nodes()} nœuds · {G.number_of_edges()} arcs explorés",
    )
    return


@app.cell
def _(LignePlan):
    def calculer_nb_echanges(indice_etape: int, effectif: int, chemin_optimal: list) -> int:
        if indice_etape == 0:
            return 0
        effectif_precedent = chemin_optimal[indice_etape - 1][1]
        return abs(effectif - effectif_precedent)


    def construire_plan(G, chemin_optimal, mois, besoins, cfg) -> list[LignePlan]:
        lignes = []
        cumul = 0

        for indice_etape, noeud in enumerate(chemin_optimal):
            indice_mois, effectif = noeud
            nom_mois = mois[indice_mois]
            donnees_noeud = G.nodes[noeud]

            nb_echanges = calculer_nb_echanges(indice_etape, effectif, chemin_optimal)
            cout_ajustement = cfg.cout_changement * nb_echanges
            cout_ecart_mensuel = donnees_noeud["cout_ecart"]
            cumul += cout_ajustement + cout_ecart_mensuel

            lignes.append(LignePlan(
                mois=nom_mois,
                effectif=effectif,
                besoin_minimal=besoins.get(nom_mois, "non défini"),
                ajouts_suppressions=nb_echanges,
                cout_ajustement=cout_ajustement,
                surnumeraires=donnees_noeud["surnumeraires"],
                manquants=donnees_noeud["manquants"],
                cout_ecart=cout_ecart_mensuel,
                cout_cumule=cumul,
            ))

        return lignes

    return (construire_plan,)


@app.cell
def _(
    G,
    LignePlan,
    asdict,
    besoins,
    cfg,
    chemin_optimal,
    construire_plan,
    mo,
    mois,
    pd,
):
    lignes = construire_plan(G, chemin_optimal, mois, besoins, cfg)
    df_plan = pd.DataFrame([asdict(ligne) for ligne in lignes])
    df_plan.columns = LignePlan.LABELS
    mo.ui.table(df_plan)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Visualisation du DAG
    """)
    return


@app.cell
def _(go):
    def calculer_positions(G) -> dict:
        return {
            (indice_mois, effectif): (indice_mois, -effectif)
            for (indice_mois, effectif) in G.nodes
        }

    def separer_arcs(G, positions, arcs_optimaux) -> tuple:
        arcs_x_normaux, arcs_y_normaux = [], []
        arcs_x_optimaux, arcs_y_optimaux = [], []

        for noeud_source, noeud_dest in G.edges:
            x_source, y_source = positions[noeud_source]
            x_dest, y_dest = positions[noeud_dest]
            if (noeud_source, noeud_dest) in arcs_optimaux:
                arcs_x_optimaux += [x_source, x_dest, None]
                arcs_y_optimaux += [y_source, y_dest, None]
            else:
                arcs_x_normaux += [x_source, x_dest, None]
                arcs_y_normaux += [y_source, y_dest, None]

        return arcs_x_normaux, arcs_y_normaux, arcs_x_optimaux, arcs_y_optimaux

    def preparer_noeuds(G, positions, noeuds_optimaux, mois) -> tuple:
        noeuds_x, noeuds_y, noeuds_texte, noeuds_couleur = [], [], [], []

        for noeud in G.nodes:
            x, y = positions[noeud]
            indice_mois, effectif = noeud
            noeuds_x.append(x)
            noeuds_y.append(y)
            noeuds_texte.append(f"{mois[indice_mois]} | effectif={effectif}")
            noeuds_couleur.append("#e76f51" if noeud in noeuds_optimaux else "#2a9d8f")

        return noeuds_x, noeuds_y, noeuds_texte, noeuds_couleur

    def construire_figure_dag(
        arcs_normaux, arcs_optimaux_coords, noeuds, mois
    ) -> go.Figure:
        arcs_x_normaux, arcs_y_normaux = arcs_normaux
        arcs_x_optimaux, arcs_y_optimaux = arcs_optimaux_coords
        noeuds_x, noeuds_y, noeuds_texte, noeuds_couleur = noeuds

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=arcs_x_normaux,
                y=arcs_y_normaux,
                mode="lines",
                line=dict(color="rgba(120, 120, 120, 0.25)", width=1),
                hoverinfo="skip",
                name="Arcs faisables",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=arcs_x_optimaux,
                y=arcs_y_optimaux,
                mode="lines",
                line=dict(color="#e63946", width=3),
                hoverinfo="skip",
                name="Chemin optimal",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=noeuds_x,
                y=noeuds_y,
                mode="markers",
                marker=dict(size=8, color=noeuds_couleur),
                text=noeuds_texte,
                hovertemplate="%{text}<extra></extra>",
                name="Noeuds",
            )
        )
        fig.update_layout(
            title="DAG des transitions mensuelles",
            xaxis=dict(
                title="Mois",
                tickmode="array",
                tickvals=list(range(len(mois))),
                ticktext=mois,
            ),
            yaxis=dict(title="Effectif (axe inversé)", showgrid=True),
            template="plotly_white",
            height=620,
            legend=dict(orientation="h", y=1.02, x=0),
            margin=dict(l=40, r=20, t=70, b=40),
        )
        return fig

    return (
        calculer_positions,
        construire_figure_dag,
        preparer_noeuds,
        separer_arcs,
    )


@app.cell
def _(
    G,
    arcs_optimaux,
    calculer_positions,
    chemin_optimal,
    construire_figure_dag,
    mo,
    mois,
    preparer_noeuds,
    separer_arcs,
):
    noeuds_optimaux = set(chemin_optimal)
    positions = calculer_positions(G)

    arcs_normaux = separer_arcs(G, positions, arcs_optimaux)[:2]
    arcs_optimaux_coords = separer_arcs(G, positions, arcs_optimaux)[2:]
    noeuds = preparer_noeuds(G, positions, noeuds_optimaux, mois)

    fig_dag = construire_figure_dag(arcs_normaux, arcs_optimaux_coords, noeuds, mois)
    mo.ui.plotly(fig_dag)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Détail des arcs optimaux
    """)
    return


@app.function
def decrire_arc(noeud_source, noeud_dest, mois, G) -> dict:
    indice_mois_source, effectif_source = noeud_source
    indice_mois_dest, effectif_dest = noeud_dest
    return {
        "Depuis": f"{mois[indice_mois_source]} (effectif {effectif_source})",
        "Vers": f"{mois[indice_mois_dest]} (effectif {effectif_dest})",
        "Echanges": abs(effectif_dest - effectif_source),
        "Poids arc (EUR)": G.edges[noeud_source, noeud_dest]["poids"],
    }


@app.cell
def _(G, chemin_optimal, mo, mois, pd):
    df_arcs = pd.DataFrame(
        [
            decrire_arc(noeud_source, noeud_dest, mois, G)
            for noeud_source, noeud_dest in zip(chemin_optimal, chemin_optimal[1:])
        ]
    )

    mo.ui.table(df_arcs)
    return


if __name__ == "__main__":
    app.run()
