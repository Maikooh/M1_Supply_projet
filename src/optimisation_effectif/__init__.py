"""Description.

Module de résolution de problèmes de déploiement optimal de personnel.

Expose les trois modèles de données (``ProblemeDeploiement``,
``SolutionDeploiement``, ``EtapeDeploiement``) ainsi que la fonction
``resoudre`` qui calcule la planification de coût minimal.

Exemples :

>>> from optimisation_effectif import ProblemeDeploiement, resoudre
>>> probleme = ProblemeDeploiement(
...     mois=["Janvier", "Fevrier", "Mars"],
...     besoins={"Mars": 4},
...     effectif_initial=3,
...     effectif_final=3,
...     cout_changement=160,
...     cout_ecart=200,
...     limite_heures_sup=0.25,
...     echanges_max_absolu=3,
... )
>>> solution = resoudre(probleme)
>>> solution.cout_total
200.0
"""

from .models import EtapeDeploiement, ProblemeDeploiement, SolutionDeploiement
from .solver import resoudre

__all__ = [
    "ProblemeDeploiement",
    "SolutionDeploiement",
    "EtapeDeploiement",
    "resoudre",
]
