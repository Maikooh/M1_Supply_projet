"""Description.

Module implémentant les fonctions de calcul des coûts pour le problème
de déploiement d'effectifs."""

import math

from .models import ProblemeDeploiement


def ecart_est_valide(
    mois_nom: str, effectif: int, probleme: ProblemeDeploiement
) -> bool:
    """Vérifie si l'effectif est admissible pour le mois donné.

    Retourne ``True`` si le mois n'a pas de besoin défini, ou si le nombre
    de manquants est inférieur ou égal à ``limite_heures_sup * besoin``.

    Args:
        mois_nom (str): Nom du mois à évaluer.
        effectif (int): Effectif déployé pour ce mois.
        probleme (ProblemeDeploiement): Le problème de déploiement.

    Returns:
        bool: ``True`` si l'écart est admissible, ``False`` sinon.

    Exemples :

    >>> from optimisation_effectif.models import ProblemeDeploiement
    >>> p = ProblemeDeploiement(
    ...     mois=["Jan"], besoins={"Jan": 4},
    ...     cout_changement=100, cout_ecart=200,
    ...     limite_heures_sup=0.25, echanges_max_absolu=2,
    ... )
    >>> ecart_est_valide("Jan", 3, p)
    True
    >>> ecart_est_valide("Jan", 2, p)
    False
    >>> ecart_est_valide("Fev", 2, p)
    True
    """
    besoin = probleme.besoins.get(mois_nom)
    if besoin is None:
        return True

    manquants = max(besoin - effectif, 0)
    limite_heures_sup = probleme.limite_heures_sup
    if limite_heures_sup is None:
        raise ValueError("limite_heures_sup ne peut pas être None.")

    return manquants <= limite_heures_sup * besoin


def calculer_cout_ecart(
    mois_nom: str, effectif: int, probleme: ProblemeDeploiement
) -> tuple[float, int, int]:
    """Calcule le coût d'écart et les effectifs surnuméraires/manquants.

    Retourne un triplet ``(cout, surnumeraires, manquants)``. Si le mois n'a
    pas de besoin défini, retourne ``(0.0, 0, 0)``.

    Args:
        mois_nom (str): Nom du mois à évaluer.
        effectif (int): Effectif déployé pour ce mois.
        probleme (ProblemeDeploiement): Le problème de déploiement.

    Returns:
        tuple[float, int, int]: Triplet (coût d'écart, surnuméraires, manquants).

    Avant le calcul on vérifie que :

    - l'écart est admissible (cf. ``ecart_est_valide``)

    Exemples :

    >>> from optimisation_effectif.models import ProblemeDeploiement
    >>> p = ProblemeDeploiement(
    ...     mois=["Jan"], besoins={"Jan": 4},
    ...     cout_changement=100, cout_ecart=200,
    ...     limite_heures_sup=0.25, echanges_max_absolu=2,
    ... )
    >>> calculer_cout_ecart("Jan", 5, p)
    (200.0, 1, 0)
    >>> calculer_cout_ecart("Jan", 2, p)
    Traceback (most recent call last):
        ...
    ValueError: Mois 'Jan' : effectif 2 dépasse la limite d'heures supplémentaires
    """
    besoin = probleme.besoins.get(mois_nom)
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
    """Vérifie si la variation d'effectif entre deux mois est autorisée.

    Le nombre d'échanges est borné par ``echanges_max_absolu`` et, si définie,
    par ``fraction_echanges_max * effectif_actuel`` (le minimum des deux s'applique).

    Args:
        effectif_actuel (int): Effectif du mois courant.
        effectif_suivant (int): Effectif du mois suivant.
        probleme (ProblemeDeploiement): Le problème de déploiement.

    Returns:
        bool: ``True`` si la variation est autorisée, ``False`` sinon.

    Exemples :

    >>> from optimisation_effectif.models import ProblemeDeploiement
    >>> p = ProblemeDeploiement(
    ...     mois=["Jan", "Fev"], besoins={},
    ...     cout_changement=100, cout_ecart=200,
    ...     limite_heures_sup=0.25, echanges_max_absolu=2,
    ... )
    >>> echange_autorise(5, 7, p)
    True
    >>> echange_autorise(5, 8, p)
    False
    """
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
    """Vérifie que l'effectif respecte les contraintes de début et de fin.

    Au premier mois, si ``effectif_initial`` est défini, l'effectif doit
    lui être égal. Au dernier mois, la même logique s'applique pour
    ``effectif_final``. Pour les mois intermédiaires, retourne toujours ``True``.

    Args:
        indice_mois (int): Indice du mois dans la liste des mois.
        effectif (int): Effectif à valider.
        probleme (ProblemeDeploiement): Le problème de déploiement.

    Returns:
        bool: ``True`` si l'effectif est valide pour ce mois, ``False`` sinon.

    Exemples :

    >>> from optimisation_effectif.models import ProblemeDeploiement
    >>> p = ProblemeDeploiement(
    ...     mois=["Jan", "Fev"], besoins={},
    ...     effectif_initial=3,
    ...     cout_changement=100, cout_ecart=200,
    ...     limite_heures_sup=0.25, echanges_max_absolu=2,
    ... )
    >>> est_effectif_valide(0, 3, p)
    True
    >>> est_effectif_valide(0, 5, p)
    False
    >>> est_effectif_valide(1, 5, p)
    True
    """
    if indice_mois == 0 and probleme.effectif_initial is not None:
        return effectif == probleme.effectif_initial
    if indice_mois == len(probleme.mois) - 1 and probleme.effectif_final is not None:
        return effectif == probleme.effectif_final
    return True
