"""Description.

Module implémentant les modèles de données pour le problème de déploiement
d'effectifs."""

from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    model_validator,
)


class ProblemeDeploiement(BaseModel):
    """Encode les données d'un problème de déploiement d'effectifs.

    Chaque mois de la liste ``mois`` peut avoir un besoin en personnel défini dans
    ``besoins``. Les coûts ``cout_changement`` et ``cout_ecart`` pénalisent
    respectivement les ajustements d'effectif et les écarts au besoin.

    Avant la création de l'objet on vérifie que :

    - chaque clé de ``besoins`` appartient à la liste ``mois``
    - ``effectif_initial`` et ``effectif_final`` sont inférieurs ou égaux à
      ``effectif_max``
    - si ``effectif_max`` est absent, il est déduit du maximum des valeurs
      disponibles (besoins, effectif_initial, effectif_final)

    Exemples :

    >>> ProblemeDeploiement(
    ...     mois=["Janvier"],
    ...     besoins={"Fevrier": 2},
    ...     effectif_initial=2,
    ...     cout_changement=100,
    ...     cout_ecart=150,
    ...     limite_heures_sup=0.25,
    ...     echanges_max_absolu=2,
    ... )
    Traceback (most recent call last):
        ...
    pydantic_core._pydantic_core.ValidationError: ...
      Value error, 'Fevrier' dans besoins est absent de la liste mois ...

    >>> ProblemeDeploiement(
    ...     mois=["Janvier"],
    ...     besoins={"Janvier": 2},
    ...     effectif_initial=5,
    ...     effectif_max=3,
    ...     cout_changement=100,
    ...     cout_ecart=150,
    ...     limite_heures_sup=0.25,
    ...     echanges_max_absolu=2,
    ... )
    Traceback (most recent call last):
        ...
    pydantic_core._pydantic_core.ValidationError: ...
      Value error, L'effectif initial ne peut pas être supérieur ...
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    mois: list[str]
    besoins: dict[str, NonNegativeInt]

    effectif_initial: NonNegativeInt | None = None
    effectif_final: NonNegativeInt | None = None
    effectif_max: NonNegativeInt | None = None

    cout_changement: NonNegativeFloat
    cout_ecart: NonNegativeFloat

    limite_heures_sup: Annotated[NonNegativeFloat, Field(lt=1.0)]
    echanges_max_absolu: NonNegativeInt
    fraction_echanges_max: float | None = None

    @model_validator(mode="after")
    def verifier_coherence(self):
        for mois in self.besoins:
            if mois not in self.mois:
                raise ValueError(f"'{mois}' dans besoins est absent de la liste mois")

        if self.effectif_max is None:
            candidats = list(self.besoins.values())
            if self.effectif_initial is not None:
                candidats.append(self.effectif_initial)
            if self.effectif_final is not None:
                candidats.append(self.effectif_final)
            if not candidats:
                raise ValueError(
                    "effectif_max doit être spécifié si besoins, "
                    "effectif_initial et effectif_final sont tous absents."
                )
            self.effectif_max = max(candidats)

        if (
            self.effectif_initial is not None
            and self.effectif_initial > self.effectif_max
        ):
            raise ValueError(
                "L'effectif initial ne peut pas être supérieur à l'effectif maximum"
            )
        if self.effectif_final is not None and self.effectif_final > self.effectif_max:
            raise ValueError(
                "L'effectif final ne peut pas être supérieur à l'effectif maximum"
            )

        return self


class EtapeDeploiement(BaseModel):
    """Encode l'état du déploiement pour un mois donné.

    Stocke l'effectif en place, le besoin minimal, les mouvements de personnel
    et les coûts associés pour une étape de la solution.

    Avant la création de l'objet on vérifie que :

    - ``surnumeraires`` et ``manquants`` ne sont pas simultanément positifs
    - si ``besoin_minimal`` est absent, l'écart est nul

    Exemples :

    >>> EtapeDeploiement(
    ...     mois="Janvier",
    ...     effectif=5,
    ...     besoin_minimal=3,
    ...     ajouts_suppressions=0,
    ...     cout_ajustement=0.0,
    ...     surnumeraires=1,
    ...     manquants=1,
    ...     cout_ecart=200.0,
    ...     cout_cumule=200.0,
    ... )
    Traceback (most recent call last):
        ...
    pydantic_core._pydantic_core.ValidationError: ...
      Value error, Mois 'Janvier' : surnuméraires et manquants ne peuvent ...
    """

    mois: str
    effectif: NonNegativeInt
    besoin_minimal: NonNegativeInt | None
    ajouts_suppressions: NonNegativeInt
    cout_ajustement: NonNegativeFloat
    surnumeraires: NonNegativeInt
    manquants: NonNegativeInt
    cout_ecart: NonNegativeFloat
    cout_cumule: NonNegativeFloat

    @model_validator(mode="after")
    def verifier_ecart(self):
        if self.surnumeraires > 0 and self.manquants > 0:
            raise ValueError(
                f"Mois '{self.mois}' : surnuméraires et manquants ne peuvent "
                f"pas être simultanément positifs"
            )
        if self.besoin_minimal is None and (
            self.surnumeraires > 0 or self.manquants > 0
        ):
            raise ValueError(f"Mois '{self.mois}' : écart non nul sans besoin défini")
        return self


class SolutionDeploiement(BaseModel):
    """Encode une solution complète du problème de déploiement.

    Contient le chemin optimal dans le graphe des effectifs, le coût total
    et le détail mois par mois sous forme d'étapes.
    """

    chemin: list[tuple[int, int]]
    cout_total: NonNegativeFloat
    lignes: list[EtapeDeploiement]
