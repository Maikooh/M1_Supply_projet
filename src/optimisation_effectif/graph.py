"""Description.

Module implémentant la construction du graphe orienté acyclique (DAG) pour
le problème de déploiement d'effectifs."""

import networkx as nx

from .costs import (
    calculer_cout_ecart,
    ecart_est_valide,
    echange_autorise,
    est_effectif_valide,
)
from .models import ProblemeDeploiement

# Identifiants des noeuds utilisés quand effectif_initial/final est libre
NOEUD_SOURCE = "__source__"
NOEUD_PUITS = "__puits__"


class GrapheDeploiement:
    """Construit le DAG du problème de déploiement d'effectifs.

    Chaque nœud ``(indice_mois, effectif)`` représente un effectif possible
    pour un mois donné. Un arc relie deux nœuds consécutifs si la variation
    d'effectif est autorisée. Deux nœuds virtuels ``NOEUD_SOURCE`` et
    ``NOEUD_PUITS`` encadrent le graphe pour permettre l'algorithme de
    plus court chemin quel que soit l'effectif initial ou final.

    Avant la construction on vérifie que :

    - les nœuds dont l'écart dépasse ``limite_heures_sup`` sont exclus
    - les nœuds aux bornes incompatibles avec ``effectif_initial`` ou
      ``effectif_final`` sont exclus
    - les arcs dont la variation dépasse ``echanges_max_absolu`` sont exclus

    Exemples :

    >>> from optimisation_effectif.models import ProblemeDeploiement
    >>> p = ProblemeDeploiement(
    ...     mois=["Jan", "Fev"], besoins={},
    ...     effectif_initial=2, effectif_final=2,
    ...     cout_changement=100, cout_ecart=200,
    ...     limite_heures_sup=0.25, echanges_max_absolu=1,
    ... )
    >>> g = GrapheDeploiement(p)
    >>> (0, 2) in g.G
    True
    >>> (0, 5) in g.G
    False
    """

    def __init__(self, probleme: ProblemeDeploiement) -> None:
        """Initialise et construit le graphe complet.

        Args:
            probleme (ProblemeDeploiement): Le problème de déploiement à modéliser.
        """
        self.probleme = probleme
        self.G = nx.DiGraph()
        self._ajouter_noeuds()
        self._ajouter_arcs()
        self._ajouter_noeuds_virtuels()

    @property
    def effectif_max_safe(self) -> int:
        """Retourne effectif_max en garantissant qu'il n'est pas None.

        Raises:
            ValueError: Si effectif_max est None.
        """
        if self.probleme.effectif_max is None:
            raise ValueError(
                "effectif_max ne peut pas être None lors de la construction du graphe."
            )
        return self.probleme.effectif_max

    def _ajouter_noeuds(self) -> None:
        """Ajoute les noeuds valides au graphe."""
        for indice_mois, nom_mois in enumerate(self.probleme.mois):
            for effectif in range(self.effectif_max_safe + 1):
                if not est_effectif_valide(indice_mois, effectif, self.probleme):
                    continue
                if not ecart_est_valide(nom_mois, effectif, self.probleme):
                    continue
                cout, surnumeraires, manquants = calculer_cout_ecart(
                    nom_mois, effectif, self.probleme
                )
                self.G.add_node(
                    (indice_mois, effectif),
                    mois=nom_mois,
                    effectif=effectif,
                    cout_ecart=cout,
                    surnumeraires=surnumeraires,
                    manquants=manquants,
                )

    def _ajouter_arcs(self) -> None:
        """Ajoute les arcs valides entre noeuds consécutifs."""
        for indice_mois in range(len(self.probleme.mois) - 1):
            for effectif_actuel in range(self.effectif_max_safe + 1):
                source = (indice_mois, effectif_actuel)
                if source not in self.G:
                    continue
                self._ajouter_arcs_depuis(source)

    def _ajouter_arcs_depuis(self, source: tuple[int, int]) -> None:
        """Ajoute tous les arcs valides depuis un noeud source donné.

        Args:
            source (tuple[int, int]): Nœud de départ encodé comme
                ``(indice_mois, effectif)``.
        """
        indice_mois, effectif_actuel = source

        for effectif_suivant in range(self.effectif_max_safe + 1):
            destination = (indice_mois + 1, effectif_suivant)

            if destination not in self.G:
                continue
            if not echange_autorise(effectif_actuel, effectif_suivant, self.probleme):
                continue

            echanges = abs(effectif_suivant - effectif_actuel)
            poids = (
                self.probleme.cout_changement * echanges
                + self.G.nodes[destination]["cout_ecart"]
            )
            self.G.add_edge(source, destination, poids=poids, echanges=echanges)

    def _ajouter_noeuds_virtuels(self) -> None:
        """Ajoute systématiquement les nœuds source et puits.

        Quand effectif_initial est fixé, une seule arête source → (0, effectif_initial)
        est créée avec poids=cout_ecart du nœud de départ, de sorte que le poids total
        du chemin calculé par Bellman-Ford inclut toujours le coût du premier nœud.
        Quand effectif_initial est None, une arête est créée vers chaque nœud valide
        du premier mois. La même logique s'applique symétriquement au nœud puits.
        """
        self.G.add_node(NOEUD_SOURCE)
        if self.probleme.effectif_initial is not None:
            noeud = (0, self.probleme.effectif_initial)
            if noeud in self.G:
                self.G.add_edge(
                    NOEUD_SOURCE,
                    noeud,
                    poids=self.G.nodes[noeud]["cout_ecart"],
                    echanges=0,
                )
        else:
            for effectif in range(self.effectif_max_safe + 1):
                noeud = (0, effectif)
                if noeud in self.G:
                    self.G.add_edge(
                        NOEUD_SOURCE,
                        noeud,
                        poids=self.G.nodes[noeud]["cout_ecart"],
                        echanges=0,
                    )

        self.G.add_node(NOEUD_PUITS)
        dernier = len(self.probleme.mois) - 1
        if self.probleme.effectif_final is not None:
            noeud = (dernier, self.probleme.effectif_final)
            if noeud in self.G:
                self.G.add_edge(noeud, NOEUD_PUITS, poids=0, echanges=0)
        else:
            for effectif in range(self.effectif_max_safe + 1):
                noeud = (dernier, effectif)
                if noeud in self.G:
                    self.G.add_edge(noeud, NOEUD_PUITS, poids=0, echanges=0)
