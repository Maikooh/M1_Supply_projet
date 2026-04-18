"""Description.
Ce fichier encode les données utilisées."""

from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, Field, NonNegativeFloat, NonNegativeInt, model_validator


class ProblemeDeploiement(BaseModel):
    """Modèle de données pour le problème de déploiement.

    Exemple d'utilisation::

        probleme = ProblemeDeploiement(
            mois=["Janvier", "Fevrier", "Mars"],
            besoins={"Mars": 4},
            effectif_initial=3,
            effectif_final=3,
            effectif_max=10,
            cout_changement=160,
            cout_ecart=200,
            limite_heures_sup=0.25,
            echanges_max_absolu=3,
        )
    """

    mois: list[str]
    besoins: dict[str, NonNegativeInt]

    effectif_initial: NonNegativeInt
    effectif_final: NonNegativeInt
    effectif_max: NonNegativeInt

    cout_changement: NonNegativeFloat
    cout_ecart: NonNegativeFloat

    limite_heures_sup: Annotated[NonNegativeFloat, Field(lt=1.0)]
    echanges_max_absolu: NonNegativeInt

    @model_validator(mode="after")
    def verifier_coherence(self):
        for mois in self.besoins:
            if mois not in self.mois:
                raise ValueError(f"'{mois}' dans besoins est absent de la liste mois")

        if self.effectif_initial > self.effectif_max:
            raise ValueError(
                "L'effectif initial ne peut pas être supérieur à l'effectif maximum"
            )
        if self.effectif_final > self.effectif_max:
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


@dataclass
class SolutionDeploiement:
    chemin: list[tuple[int, int]]
    cout_total: NonNegativeFloat
    lignes: list[EtapeDeploiement]
