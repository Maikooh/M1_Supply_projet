"""Description.
Ce fichier contient la logique de construction du graphe de déploiement."""

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
    """Construit le DAG du problème de déploiement."""

    def __init__(self, probleme: ProblemeDeploiement) -> None:
        self.probleme = probleme
        self.G = nx.DiGraph()
        self._ajouter_noeuds()
        self._ajouter_arcs()
        self._ajouter_noeuds_virtuels()

    def _ajouter_noeuds(self) -> None:
        """Ajoute les noeuds valides au graphe."""
        for indice_mois, nom_mois in enumerate(self.probleme.mois):
            for effectif in range(self.probleme.effectif_max + 1):
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
            for effectif_actuel in range(self.probleme.effectif_max + 1):
                source = (indice_mois, effectif_actuel)
                if source not in self.G:
                    continue
                self._ajouter_arcs_depuis(source)

    def _ajouter_arcs_depuis(self, source: tuple[int, int]) -> None:
        """Ajoute tous les arcs valides depuis un noeud source donné."""
        indice_mois, effectif_actuel = source

        for effectif_suivant in range(self.probleme.effectif_max + 1):
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
        """Ajoute source/puits quand effectif_initial ou effectif_final est libre."""
        if self.probleme.effectif_initial is None:
            self.G.add_node(NOEUD_SOURCE)
            for effectif in range(self.probleme.effectif_max + 1):
                noeud = (0, effectif)
                if noeud in self.G:
                    self.G.add_edge(
                        NOEUD_SOURCE,
                        noeud,
                        poids=self.G.nodes[noeud]["cout_ecart"],
                        echanges=0,
                    )

        if self.probleme.effectif_final is None:
            self.G.add_node(NOEUD_PUITS)
            dernier = len(self.probleme.mois) - 1
            for effectif in range(self.probleme.effectif_max + 1):
                noeud = (dernier, effectif)
                if noeud in self.G:
                    self.G.add_edge(noeud, NOEUD_PUITS, poids=0, echanges=0)
