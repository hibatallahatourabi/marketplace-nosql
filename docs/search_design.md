# Search Design — Marketplace NoSQL

## 1. Objectif

Le module Search & Categories permet de rechercher
des produits selon plusieurs critères, de calculer
des facettes et d'optimiser les requêtes MongoDB.

L'implémentation utilise MongoDB Shell (mongosh).

## 2. Modèle des produits

Le module respecte le schéma commun du catalogue :

- product_id : String
- title : String
- brand : String
- category.main : String
- category.path : Array[String]
- price : Decimal128 ou null
- rating.average : Number
- rating.count : Number

Exemple :

```json
{
  "product_id": "B0BWJGQ32Y",
  "brand": "Ebbfurln",
  "category": {
    "main": "All Beauty",
    "path": [
      "Beauty & Personal Care",
      "Hair Care",
      "Hair Extensions, Wigs & Accessories",
      "Wigs"
    ]
  },
  "price": {
    "$numberDecimal": "45.65"
  },
  "rating": {
    "average": 4.1,
    "count": 60
  }
}
```

Le schéma des produits existants n'est pas modifié.

## 3. Recherche multicritère

Fichier : `mongosh/search_products.js`

Les critères disponibles sont :

- Catégorie principale.
- Chemin hiérarchique.
- Marque.
- Prix minimum.
- Prix maximum.
- Note minimale.

Exemple de filtre MongoDB :

```javascript
{
  "category.main": "All Beauty",
  "category.path.0": "Beauty & Personal Care",
  "category.path.1": "Hair Care",
  price: {
    $type: "number",
    $gte: NumberDecimal("0"),
    $lte: NumberDecimal("100")
  },
  "rating.average": {
    $gte: 4
  }
}
```

Les positions du tableau category.path permettent
de respecter le chemin hiérarchique exact.

Les prix null, absents ou négatifs sont exclus
lorsqu'un filtre de prix positif est appliqué.

Les résultats sont triés par note décroissante,
puis par identifiant du produit.

## 4. Recherche à facettes

Fichier : `mongosh/facet_search.js`

La recherche à facettes utilise le pipeline
d'agrégation MongoDB et l'opérateur $facet.

Les facettes calculées sont :

- Marques et nombre de produits par marque.
- Intervalles de prix.
- Nombre de prix manquants.
- Intervalles de notes.

Les principaux opérateurs utilisés sont :

- $match : filtrage des documents.
- $group : regroupement par marque.
- $bucket : regroupement par intervalle.
- $count : comptage des documents.
- $sort : tri des résultats.
- $facet : calcul de plusieurs agrégations.
- $set : normalisation du résultat.

Les intervalles de prix sont :

