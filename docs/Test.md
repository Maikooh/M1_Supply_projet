# Tests et couverture de code

Ce projet utilise `pytest` pour les tests et `pytest-cov` pour mesurer la couverture de code.

## Lancer les tests avec couverture

```bash
uv sync --group dev
uv run python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

## Résultats

* Un résumé de la couverture s’affiche dans le terminal
* Un rapport HTML détaillé est généré dans le dossier `htmlcov/` (gitignore auto)

## Ouvrir le rapport HTML

Sur Windows :

```bash
start htmlcov/index.html
```

## Interprétation

* `Stmts` : nombre total de lignes de code
* `Miss` : lignes non couvertes par les tests
* `Cover` : pourcentage de couverture
* `Missing` : lignes à tester en priorité

