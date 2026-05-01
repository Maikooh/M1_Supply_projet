"""Description.

Module de tests unitaires pour models.py
"""

import pytest
from pydantic import ValidationError

from src.optimisation_effectif.models import (
    EtapeDeploiement,
    ProblemeDeploiement,
    SolutionDeploiement,
)


def _etape(
    effectif, manquants=0, surnumeraires=0, besoin_minimal=None, limite_heures_sup=None
):
    """Crée une EtapeDeploiement minimale pour les tests."""
    return EtapeDeploiement(
        mois="Mars",
        effectif=effectif,
        besoin_minimal=besoin_minimal,
        ajouts_suppressions=0,
        cout_ajustement=0.0,
        surnumeraires=surnumeraires,
        manquants=manquants,
        cout_ecart=0.0,
        cout_cumule=0.0,
        limite_heures_sup=limite_heures_sup,
    )


def _probleme(**kwargs):
    """Crée un ProblemeDeploiement minimal pour les tests."""
    base = dict(
        mois=["Mars", "Avril"],
        besoins={"Mars": 4, "Avril": 6},
        effectif_initial=3,
        effectif_final=3,
        effectif_max=10,
        cout_changement=160.0,
        cout_ecart=200.0,
        limite_heures_sup=0.25,
        echanges_max_absolu=3,
    )
    base.update(kwargs)
    return ProblemeDeploiement(**base)  # type: ignore


def test_mois_absent_dans_besoins():
    """Un mois présent dans besoins mais absent de mois → erreur."""
    with pytest.raises(ValueError, match="absent de la liste mois"):
        _probleme(besoins={"Juillet": 4})


def test_effectif_initial_superieur_au_max():
    """effectif_initial > effectif_max → erreur."""
    with pytest.raises(ValueError, match="effectif initial"):
        _probleme(effectif_initial=15, effectif_max=10)


def test_effectif_final_superieur_au_max():
    """effectif_final > effectif_max → erreur."""
    with pytest.raises(ValueError, match="effectif final"):
        _probleme(effectif_final=15, effectif_max=10)


def test_effectif_max_calcule_automatiquement():
    """effectif_max à None → calculé comme max(initial, final, max(besoins))."""
    probleme = _probleme(effectif_max=None)
    assert probleme.effectif_max == max(3, 3, 6)


def test_effectif_max_calcule_avec_initial_dominant():
    """Vérifie que effectif_max prend l'initial s'il est le plus grand."""
    # initial=20, final=10, max besoins=6 -> effectif_max doit être 20
    probleme = _probleme(effectif_initial=20, effectif_final=10, effectif_max=None)
    assert probleme.effectif_max == 20


def test_effectif_max_calcule_avec_final_dominant():
    """Vérifie que effectif_max prend le final s'il est le plus grand."""
    # initial=5, final=15, max besoins=6 -> effectif_max doit être 15
    probleme = _probleme(effectif_initial=5, effectif_final=15, effectif_max=None)
    assert probleme.effectif_max == 15


def test_etape_valide():
    """Création d'une étape valide sans erreur."""
    etape = _etape(effectif=4)
    assert etape.mois == "Mars"


def test_surnumeraires_et_manquants_simultanement():
    """surnumeraires et manquants positifs en même temps → erreur."""
    with pytest.raises(ValueError, match="simultanément positifs"):
        _etape(effectif=4, manquants=1, surnumeraires=2, besoin_minimal=6)


def test_manquants_sans_besoin_defini():
    """manquants non nul sans besoin_minimal défini → erreur."""
    with pytest.raises(ValueError, match="écart non nul sans besoin défini"):
        EtapeDeploiement(
            mois="Mars",
            effectif=4,
            besoin_minimal=None,
            ajouts_suppressions=0,
            cout_ajustement=0.0,
            surnumeraires=0,
            manquants=2,
            cout_ecart=0.0,
            cout_cumule=0.0,
        )


def test_manquants_apres_heures_sup_sans_limite():
    """Sans limite définie, retourne les manquants bruts."""
    etape = _etape(effectif=4, manquants=3, besoin_minimal=7)
    assert etape.manquants_apres_heures_sup == 3


def test_manquants_apres_heures_sup_sans_manquants():
    """Sans manquants, retourne 0 peu importe la limite."""
    etape = _etape(effectif=4, manquants=0, limite_heures_sup=0.25)
    assert etape.manquants_apres_heures_sup == 0


def test_manquants_apres_heures_sup_partiellement_couverts():
    """Les heures sup couvrent une partie des manquants."""
    # 4 * 0.25 = 1 couvert → 3 - 1 = 2 restants
    etape = _etape(effectif=4, manquants=3, besoin_minimal=7, limite_heures_sup=0.25)
    assert etape.manquants_apres_heures_sup == 2


def test_manquants_apres_heures_sup_totalement_couverts():
    """Les heures sup couvrent tous les manquants."""
    # 4 * 0.25 = 1 couvert → 1 - 1 = 0 restants
    etape = _etape(effectif=4, manquants=1, besoin_minimal=5, limite_heures_sup=0.25)
    assert etape.manquants_apres_heures_sup == 0


def test_manquants_apres_heures_sup_jamais_negatif():
    """Le résultat ne peut pas être négatif."""
    # 8 * 0.25 = 2 couverts → 1 - 2 = 0 (pas -1)
    etape = _etape(effectif=8, manquants=1, besoin_minimal=9, limite_heures_sup=0.25)
    assert etape.manquants_apres_heures_sup == 0


def test_solution_valide():
    """Création d'une solution valide avec une étape."""
    etape = _etape(effectif=4)
    solution = SolutionDeploiement(
        chemin=[(0, 1)],
        cout_total=160.0,
        lignes=[etape],
    )
    assert solution.cout_total == 160.0
    assert len(solution.lignes) == 1
    assert solution.chemin == [(0, 1)]


def test_solution_cout_total_negatif_invalide():
    """Un coût total négatif doit être refusé."""
    etape = _etape(effectif=4)
    with pytest.raises(ValidationError):
        SolutionDeploiement(
            chemin=[(0, 1)],
            cout_total=-1.0,
            lignes=[etape],
        )


def test_solution_chemin_tuple_invalide():
    """Chaque élément de chemin doit être un tuple de 2 entiers."""
    etape = _etape(effectif=4)
    with pytest.raises(ValidationError):
        SolutionDeploiement(
            chemin=[(0, 1, 2)],  # type: ignore
            cout_total=10.0,
            lignes=[etape],
        )


def test_solution_lignes_type_invalide():
    """Les lignes doivent contenir des EtapeDeploiement valides."""
    with pytest.raises(ValidationError):
        SolutionDeploiement(
            chemin=[(0, 1)],
            cout_total=10.0,
            lignes=["etape_invalide"],  # type: ignore
        )


def test_creation_sans_besoin():
    """Vérifie qu'on peut créer un problème sans besoins (dict vide)."""
    probleme = _probleme(besoins={}, effectif_initial=5, effectif_max=None)
    assert probleme.besoins == {}
    assert probleme.effectif_max == 5


def test_limite_heures_sup_invalide():
    """Vérifie que Pydantic bloque une limite d'heures sup >= 1."""
    with pytest.raises(ValidationError):
        _probleme(limite_heures_sup=1.5)
