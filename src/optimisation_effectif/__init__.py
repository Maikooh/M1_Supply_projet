"""Module de résolution de problèmes de déploiement optimal de personnel.

Utilisation typique :

    from optimisation_effectif import ProblemeDeploiement, resoudre

    probleme = ProblemeDeploiement(
        mois=["Janvier", "Fevrier", "Mars", ...],
        besoins={"Mars": 4, "Avril": 6, ...},
        effectif_initial=3,
        effectif_final=3,
        effectif_max=10,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=3,
    )

    solution = resoudre(probleme)
    print(solution.cout_total)
"""

from .models import EtapeDeploiement, ProblemeDeploiement, SolutionDeploiement
from .solver import resoudre

__all__ = [
    "ProblemeDeploiement",
    "SolutionDeploiement",
    "EtapeDeploiement",
    "resoudre",
]
