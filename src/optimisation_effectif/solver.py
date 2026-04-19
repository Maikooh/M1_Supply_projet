import networkx as nx

from .graph import GrapheDeploiement
from .models import EtapeDeploiement, ProblemeDeploiement, SolutionDeploiement


def _trouver_chemin(
    graph: nx.DiGraph,
    probleme: ProblemeDeploiement,
) -> tuple[list[tuple[int, int]], float]:
    """Trouve le chemin de coût minimal dans le DAG via Bellman-Ford."""
    noeud_depart = (0, probleme.effectif_initial)
    noeud_arrivee = (len(probleme.mois) - 1, probleme.effectif_final)

    if noeud_depart not in graph or noeud_arrivee not in graph:
        msg = (
            f"Le noeud de départ {noeud_depart} ou d'arrivée "
            f"{noeud_arrivee} est manquant dans le graphe."
        )
        raise ValueError(msg)

    chemin = nx.bellman_ford_path(graph, noeud_depart, noeud_arrivee, weight="poids")
    cout_total = nx.path_weight(graph, chemin, weight="poids")

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
    et retourne la solution complète."""

    graph = GrapheDeploiement(probleme).G
    chemin, cout_total = _trouver_chemin(graph, probleme)
    etapes = _construire_plan(graph, chemin, probleme)

    return SolutionDeploiement(
        chemin=chemin,
        cout_total=cout_total,
        lignes=etapes,
    )
