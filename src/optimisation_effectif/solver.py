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
        raise ValueError(
            f"Aucune solution trouvée avec les paramètres fournis.\n"
            f"Effectif initial : {probleme.effectif_initial}\n"
            f"Effectif final   : {probleme.effectif_final}\n"
            f"Echanges max     : {probleme.echanges_max_absolu} ou "
            f"{probleme.fraction_echanges_max:.0%} de l'effectif\n"
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
                limite_heures_sup=probleme.limite_heures_sup
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

if __name__ == "__main__":
    # 1. Créer un problème de test
    test_prob = ProblemeDeploiement(
        mois=["Janvier", "Fevrier"],
        besoins={"Janvier": 5, "Fevrier": 8},
        effectif_initial=5,
        effectif_final=5,
        cout_changement=100.0,
        cout_ecart=200.0,
        echanges_max_absolu=3
    )
    
    # 2. Tenter de résoudre
    try:
        sol = resoudre(test_prob)
        print(f"Succès ! Coût total : {sol.cout_total}")
        for ligne in sol.lignes:
            print(f"Mois: {ligne.mois}, Effectif: {ligne.effectif}")
    except Exception as e:
        print(f"Erreur lors de la résolution : {e}")