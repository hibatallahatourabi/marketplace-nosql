
# Search Design — Marketplace NoSQL

## 1. Objectif

Ce module permet de rechercher les produits dans MongoDB
selon plusieurs critères et de calculer des facettes.

Les tests utilisent la catégorie "All Beauty".

## 2. Modèle des produits

La collection `products` respecte le schéma commun :

- `product_id` : String
- `title` : String
- `brand` : String
- `category.main` : String
- `category.path` : Array[String]
- `price` : Decimal128
- `rating.average` : Number
- `rating.count` : Number

Le modèle peut également contenir les champs `features`,
`description`, `attributes`, `images` et `source`.

## 3. Recherche multicritère

Fichier : `search/product_search.py`

Fonction : `search_products()`

Critères disponibles :

- Marque : `brand`
- Prix minimum : `price >= min_price`
- Prix maximum : `price <= max_price`
- Note minimale : `rating.average >= min_rating`
- Catégorie principale : `category.main`
- Sous-catégorie : `category.path`

Les prix sont convertis en Decimal128 avant la recherche.

Exemple :

```python
results = search_products(
    min_price=80,
    max_price=130,
    min_rating=4.0,
    category="All Beauty",
    subcategory="Hair Care"
)
```

Résultat sur les données de test :

- B001 : Hair Chalk Pink
- B002 : Hair Shampoo

## 4. Recherche à facettes

Fichier : `search/facet_search.py`

Fonction : `facet_search()`

L'opérateur MongoDB `$facet` calcule simultanément :

- Le nombre de produits par marque
- Le nombre de produits par tranche de prix
- Le nombre de produits par intervalle de notes

Sur les trois produits de test :

| Facette | Résultat |
|---|---|
| Marques | CeraVe : 1, ColorPop : 1, L'Oreal : 1 |
| Prix [0,100[ | 1 |
| Prix [100,200[ | 2 |
| Notes [4,5[ | 3 |

## 5. Index MongoDB

Fichier : `search/search_indexes.py`

Index créés dans `products` :

- `idx_brand`
- `idx_price`
- `idx_rating`
- `idx_category_main`
- `idx_category_path`
- `idx_category_price_rating`

L'index `idx_category_path` est multikey,
car `category.path` est un tableau.

## 6. Benchmark

Fichier : `benchmarks/search_benchmark.py`

La comparaison utilise `explain()` avec
`executionStats` et deux stratégies :

- Avec index : `IXSCAN` + `FETCH`
- Sans index : `COLLSCAN`

Résultats sur trois produits :

| Indicateur | Avec index | Sans index |
|---|---|---|
| Documents retournés | 3 | 3 |
| Documents examinés | 3 | 3 |
| Clés examinées | 3 | 0 |
| Temps affiché | 0 ms | 0 ms |

Ces résultats confirment l'utilisation de l'index,
mais ne démontrent pas de gain de performance
sur un aussi petit ensemble de données.

## 7. Tests

Fichier : `tests/test_search.py`

Cinq tests vérifient :

1. Recherche par catégorie
2. Recherche par marque
3. Recherche par prix et note
4. Type Decimal128 du prix
5. Recherche à facettes

Les cinq tests ont réussi avec Pytest.

## 8. Limites

Les tests actuels utilisent trois produits fictifs.

Les performances devront être réévaluées avec un
volume plus important de produits réels issus
du dataset Amazon Reviews 2023.
### Validation globale

La suite complète des tests du module Search & Categories
a été exécutée avec la commande :

python -m pytest tests/ -v

Résultat : 16 tests réussis en 1.08 seconde.

Les tests couvrent également :
- La gestion des catégories hiérarchiques
- La compatibilité du schéma des produits
- Les recherches avec des valeurs manquantes
- Les facettes avec des valeurs manquantes
