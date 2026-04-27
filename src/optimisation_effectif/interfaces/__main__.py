"""Description.

Interface typer pour le déploiement optimal d'effectifs.
"""

import sys

from rich import print
from rich.table import Table
from typer import Typer

from ..models import EtapeDeploiement, ProblemeDeploiement, SolutionDeploiement
from ..solver import resoudre

app = Typer()


def _probleme_to_table(probleme: ProblemeDeploiement) -> Table:
    """Convertit un ProblemeDeploiement en une table Rich.

    Args:
        probleme (ProblemeDeploiement): Le problème de déploiement à afficher.

    Returns:
        Table: La table Rich correspondant au problème.
    """
    table = Table(title="Problème de déploiement")
    table.add_column("Mois")
    table.add_column("Besoin minimal", justify="right")
    for mois in probleme.mois:
        besoin = probleme.besoins.get(mois)
        table.add_row(mois, str(besoin) if besoin is not None else "-")
    return table


def _etape_to_row(etape: EtapeDeploiement) -> tuple[str, ...]:
    """Convertit une EtapeDeploiement en ligne de table Rich.

    Args:
        etape (EtapeDeploiement): L'étape à convertir.

    Returns:
        tuple[str, ...]: Les valeurs de la ligne dans l'ordre des colonnes.
    """
    besoin = str(etape.besoin_minimal) if etape.besoin_minimal is not None else "-"
    return (
        etape.mois,
        str(etape.effectif),
        besoin,
        str(etape.ajouts_suppressions),
        str(etape.surnumeraires),
        str(etape.manquants),
        f"{etape.cout_ajustement:.0f}",
        f"{etape.cout_ecart:.0f}",
        f"{etape.cout_cumule:.0f}",
    )


def _solution_to_table(solution: SolutionDeploiement) -> Table:
    """Convertit une SolutionDeploiement en une table Rich.

    Args:
        solution (SolutionDeploiement): La solution à afficher.

    Returns:
        Table: La table Rich correspondant à la solution.
    """
    table = Table(title=f"Solution — coût total : {solution.cout_total:.0f} €")
    table.add_column("Mois")
    table.add_column("Effectif", justify="right")
    table.add_column("Besoin", justify="right")
    table.add_column("+/-", justify="right")
    table.add_column("Surnum.", justify="right")
    table.add_column("Manquants", justify="right")
    table.add_column("Coût ajust.", justify="right")
    table.add_column("Coût écart", justify="right")
    table.add_column("Coût cumulé", justify="right")
    for etape in solution.lignes:
        table.add_row(*_etape_to_row(etape))
    return table


@app.command()
def demo():
    """Génère un fichier demonstration.json contenant un problème exemple."""
    probleme = ProblemeDeploiement(
        mois=[
            "Janvier",
            "Fevrier",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Aout",
            "Septembre",
        ],
        besoins={
            "Mars": 4,
            "Avril": 6,
            "Mai": 7,
            "Juin": 4,
            "Juillet": 6,
            "Aout": 2,
        },
        effectif_initial=3,
        effectif_final=3,
        effectif_max=30,
        cout_changement=160,
        cout_ecart=200,
        limite_heures_sup=0.25,
        echanges_max_absolu=3,
        fraction_echanges_max=1 / 3,
    )
    with open("demonstration.json", "w") as fichier:
        fichier.write(probleme.model_dump_json(indent=2))


@app.command()
def view(chemin: str):
    """Visualise un fichier JSON encodant un problème de déploiement."""
    with open(chemin) as fichier:
        donnees = fichier.read()
    try:
        probleme = ProblemeDeploiement.model_validate_json(donnees)
    except Exception as err:
        print(err)
        sys.exit(1)
    print(_probleme_to_table(probleme))


@app.command()
def solve(chemin: str):
    """Résout un problème de déploiement à partir du fichier JSON indiqué."""
    with open(chemin) as fichier:
        donnees = fichier.read()
    try:
        probleme = ProblemeDeploiement.model_validate_json(donnees)
    except Exception as err:
        print(err)
        sys.exit(1)
    try:
        solution = resoudre(probleme)
    except ValueError as err:
        print(err)
        sys.exit(1)
    print(_solution_to_table(solution))


if __name__ == "__main__":
    app()
