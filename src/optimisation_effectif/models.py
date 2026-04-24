"""Description.
Ce fichier encode les données utilisées."""

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
    model_config = ConfigDict(extra="forbid", strict=True)
    """Modèle de données pour le problème de déploiement.

    Exemple d'utilisation::

        probleme = ProblemeDeploiement(
            mois=["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin"],
            besoins={"Mars": 4, "Avril": 6, "Mai": 7, "Juin": 4, "Juillet": 6},
            effectif_initial=3,
            effectif_final=3,
            effectif_max=10,
            cout_changement=160,
            cout_ecart=200,
            limite_heures_sup=0.25,
            echanges_max_absolu=3,
            fraction_echanges_max=0.3,
        )
    """

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
    chemin: list[tuple[int, int]]
    cout_total: NonNegativeFloat
    lignes: list[EtapeDeploiement]
