import pytest
import networkx as nx

from src.optimisation_effectif.models import ProblemeDeploiement
from src.optimisation_effectif.graph import (
    GrapheDeploiement,
    NOEUD_SOURCE,
    NOEUD_PUITS,
)


@pytest.fixture
def probleme_simple():
    return ProblemeDeploiement(
        effectif_initial=10,
        effectif_final=12,
        mois=["Janvier", "Février"],
        besoins={"Janvier": 10, "Février": 12},
        limite_heures_sup=0.5,
        cout_changement=100,
        cout_ecart=200,
        fraction_echanges_max=1.0,
        echanges_max_absolu=10,
    )

def test_initialisation_graphe(probleme_simple):
    """Vérifie que le graphe est bien un graphe orienté (DiGraph)."""
    graphe = GrapheDeploiement(probleme_simple)
    assert isinstance(graphe.G, nx.DiGraph)


def test_noeuds_virtuels_existent(probleme_simple):
    """Vérifie que les noeuds source et puits sont bien ajoutés."""
    graphe = GrapheDeploiement(probleme_simple)
    assert NOEUD_SOURCE in graphe.G
    assert NOEUD_PUITS in graphe.G


def test_noeud_initial_present(probleme_simple):
    """Vérifie que le noeud correspondant à l'effectif initial est présent."""
    graphe = GrapheDeploiement(probleme_simple)
    assert (0, probleme_simple.effectif_initial) in graphe.G


def test_noeud_final_present(probleme_simple):
    """Vérifie que le noeud correspondant à l'effectif final est présent."""
    graphe = GrapheDeploiement(probleme_simple)
    dernier = len(probleme_simple.mois) - 1
    assert (dernier, probleme_simple.effectif_final) in graphe.G


def test_attributs_noeuds(probleme_simple):
    """Vérifie que les attributs d'un noeud sont correctement stockés."""
    graphe = GrapheDeploiement(probleme_simple)
    data = graphe.G.nodes[(0, 10)]
    assert data["mois"] == "Janvier"
    assert data["effectif"] == 10
    assert "cout_ecart" in data


def test_aucun_arc_vers_noeud_inexistant(probleme_simple):
    """Vérifie qu'aucun arc ne pointe vers un noeud inexistant."""
    graphe = GrapheDeploiement(probleme_simple)
    for _, dest in graphe.G.edges:
        assert dest in graphe.G.nodes


def test_arcs_mois_consecutifs(probleme_simple):
    """Vérifie que les arcs relient uniquement des mois consécutifs."""
    graphe = GrapheDeploiement(probleme_simple)
    for u, v in graphe.G.edges:
        if isinstance(u, tuple) and isinstance(v, tuple):
            assert v[0] == u[0] + 1


def test_arc_existe_si_valide(probleme_simple):
    """Vérifie qu'un arc existe entre deux noeuds valides si la transition est autorisée."""
    graphe = GrapheDeploiement(probleme_simple)
    if (0, 10) in graphe.G and (1, 12) in graphe.G:
        assert graphe.G.has_edge((0, 10), (1, 12))


def test_source_connectee(probleme_simple):
    """Vérifie que le noeud source est connecté à au moins un noeud du premier mois."""
    graphe = GrapheDeploiement(probleme_simple)
    successeurs = list(graphe.G.successors(NOEUD_SOURCE))
    assert len(successeurs) > 0


def test_source_vers_noeud_initial(probleme_simple):
    """Vérifie que la source est reliée au noeud initial quand il est valide."""
    graphe = GrapheDeploiement(probleme_simple)

    noeud = (0, probleme_simple.effectif_initial)
    if noeud in graphe.G:
        assert graphe.G.has_edge(NOEUD_SOURCE, noeud)


def test_dernier_mois_vers_puits(probleme_simple):
    """Vérifie que le dernier mois est relié au noeud puits."""
    graphe = GrapheDeploiement(probleme_simple)
    dernier = len(probleme_simple.mois) - 1
    noeud = (dernier, probleme_simple.effectif_final)
    if noeud in graphe.G:
        assert graphe.G.has_edge(noeud, NOEUD_PUITS)


def test_calcul_poids_simple(probleme_simple):
    """Vérifie le calcul du poids d'un arc."""
    graphe = GrapheDeploiement(probleme_simple)
    if graphe.G.has_edge((0, 10), (1, 12)):
        data = graphe.G.edges[(0, 10), (1, 12)]
        assert data["echanges"] == 2
        assert data["poids"] == 200


def test_echanges_coherents(probleme_simple):
    """Vérifie que le nombre d'échanges correspond à la différence d'effectif."""
    graphe = GrapheDeploiement(probleme_simple)
    for (u, v, data) in graphe.G.edges(data=True):
        if isinstance(u, tuple) and isinstance(v, tuple):
            _, e1 = u
            _, e2 = v
            assert data["echanges"] == abs(e2 - e1)


def test_attributs_arcs(probleme_simple):
    """Vérifie que chaque arc possède les attributs 'poids' et 'echanges'."""
    graphe = GrapheDeploiement(probleme_simple)
    for _, _, data in graphe.G.edges(data=True):
        assert "poids" in data
        assert "echanges" in data


def test_pas_d_arcs_si_echange_interdit(probleme_simple):
    """Vérifie qu'aucun arc métier n'est créé si les échanges sont interdits."""
    probleme_simple.echanges_max_absolu = 0
    graphe = GrapheDeploiement(probleme_simple)
    arcs_metier = [
        (u, v) for u, v in graphe.G.edges
        if isinstance(u, tuple) and isinstance(v, tuple)
    ]
    assert len(arcs_metier) == 0


def test_graphe_sans_solution_depuis_source(probleme_simple):
    """Vérifie qu'aucun chemin n'est possible si le premier mois est invalide."""
    probleme_simple.besoins["Janvier"] = 100
    probleme_simple.limite_heures_sup = 0.01
    graphe = GrapheDeploiement(probleme_simple)
    successeurs = list(graphe.G.successors(NOEUD_SOURCE))
    assert len(successeurs) == 0