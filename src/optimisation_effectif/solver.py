import networkx as nx

from .graph import NOEUD_PUITS, NOEUD_SOURCE, GrapheDeploiement
from .models import EtapeDeploiement, ProblemeDeploiement, SolutionDeploiement

# Un nœud est soit un tuple (indice_mois, effectif), soit un identifiant virtuel (str)
Node = tuple[int, int] | str


def _trouver_chemin(
    graph: nx.DiGraph,
    probleme: ProblemeDeploiement,
) -> tuple[list[Node], float]:
    """Trouve le chemin de coût minimal dans le DAG via Bellman-Ford.

    Utilise les noeuds source/puits quand effectif_initial ou
    effectif_final est None, permettant au solveur de choisir librement
    l'effectif optimal de départ et/ou d'arrivée.
    """
    noeud_depart = (
        NOEUD_SOURCE
        if probleme.effectif_initial is None
        else (0, probleme.effectif_initial)
    )
    noeud_arrivee = (
        NOEUD_PUITS
        if probleme.effectif_final is None
        else (len(probleme.mois) - 1, probleme.effectif_final)
    )

    if noeud_depart not in graph or noeud_arrivee not in graph:
        raise ValueError(
            f"Le noeud de départ {noeud_depart} ou d'arrivée "
            f"{noeud_arrivee} est manquant dans le graphe."
        )

    try:
        chemin = nx.bellman_ford_path(
            graph, noeud_depart, noeud_arrivee, weight="poids"
        )
        cout_total = nx.path_weight(graph, chemin, weight="poids")
    except nx.NetworkXNoPath:
        debut = (
            "libre"
            if probleme.effectif_initial is None
            else str(probleme.effectif_initial)
        )
        fin = (
            "libre" if probleme.effectif_final is None else str(probleme.effectif_final)
        )
        fraction = (
            f"{probleme.fraction_echanges_max:.0%}"
            if probleme.fraction_echanges_max is not None
            else "non définie"
        )
        raise ValueError(
            f"Aucune solution trouvée avec les paramètres fournis.\n"
            f"Effectif initial : {debut}\n"
            f"Effectif final   : {fin}\n"
            f"Echanges max     : {probleme.echanges_max_absolu} ou "
            f"{fraction} de l'effectif\n"
            f"Essayez d'ajuster vos paramètres pour trouver une solution réalisable."
        ) from None

    return chemin, cout_total


def _construire_plan(
    graph: nx.DiGraph,
    chemin: list[tuple[int, int]],
    probleme: ProblemeDeploiement,
) -> list[EtapeDeploiement]:
    """Construit le plan détaillé mois par mois à partir du chemin optimal."""
    etapes = []
    cumul = 0.0

    for indice_etape, noeud in enumerate(chemin):
        indice_mois, effectif = noeud
        nom_mois = probleme.mois[indice_mois]
        donnees_noeud = graph.nodes[noeud]

        effectif_precedent = (
            chemin[indice_etape - 1][1] if indice_etape > 0 else effectif
        )
        nb_echanges = abs(effectif - effectif_precedent)

        cout_ajustement = float(probleme.cout_changement * nb_echanges)
        cumul += cout_ajustement + donnees_noeud["cout_ecart"]

        etapes.append(
            EtapeDeploiement(
                mois=nom_mois,
                effectif=effectif,
                besoin_minimal=probleme.besoins.get(nom_mois),
                ajouts_suppressions=nb_echanges,
                cout_ajustement=cout_ajustement,
                surnumeraires=donnees_noeud["surnumeraires"],
                manquants=donnees_noeud["manquants"],
                cout_ecart=donnees_noeud["cout_ecart"],
                cout_cumule=cumul,
            )
        )

    return etapes


def resoudre(probleme: ProblemeDeploiement) -> SolutionDeploiement:
    """Résout le problème de déploiement optimal de personnel.

    Construit le DAG, trouve le chemin de coût minimal via Bellman-Ford
    et retourne la solution complète.

    Si effectif_initial ou effectif_final est None, le solveur choisit
    automatiquement l'effectif optimal pour minimiser le coût total.
    """
    graph = GrapheDeploiement(probleme).G
    chemin_brut, cout_total = _trouver_chemin(graph, probleme)

    debut_libre = probleme.effectif_initial is None
    fin_libre = probleme.effectif_final is None

    chemin_trimmed: list[Node] = chemin_brut[1:] if debut_libre else chemin_brut
    chemin_trimmed = chemin_trimmed[:-1] if fin_libre else chemin_trimmed
    chemin: list[tuple[int, int]] = chemin_trimmed  # type: ignore[assignment]

    etapes = _construire_plan(graph, chemin, probleme)
    cout_total = etapes[-1].cout_cumule if etapes else 0.0

    return SolutionDeploiement(
        chemin=chemin,
        cout_total=cout_total,
        lignes=etapes,
    )
