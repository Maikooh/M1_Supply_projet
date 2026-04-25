"""Description.
Ce fichier contient les fonctions de calcul
des coûts pour le problème de déploiement."""

import math

from .models import ProblemeDeploiement


def ecart_est_valide(
    mois_nom: str, effectif: int, probleme: ProblemeDeploiement
) -> bool:
    besoin = probleme.besoins.get(mois_nom.capitalize())
    if besoin is None:
        return True

    manquants = max(besoin - effectif, 0)
    return manquants <= probleme.limite_heures_sup * besoin


def calculer_cout_ecart(
    mois_nom: str, effectif: int, probleme: ProblemeDeploiement
) -> tuple[float, int, int]:
    besoin = probleme.besoins.get(mois_nom.capitalize())
    if besoin is None:
        return 0.0, 0, 0

    if not ecart_est_valide(mois_nom, effectif, probleme):
        msg = (
            f"Mois '{mois_nom}' : effectif {effectif} "
            "dépasse la limite d'heures supplémentaires"
        )
        raise ValueError(msg)

    surnumeraires = max(effectif - besoin, 0)
    manquants = max(besoin - effectif, 0)
    cout = probleme.cout_ecart * (surnumeraires + manquants)
    return float(cout), surnumeraires, manquants


def echange_autorise(
    effectif_actuel: int, effectif_suivant: int, probleme: ProblemeDeploiement
) -> bool:
    echanges = abs(effectif_suivant - effectif_actuel)

    if probleme.fraction_echanges_max is None:
        echanges_max = probleme.echanges_max_absolu
    else:
        echanges_max_fraction = math.floor(
            probleme.fraction_echanges_max * effectif_actuel + 1e-9
        )
        echanges_max = min(probleme.echanges_max_absolu, echanges_max_fraction)

    return echanges <= echanges_max


def est_effectif_valide(
    indice_mois: int, effectif: int, probleme: ProblemeDeploiement
) -> bool:
    if indice_mois == 0 and probleme.effectif_initial is not None:
        return effectif == probleme.effectif_initial
    if indice_mois == len(probleme.mois) - 1 and probleme.effectif_final is not None:
        return effectif == probleme.effectif_final
    return True
