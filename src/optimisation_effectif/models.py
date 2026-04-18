"""Description.
Ce fichier encode les données utilisées."""

from pydantic import BaseModel, NonNegativeInt, NonNegativeFloat, model_validator, Field
from typing import Annotated
from dataclasses import dataclass

class ProblemeDeploiement(BaseModel):
    """Modèle de données pour le problème de déploiement.
    
    Exemple d'utilisation: 
    
    donnee_exemple = ProblemeDeploiement(
    mois=["Janvier", "Fevrier", "Mars", ...],
    besoins={"Mars": 4, "Avril": 6, "Mai": 7, ...},
    effectif_initial=3,
    effectif_final=3,
    effectif_max=10,
    cout_changement=160,
    cout_ecart=200,
    limite_heures_sup=0.25,
    echanges_max_absolu=3,
)"""
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
            raise ValueError("L'effectif initial ne peut pas être supérieur à l'effectif maximum")
        if self.effectif_final > self.effectif_max:
            raise ValueError("L'effectif final ne peut pas être supérieur à l'effectif maximum")
        return self
    
