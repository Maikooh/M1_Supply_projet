# optimisation-effectif

**Planification optimale des effectifs par plus court chemin dans un graphe acyclique.**

[![Python](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![Pydantic](https://img.shields.io/badge/pydantic-v2-orange)](https://docs.pydantic.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)](https://fastapi.tiangolo.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## Le problème

Toute organisation confrontée à une demande variable dans le temps doit ajuster ses effectifs de façon dynamique : trop de personnel engendre des surcoûts, pas assez dégrade la qualité de service. Les décisions d'embauche et de licenciement ont elles-mêmes un coût, ce qui rend le problème non trivial.

**`optimisation-effectif`** résout ce problème de planification multi-périodes de manière exacte, pour n'importe quel horizon temporel et n'importe quelle structure de coûts.

---

## Méthode

Le problème est modélisé comme un **graphe orienté acyclique (DAG)** :

- chaque nœud `(période, effectif)` représente un état possible,
- chaque arc pondéré représente une transition d'une période à la suivante,
- le **plus court chemin** (Bellman-Ford via NetworkX) retourne le plan de coût minimal.

Cette approche garantit l'**optimalité globale** de la solution, contrairement aux heuristiques greedy, et reste **polynomiale** pour des horizons de taille raisonnable.

---

## Démonstration

![Démonstration](.img/demonstration.gif)
---

## Installation

```bash
pip install optimisation-effectif
```

Ou depuis les sources :

```bash
git clone <url-du-repo>
cd optimisation-effectif
uv sync
```

---

## Utilisation

### Python

```python
from optimisation_effectif import ProblemeDeploiement, resoudre

probleme = ProblemeDeploiement(
    mois=["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin",
          "Juillet", "Aout", "Septembre"],
    besoins={"Mars": 4, "Avril": 6, "Mai": 7, "Juin": 4, "Juillet": 6, "Aout": 2},
    effectif_initial=3,
    effectif_final=3,
    effectif_max=30,
    cout_changement=160,
    cout_ecart=200,
    limite_heures_sup=0.25,
    echanges_max_absolu=3,
    fraction_echanges_max=1 / 3,
)

solution = resoudre(probleme)
print(solution.cout_total)   # 2160.0
```

### CLI

```bash
# Générer un fichier JSON exemple
python -m optimisation_effectif.interfaces demo

# Visualiser le problème
python -m optimisation_effectif.interfaces view demonstration.json

# Résoudre
python -m optimisation_effectif.interfaces solve demonstration.json
```

### API REST

```bash
python -m optimisation_effectif.api
```

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/deploiement/demo` | Retourne le problème exemple |
| `POST` | `/deploiement/resoudre` | Résout un problème, retourne la solution |
| `GET` | `/docs` | Swagger UI interactif |

```bash
curl -X POST http://127.0.0.1:8000/deploiement/resoudre \
  -H "Content-Type: application/json" \
  -d @demonstration.json
```

---

## Structure

```
optimisation_effectif/
├── models.py        # Modèles Pydantic — ProblemeDeploiement, SolutionDeploiement
├── costs.py         # Calcul des coûts et validations
├── graph.py         # Construction du DAG (NetworkX)
├── solver.py        # Résolution par Bellman-Ford
├── interfaces/      # CLI Typer + Rich
└── api/             # API FastAPI
```
---

## Licence

MIT
