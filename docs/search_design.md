# Search Design — Marketplace NoSQL

## 1. Objectif

Ce module permet de rechercher les produits dans MongoDB selon plusieurs critères, de calculer des facettes et d'évaluer les performances des requêtes.

L'implémentation utilise directement **MongoDB Shell (`mongosh`)**, sans PyMongo.

## 2. Modèle des produits

La collection `products` contient les champs communs suivants :

- `product_id` : String
- `title` : String
- `brand` : String
- `category.main` : String
- `category.path` : Array[String]
- `price` : Decimal128
- `rating.average` : Number
- `rating.count` : Number

Des champs supplémentaires peuvent être présents selon les catégories : `features`, `description`, `attributes`, `images` et `source`.

## 3. Recherche multicritère

**Fichier :** `mongosh/search_products.js`

La recherche utilise `db.products.find()` et permet de filtrer les produits selon :

- La catégorie principale
- La sous-catégorie
- Le prix minimum et maximum
- La note minimale

Les comparaisons de prix utilisent `NumberDecimal()` pour respecter le type Decimal128.

**Résultats validés :**

- B001 : Hair Chalk Pink
- B002 : Hair Shampoo

## 4. Recherche à facettes

**Fichier :** `mongosh/facet_search.js`

L'agrégation MongoDB `$facet` permet de calculer simultanément :

- Le nombre de produits par marque
- Le nombre de produits par tranche de prix
- Le nombre de produits par intervalle de notes

**Résultats sur les trois produits de test :**

| Facette | Résultat |
|---|---|
| Marques | CeraVe : 1, ColorPop : 1, L'Oreal : 1 |
| Prix [50,100[ | 1 |
| Prix [100,200[ | 2 |
| Notes [4,5.01[ | 3 |

## 5. Index MongoDB

**Fichier :** `mongosh/search_indexes.js`

Les index sont créés avec `createIndex()`.

Index de la collection `products` :

- `idx_brand`
- `idx_price`
- `idx_rating`
- `idx_category_main`
- `idx_category_path`
- `idx_category_price_rating`

L'index sur `category.path` est multikey, car ce champ contient un tableau.

La collection `categories` utilise également des index sur `category_id`, `parent_id` et `ancestors`.

## 6. Benchmark

**Fichier :** `mongosh/search_benchmark.js`

La comparaison utilise `explain("executionStats")` avec deux stratégies :

- Avec index composé : recherche indexée.
- Sans index : parcours complet de la collection (`COLLSCAN`).

**Résultats mesurés :**

| Indicateur | Avec index | Sans index |
|---|---:|---:|
| Produits retournés | 2 | 2 |
| Documents examinés | 2 | 3 |
| Clés examinées | 2 | 0 |
| Temps d'exécution | 0 ms | 0 ms |

L'index réduit le nombre de documents examinés. Toutefois, avec seulement trois produits, aucun gain de temps mesurable ne peut être démontré.

## 7. Exécution et validation

Les scripts sont exécutés avec MongoDB Shell depuis la racine du projet.

Exemple :

```powershell
mongosh "mongodb://localhost:27017/marketplace_db" --file mongosh/search_products.js
```

Les scripts suivants ont été exécutés avec succès :

- `mongosh/search_products.js`
- `mongosh/facet_search.js`
- `mongosh/category_hierarchy.js`
- `mongosh/search_indexes.js`
- `mongosh/search_benchmark.js`

Les vérifications ont été effectuées sur une base locale contenant trois produits et six catégories.

## 8. Limites

Les données actuelles sont fictives et servent uniquement à valider les requêtes MongoDB.

Les performances devront être réévaluées sur un volume plus important de produits provenant du dataset Amazon Reviews 2023.

La compatibilité avec les données réelles du catalogue commun devra également être vérifiée avant l'intégration finale.