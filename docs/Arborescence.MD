Ce document propose une arborescence pour le projet

```
./
│
├── pyproject.toml
├── docs
├── notebooks
├── README.md
│
├── src/
│   └── optimisation_effectif/ (nom du module)
│       ├── README.md (propre à la librairie)
│       ├── __init__.py
│       ├── graphe.py
│       ├── solveur.py
│       └── rapport_visuel.py 
│
├── interfaces/ (on verra à la fin)
│   
│   
│
└── tests/
    ├── test_modele.py
    ├── test_graphe.py
    └── test_solveur.py
```