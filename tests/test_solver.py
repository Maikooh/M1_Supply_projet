"""Description.

Tests unitaires du module solver.
"""

import networkx as nx
import pytest

from src.optimisation_effectif.models import ProblemeDeploiement, SolutionDeploiement
from src.optimisation_effectif.solver import _trouver_chemin, resoudre


def test_resolution_simple():
    """Un mois, effectif = besoin -> coût nul."""
    probleme = ProblemeDeploiement(
        mois=["Janvier"],
        besoins={"Janvier": 5},
        effectif_initial=5,
        effectif_final=5,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    solution = resoudre(probleme)
    assert solution.cout_total == 0.0
    assert solution.lignes[0].surnumeraires == 0
    assert solution.lignes[0].manquants == 0


def test_resolution_deux_mois_stable():
    """Deux mois avec le meme effectif -> pas d'échange et coût nul."""
    probleme = ProblemeDeploiement(
        mois=["Janvier", "Février"],
        besoins={"Janvier": 5, "Février": 5},
        effectif_initial=5,
        effectif_final=5,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    solution = resoudre(probleme)
    assert solution.cout_total == 0.0
    assert solution.chemin == [(0, 5), (1, 5)]


def test_resolution_retourne_solution_deploiement():
    """resoudre retourne bien une instance de SolutionDeploiement."""
    probleme = ProblemeDeploiement(
        mois=["Janvier"],
        besoins={"Janvier": 5},
        effectif_initial=5,
        effectif_final=5,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    assert isinstance(resoudre(probleme), SolutionDeploiement)


# structure


def test_nombre_etapes_egal_nombre_mois():
    """contient autant d'étapes que de mois."""
    probleme = ProblemeDeploiement(
        mois=["Janvier", "Février", "Mars"],
        besoins={"Janvier": 5, "Février": 5, "Mars": 5},
        effectif_initial=5,
        effectif_final=5,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    solution = resoudre(probleme)
    assert len(solution.lignes) == len(probleme.mois)


def test_chemin_debut_et_fin_corrects():
    """Le chemin commence à l'effectif initial et se termine à l'effectif final."""
    probleme = ProblemeDeploiement(
        mois=["Janvier", "Février"],
        besoins={"Janvier": 5, "Février": 7},
        effectif_initial=5,
        effectif_final=7,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    solution = resoudre(probleme)
    assert solution.chemin[0] == (0, probleme.effectif_initial)
    assert solution.chemin[-1] == (len(probleme.mois) - 1, probleme.effectif_final)


# calcul des coûts


def test_cout_surnumeraires():
    """Surnumeraires en mois 2 : cout = cout_ecart * surnumeraires."""
    # effectif=5, besoin=3 donc 2 surnuméraires : 200 * 2 = 400
    probleme = ProblemeDeploiement(
        mois=["Janvier", "Février"],
        besoins={"Janvier": 5, "Février": 3},
        effectif_initial=5,
        effectif_final=5,
        cout_changement=0,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    solution = resoudre(probleme)
    assert solution.lignes[1].surnumeraires == 2
    assert solution.lignes[1].cout_ecart == 400.0
    assert solution.cout_total == 400.0


def test_cout_changement_pris_en_compte():
    """Le changement d'effectif génère un coût = cout_changement * nombre d'échanges."""
    probleme = ProblemeDeploiement(
        mois=["Janvier", "Février"],
        besoins={"Janvier": 5, "Février": 7},
        effectif_initial=5,
        effectif_final=7,
        cout_changement=100,
        cout_ecart=0,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    solution = resoudre(probleme)
    assert solution.lignes[1].ajouts_suppressions == 2
    assert solution.lignes[1].cout_ajustement == 200.0
    assert solution.cout_total == 200.0


def test_cout_cumule_croissant():
    """Le coût cumulé est croissant ou égal d'un mois à l'autre."""
    probleme = ProblemeDeploiement(
        mois=["Janvier", "Février", "Mars"],
        besoins={"Janvier": 5, "Février": 3, "Mars": 3},
        effectif_initial=5,
        effectif_final=5,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    solution = resoudre(probleme)
    cumuls = [etape.cout_cumule for etape in solution.lignes]
    assert all(cumuls[i] <= cumuls[i + 1] for i in range(len(cumuls) - 1))


def test_cout_total_egal_dernier_cout_cumule():
    """cout_total == cout_cumule final."""
    probleme = ProblemeDeploiement(
        mois=["Janvier", "Février"],
        besoins={"Janvier": 5, "Février": 5},
        effectif_initial=5,
        effectif_final=5,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    solution = resoudre(probleme)
    assert solution.cout_total == solution.lignes[-1].cout_cumule


# cas erreurs


def test_resolution_impossible_leve_exception():
    """Aucun chemin possible renvoie ValueError explicite."""
    probleme = ProblemeDeploiement(
        mois=["Janvier", "Février"],
        besoins={"Janvier": 5, "Février": 7},
        effectif_initial=5,
        effectif_final=7,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=0,
        fraction_echanges_max=0.0,
    )
    with pytest.raises(ValueError, match="Aucune solution trouvée"):
        resoudre(probleme)


def test_trouver_chemin_noeud_absent_leve_exception():
    """trouver_chemin lève ValueError si le graph ne contient pas le départ."""
    probleme = ProblemeDeploiement(
        mois=["Janvier"],
        besoins={"Janvier": 5},
        effectif_initial=5,
        effectif_final=5,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=5,
        fraction_echanges_max=0.5,
    )
    graphe_vide = nx.DiGraph()
    with pytest.raises(ValueError, match="manquant dans le graphe"):
        _trouver_chemin(graphe_vide, probleme)
