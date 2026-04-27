"""Description.

Module implémentant la résolution du problème de déploiement d'effectifs
par recherche du plus court chemin dans le DAG via l'algorithme de Bellman-Ford."""

from typing import cast

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

    Utilise systématiquement les nœuds source/puits, dont les arêtes
    encapsulent le coût du premier nœud (poids=cout_ecart), garantissant
    que path_weight reflète le coût total sans correctif conditionnel.

    Args:
        graph (nx.DiGraph): Le graphe de déploiement avec nœuds source et puits.
        probleme (ProblemeDeploiement): Le problème de déploiement.

    Returns:
        tuple[list[Node], float]: Le chemin optimal et son coût total.
    """
    if NOEUD_SOURCE not in graph or NOEUD_PUITS not in graph:
        raise ValueError(
            "Les nœuds virtuels source/puits sont manquants dans le graphe."
        )

    try:
        chemin = nx.bellman_ford_path(graph, NOEUD_SOURCE, NOEUD_PUITS, weight="poids")
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
    """Construit le plan détaillé mois par mois à partir du chemin optimal.

    Args:
        graph (nx.DiGraph): Le graphe contenant les données des nœuds.
        chemin (list[tuple[int, int]]): Séquence de nœuds du chemin optimal,
            sans les nœuds virtuels source et puits.
        probleme (ProblemeDeploiement): Le problème de déploiement.

    Returns:
        list[EtapeDeploiement]: Les étapes détaillées mois par mois.
    """
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
    et retourne la solution complète avec le détail mois par mois.

    Si ``effectif_initial`` ou ``effectif_final`` est ``None``, le solveur
    choisit automatiquement l'effectif optimal pour minimiser le coût total.

    Args:
        probleme (ProblemeDeploiement): Le problème de déploiement à résoudre.

    Returns:
        SolutionDeploiement: La solution optimale avec chemin, coût total
            et détail mois par mois.

    Avant de retourner on vérifie que :

    - le DAG contient au moins un chemin admissible entre source et puits

    Exemples :

    >>> from optimisation_effectif.models import ProblemeDeploiement
    >>> p = ProblemeDeploiement(
    ...     mois=["Jan"],
    ...     besoins={"Jan": 4},
    ...     effectif_initial=0,
    ...     effectif_final=0,
    ...     cout_changement=100,
    ...     cout_ecart=200,
    ...     limite_heures_sup=0.0,
    ...     echanges_max_absolu=0,
    ... )
    >>> resoudre(p)
    Traceback (most recent call last):
        ...
    ValueError: Aucune solution trouvée avec les paramètres fournis. ...
    """
    graph = GrapheDeploiement(probleme).G
    chemin_brut, cout_total = _trouver_chemin(graph, probleme)

    # chemin_brut commence toujours par NOEUD_SOURCE et finit par NOEUD_PUITS
    chemin = cast(list[tuple[int, int]], chemin_brut[1:-1])

    etapes = _construire_plan(graph, chemin, probleme)

    return SolutionDeploiement(
        chemin=chemin,
        cout_total=cout_total,
        lignes=etapes,
    )