- [0, 50[
- [50, 100[
- [100, 200[
- [200, 500[
- 500 et plus

Les produits sans prix restent comptabilisés
dans les facettes des marques et des notes
lorsque ces informations sont disponibles.

Les facettes actuelles sont calculées sur
l'ensemble de la collection products.

## 5. Stratégie d'indexation

Fichier : `mongosh/search_indexes.js`

| Index | Champs |
|---|---|
| idx_brand | brand |
| idx_price | price |
| idx_rating | rating.average |
| idx_category_main | category.main |
| idx_category_path | category.path |
| idx_category_price_rating | category.main, price, rating.average |

L'index sur category.path est un index multikey,
car ce champ contient un tableau.

L'index composé est défini comme suit :

```javascript
{
  "category.main": 1,
  price: 1,
  "rating.average": -1
}
```

Le script recherche les index compatibles avant
de créer de nouveaux index.

Les index existants du catalogue sont conservés,
notamment product_id_1, brand_1 et category.path_1.

## 6. Benchmark des performances

Fichiers :

- `mongosh/seed_benchmark.js`
- `mongosh/search_benchmark.js`

### 6.1 Données utilisées

Le benchmark utilise 10 000 produits synthétiques :

| Catégorie | Produits |
|---|---:|
| All Beauty | 6000 |
| Software | 2000 |
| Video Games | 2000 |
| Total | 10000 |

Le dataset contient 589 produits sans prix.

### 6.2 Méthodologie

La même requête est exécutée avec trois stratégies :

1. Plan choisi automatiquement par MongoDB.
2. Index composé imposé avec hint().
3. Parcours sans index avec hint({ $natural: 1 }).

Les statistiques sont obtenues avec :

```javascript
explain("executionStats")
```

Les indicateurs étudiés sont :

- executionTimeMillis
- totalDocsExamined
- totalKeysExamined
- nReturned

### 6.3 Résultats expérimentaux

Cinq exécutions après une première mesure initiale :

| Exécution | Automatique | Index imposé | Sans index |
|---|---:|---:|---:|
| 1 | 11 ms | 4 ms | 13 ms |
| 2 | 13 ms | 4 ms | 9 ms |
| 3 | 11 ms | 3 ms | 11 ms |
| 4 | 11 ms | 3 ms | 10 ms |
| 5 | 10 ms | 3 ms | 10 ms |
| Moyenne | 11.2 ms | 3.4 ms | 10.6 ms |
| Médiane | 11 ms | 3 ms | 10 ms |

| Indicateur | Automatique | Index imposé | Sans index |
|---|---:|---:|---:|
| Documents examinés | 328 | 328 | 10000 |
| Clés examinées | 1223 | 1223 | 0 |
| Produits retournés | 221 | 221 | 221 |

### 6.4 Analyse

L'index composé imposé permet :

- Une réduction du temps moyen de 67.92 %.
- Une accélération observée de 3.12 fois.
- Une réduction des documents examinés de 96.72 %.
- Une économie de 9672 documents examinés.

MongoDB sélectionne automatiquement le même
index composé pour cette requête.

Le plan avec index utilise IXSCAN, FETCH et SORT.

Le plan sans index utilise COLLSCAN et SORT.

Les chemins hiérarchiques sont vérifiés pendant
l'étape FETCH. Le tri nécessite encore une
opération SORT.

Les trois stratégies retournent 221 produits.

## 7. Tests automatiques

Fichiers :

- `mongosh/seed_tests.js`
- `mongosh/test_search.js`

| Groupe de tests | Tests réussis |
|---|---:|
| Recherche multicritère | 8 |
| Recherche à facettes | 4 |
| Hiérarchie des catégories | 6 |
| Synchronisation | 3 |
| Index MongoDB | 7 |
| Total | 28 |

Résultat de la validation locale :

- 28 tests réussis.
- 0 test échoué.

## 8. Compatibilité avec MongoDB Atlas

Les requêtes de recherche et de facettes ont
été testées en lecture seule sur la base Atlas
partagée avec le membre responsable du catalogue.

La synchronisation des catégories et la création
des nouveaux index sur Atlas restent soumises
à la validation de l'équipe.

## 9. Limites et perspectives

- Le benchmark utilise des données synthétiques.
- Les mesures sont effectuées sur un serveur local.
- Les stratégies sont exécutées dans un ordre fixe.
- Les temps du plan automatique peuvent inclure
  le coût de sélection du plan.
- Le nombre de résultats est comparé, mais pas
  l'identité de chaque document retourné.
- Certains tests reproduisent les requêtes plutôt
  que d'exécuter directement les scripts.
- Les facettes ne sont pas encore recalculées
  dynamiquement selon les filtres sélectionnés.
- Les performances doivent être confirmées
  sur les véritables données Amazon Reviews 2023.

## 10. Conclusion

Le module permet la recherche multicritère,
la recherche à facettes et l'optimisation
des requêtes grâce aux index MongoDB.

Les tests locaux et le benchmark démontrent
la pertinence de la stratégie d'indexation
sur les données de test utilisées.
