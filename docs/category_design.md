
# Category Design — Marketplace NoSQL

## 1. Objectif

Ce module permet de représenter la hiérarchie des
catégories et de rechercher les produits appartenant
à une catégorie ou à ses descendants.

## 2. Hiérarchie de test

All Beauty
├── Hair Care
│   ├── Hair Chalk
│   └── Shampoo
└── Skin Care
    └── Moisturizers

Six catégories sont enregistrées dans la collection
`categories`.

## 3. Modèle parent_id

Chaque catégorie possède un champ `parent_id`
qui référence sa catégorie parente directe.

Exemple :

```json
{
  "category_id": "hair_chalk",
  "name": "Hair Chalk",
  "parent_id": "hair_care"
}
```

Avantage :
- Simple à maintenir pour les relations directes.

Limite :
- La recherche de tous les descendants nécessite
  une navigation récursive ou une opération `$graphLookup`.

## 4. Modèle ancestors

Chaque catégorie possède un tableau `ancestors`
contenant les identifiants de tous ses ancêtres.

Exemple :

```json
{
  "category_id": "hair_chalk",
  "name": "Hair Chalk",
  "ancestors": ["beauty", "hair_care"]
}
```

Avantage :
- Recherche de tous les descendants avec une requête simple.

Limite :
- Un déplacement de catégorie peut nécessiter
  la mise à jour des tableaux `ancestors` de ses descendants.

## 5. Compatibilité avec products

La collection `products` utilise les noms de catégories :

```json
{
  "category": {
    "main": "All Beauty",
    "path": [
      "All Beauty",
      "Hair Care",
      "Hair Chalk"
    ]
  }
}
```

Les identifiants internes de `categories` ne sont
pas stockés dans le champ `category.path`.

## 6. Requêtes hiérarchiques

Fichier : `search/category_queries.py`

Fonctions :

- `get_direct_subcategories()`
- `get_all_descendants()`
- `get_products_in_hierarchy()`

Résultats des tests :

Sous-catégories directes de Beauty :
- Hair Care
- Skin Care

Descendants de Beauty :
- Hair Care
- Hair Chalk
- Shampoo
- Skin Care
- Moisturizers

Produits de Hair Care :
- B001 : Hair Chalk Pink
- B002 : Hair Shampoo

## 7. Index

Collection `categories` :

- `category_id_1` : index unique
- `idx_parent_id` : recherche des enfants directs
- `idx_ancestors` : recherche des descendants

Collection `products` :

- `idx_category_main`
- `idx_category_path`

## 8. Comparaison des modèles

| Critère | parent_id | ancestors |
|---|---|---|
| Parent direct | Simple | Moins direct |
| Tous les descendants | Récursion / graphLookup | Requête directe |
| Stockage | Plus faible | Plus élevé |
| Déplacement d'une branche | Plus simple | Mises à jour multiples |

## 9. Tests

Fichier : `tests/test_categories.py`

Cinq tests vérifient :

1. Sous-catégories directes
2. Tous les descendants
3. Produits de Hair Care
4. Catégorie inexistante
5. Cohérence des relations parent / ancêtres

Les cinq tests ont réussi avec Pytest.

## 10. Limites

La hiérarchie actuelle est une hiérarchie fictive
utilisée pour valider les requêtes.

La correspondance entre les noms de `category.path`
et les catégories enregistrées doit être maintenue.

Des tests complémentaires seront nécessaires
avec la hiérarchie réelle du dataset Amazon Reviews 2023.
