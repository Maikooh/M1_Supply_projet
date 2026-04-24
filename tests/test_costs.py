import pytest
from src.optimisation_effectif.costs import (
    ecart_est_valide, 
    calculer_cout_ecart, 
    echange_autorise, 
    est_effectif_valide)
from src.optimisation_effectif.models import ProblemeDeploiement

@pytest.fixture
def probleme_test():
    """Crée un objet de déploiement type pour les tests."""
    return ProblemeDeploiement(
        effectif_initial=10,
        effectif_final=10,
        mois=["Janvier", "Février"],
        besoins={"Janvier": 10, "Février": 20},
        limite_heures_sup=0.25,
        cout_changement=160,
        cout_ecart=200,
        fraction_echanges_max=0.2,
        echanges_max_absolu=5,
    )


def test_ecart_est_impossible(probleme_test):
    """ Vérifie que la fonction renvoie False pour un effectif impossible."""
    assert ecart_est_valide("Février", 10, probleme_test) is False

def test_calculer_cout_ecart_trop_de_manque_plante(probleme_test):
    """ Vérifie que le calcul echoue si le manque de personnel dépasse la limite."""
    with pytest.raises(ValueError, match="dépasse la limite d'heures supplémentaires"):
        calculer_cout_ecart("Février", 10, probleme_test)

def test_calculer_mois_inconnu_ne_plante_pas(probleme_test):
    """ Vérifie que si le mois n'existe pas, la fonction ne plante pas. """
    cout, sur, manq = calculer_cout_ecart("fevrier", 10, probleme_test)
    assert cout == 0.0

def test_ecart_est_valide_mois_inconnu(probleme_test):
    """Vérifie le comportement de validation pour un mois inexistant."""
    assert ecart_est_valide("fevrier", 10, probleme_test) is True

def test_echange_est_impossible(probleme_test):
    """Vérifie qu'un changement d'effectif trop important est refusé."""
    assert echange_autorise(10, 15, probleme_test) is False

def test_echange_autorise_succes(probleme_test):
    """Vérifie qu'un changement d'effectif raisonnable est accepté."""
    assert echange_autorise(10, 11, probleme_test) is True

def test_est_effectif_valide_initial_incorrect(probleme_test):
    """Vérifie que l'effectif du premier mois doit correspondre à l'effectif initial."""
    assert est_effectif_valide(0, 15, probleme_test) is False

def test_est_effectif_valide_final_incorrect(probleme_test):
    """Vérifie que l'effectif du dernier mois doit correspondre à l'effectif final."""
    dernier_mois_idx = len(probleme_test.mois) - 1
    assert est_effectif_valide(dernier_mois_idx, 15, probleme_test) is False

def test_calcul_cout_parfait(probleme_test):
    """Vérifie que le coût est 0 quand l'effectif correspond exactement au besoin."""
    cout, sur, manq = calculer_cout_ecart("Janvier", 10, probleme_test)
    assert cout == pytest.approx(0.0)
    assert sur == 0
    assert manq == 0

def test_calcul_cout_surplus(probleme_test):
    """Vérifie le calcul quand l'effectif est supérieur au besoin."""
    cout, sur, manq = calculer_cout_ecart("Janvier", 12, probleme_test)
    assert cout == pytest.approx(400.0)
    assert sur == 2
    assert manq == 0

def test_calculer_cout_limite_exacte_heures_sup(probleme_test):
    """Vérifie le cas où le manque est exactement égal à la limite autorisée."""
    cout, sur, manq = calculer_cout_ecart("Février", 15, probleme_test)
    assert cout == pytest.approx(1000.0)
    assert sur == 0
    assert manq == 5
