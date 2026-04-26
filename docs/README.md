Ce Projet met en place le [sujet 10](https://github.com/MECEN-TOURS/SC-2025-2026/tree/main/projets/10)

---
# Installation

```bash
git clone <url-du-repo>
cd <nom-du-repo>
```

---
# Environnement de développement

Le projet utilise **uv** pour la gestion des dépendances.

```bash
uv sync --group dev
```

---
# Exécution

Exemple avec un script Python :

```bash
uv run main.py
```

Si vous utilisez un notebook **marimo** :

```bash
uv run marimo edit notebook.py
```

---
# Qualité de code

Essayez d’utiliser du type hinting autant que possible pour garder un code clair et facile à maintenir.

Le projet utilise **pre-commit** (RUFF) pour le linting et le formatage.

>**Note** : ça peut bloquer vos commits pour non respect de la qualité du code parfois ça fixe auto parfois non dans les 2 cas il faudra refaire le commit après avoir fait les modifications nécessaires.

Si besoin (**se fait auto à chaque commit**) :

Lancer manuellement les vérifications 
```bash
uv run pre-commit run --all-files
```



---
# Workflow Git
## Principe

* La branche principale de développement est : `main`
* Les contributions passent par des Pull Requests (PR)

---
## Étape 1 : créer une branche

Depuis la branche `main` à jour :

```bash
git checkout main
git pull
```

Créer une branche selon le type de travail :

```bash
git checkout -b feature/nom_de_la_feature
git checkout -b fix/nom_du_probleme
git checkout -b docs/nom_de_la_doc
git checkout -b tests/nom_du_test
```

---

## Étape 2 : commit & push

```bash
git add .
git commit -m "message clair et concis"
git push -u origin <nom_de_la_branche>
```

---
## Étape 3 : Pull Request

* Ouvrir une PR vers `main`
* Ajouter une description claire
* Demander une review
* **Prévenir l’équipe**

---

## Étape 4 : merge

* Attendre validation (au moins 1 personne du groupe)
* Corriger si nécessaire
* Merge dans `main`

---
# Bonnes pratiques

* Faire des commits petits et fréquents
* Nommer les branches clairement
* Toujours pull avant de commencer
* Vérifier que le lint passe avant de push

---

# Structure du projet (exemple)

>Faire d'une manière logique
```
.
├── docs/
├── notebooks/
├── tests/
├── pyproject.toml
└── README.md
```

---