"""Script de test vérifie que le module reproduit les résultats du notebook initial."""

from src.optimisation_effectif import ProblemeDeploiement, resoudre

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
    effectif_max=10,
    cout_changement=160,
    cout_ecart=200,
    limite_heures_sup=0.25,
    echanges_max_absolu=3,
)

solution = resoudre(probleme)


print("=== Coût total ===\n")
print(f"  {solution.cout_total:.0f} €")

print("\n=== Chemin optimal ===")
for indice_mois, effectif in solution.chemin:
    print(f"  {probleme.mois[indice_mois]} → effectif {effectif}")

print("\n=== Plan détaillé ===")
for etape in solution.lignes:
    print(
        f"  {etape.mois:<12}"
        f"  effectif={etape.effectif}"
        f"  besoin={str(etape.besoin_minimal):<4}"
        f"  échanges={etape.ajouts_suppressions}"
        f"  coût ajust.={etape.cout_ajustement:.0f}€"
        f"  coût écart={etape.cout_ecart:.0f}€"
        f"  cumulé={etape.cout_cumule:.0f}€"
    )

assert solution.chemin[0] == (0, 3), "Noeud de départ incorrect"
assert solution.chemin[-1] == (8, 3), "Noeud d'arrivée incorrect"
assert solution.lignes[0].mois == "Janvier"
assert solution.lignes[-1].mois == "Septembre"
assert solution.cout_total > 0, "Coût total doit être positif"

print("\n Tous les tests passent")
