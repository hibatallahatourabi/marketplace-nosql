# Search Design — Marketplace NoSQL

## 1. Objectif

Le module Search & Categories permet de rechercher des produits selon plusieurs critères, de calculer des facettes dynamiques et d'optimiser les requêtes MongoDB.

L'implémentation utilise MongoDB Shell (mongosh) et JavaScript.

## 2. Modèle des produits

Le module respecte le schéma commun du catalogue :

- product_id : String
- title : String
- brand : String
- category.main : String ou null
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

Le champ category.main représente une classification interne du catalogue et ne doit pas être confondu avec la catégorie source officielle Amazon Reviews 2023.

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
  $or: [
    { "category.main": "All Beauty" },
    {
      "category.main": null,
      "category.path.0": "All Beauty"
    },
    {
      "category.main": /^\s*$/,
      "category.path.0": "All Beauty"
    }
  ],
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

Les positions du tableau category.path permettent de respecter le chemin hiérarchique exact et de récupérer les produits des sous-catégories.

Lorsque category.main est absent, null ou vide, le premier élément du chemin peut être utilisé comme catégorie principale dérivée.

Les prix null, absents ou non numériques sont exclus lorsqu'un filtre de prix est appliqué. Les prix négatifs sont exclus avec des bornes valides non négatives.

Les résultats sont triés par note décroissante, puis par identifiant du produit.

## 4. Recherche à facettes dynamiques

Fichier : `mongosh/facet_search.js`

La recherche à facettes utilise le pipeline d'agrégation MongoDB.

Un premier opérateur $match applique les critères sélectionnés. L'opérateur $facet calcule ensuite plusieurs agrégations sur les produits correspondants.

Les facettes calculées sont :

- Marques et nombre de produits par marque.
- Intervalles de prix.
- Nombre de prix manquants.
- Intervalles de notes.
- Nombre total de produits correspondants.

Les principaux opérateurs utilisés sont :

| Opérateur | Fonction |
|---|---|
| $match | Filtrage des documents |
| $group | Regroupement par marque |
| $bucket | Regroupement par intervalle |
| $count | Comptage des documents |
| $sort | Tri des résultats |
| $facet | Calcul de plusieurs agrégations |
| $set | Normalisation du résultat |

### 4.1 Intervalles de prix

- [0, 50[
- [50, 100[
- [100, 200[
- [200, 500[
- 500 et plus

### 4.2 Intervalles de notes

- [0, 2[
- [2, 3[
- [3, 4[
- [4, 5.01[

Les produits sans prix peuvent rester comptabilisés dans les facettes des marques et des notes lorsqu'aucun filtre de prix ne les exclut.

Toutes les facettes sont recalculées à partir des filtres sélectionnés simultanément.

### 4.3 Validation des filtres

Le script facet_search.js vérifie :

- La validité numérique des prix.
- L'absence de prix négatifs.
- La cohérence entre le prix minimum et le prix maximum.
- La validité numérique de la note minimale.
- Une note minimale comprise entre 0 et 5.

Les filtres invalides génèrent une erreur explicite.

### 4.4 Validation sur les données réelles

Critères sélectionnés :

- Catégorie principale : All Beauty.
- Chemin : Beauty & Personal Care / Hair Care.
- Prix : de 0 à 100.
- Note minimale : 4.

| Indicateur | Résultat |
|---|---:|
| Produits correspondants | 428 |
| Prix dans [0, 50[ | 401 |
| Prix dans [50, 100[ | 27 |
| Prix manquants | 0 |
| Notes dans [4, 5.01[ | 428 |

## 5. Stratégie d'indexation

Fichier : `mongosh/search_indexes.js`

| Index | Champs |
|---|---|
| product_id_1 | product_id (unique) |
| idx_brand | brand |
| idx_price | price |
| idx_rating | rating.average |
| idx_category_main | category.main |
| idx_category_path | category.path |
| idx_category_price_rating | category.main, price, rating.average |

L'index sur category.path est un index multikey, car ce champ contient un tableau.

L'index composé est défini comme suit :

```javascript
{
  "category.main": 1,
  price: 1,
  "rating.average": -1
}
```

Le script recherche les index compatibles avant de créer de nouveaux index.

Les index compatibles déjà présents sont réutilisés, notamment brand_1 et category.path_1.

L'index unique product_id_1 appartient au catalogue et doit être conservé.

Les spécifications incompatibles génèrent une erreur explicite. Aucun index existant n'est automatiquement supprimé.

## 6. Benchmark des performances

Fichier : `mongosh/search_benchmark.js`

### 6.1 Données utilisées

Le benchmark final utilise les 5 000 produits réels du dataset partagé.

| Indicateur | Résultat |
|---|---:|
| Produits | 5 000 |
| Identifiants uniques | 5 000 |
| Chemins distincts | 574 |
| Chemins invalides | 0 |
| Catégories principales manquantes | 39 |
| Prix null | 2 545 |
| Prix Decimal128 | 2 455 |

Un benchmark préliminaire avait également été réalisé sur 10 000 produits synthétiques.

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

Cinq exécutions sur les données réelles :

| Exécution | Automatique | Index composé | Sans index |
|---|---:|---:|---:|
| 1 | 54 ms | 10 ms | 10 ms |
| 2 | 61 ms | 11 ms | 12 ms |
| 3 | 62 ms | 11 ms | 8 ms |
| 4 | 62 ms | 10 ms | 9 ms |
| 5 | 56 ms | 11 ms | 8 ms |
| Moyenne | 59 ms | 10,6 ms | 9,4 ms |
| Médiane | 61 ms | 11 ms | 9 ms |

| Indicateur | Automatique | Index composé | Sans index |
|---|---:|---:|---:|
| Documents examinés | 2 368 | 1 472 | 5 000 |
| Clés examinées | 2 368 | 3 885 | 0 |
| Produits retournés | 428 | 428 | 428 |

### 6.4 Analyse

L'index composé imposé permet :

- Une réduction de 70,56 % des documents examinés par rapport au parcours sans index.
- Une économie de 3 528 documents examinés.
- Une réduction de 82,03 % du temps moyen par rapport au plan automatique.
- Une accélération observée d'environ 5,57 fois par rapport au plan automatique.

Cependant, le parcours sans index reste légèrement plus rapide que l'index composé imposé sur ce dataset de taille limitée.

L'utilisation d'un index ne garantit donc pas systématiquement une réduction du temps d'exécution.

Les trois stratégies retournent le même nombre de produits : 428.

## 7. Tests automatiques

Fichiers :

- `mongosh/seed_tests.js`
- `mongosh/test_search.js`
- `mongosh/test_invalid_filters.js`

| Groupe de tests | Tests réussis |
|---|---:|
| Recherche multicritère | 8 |
| Recherche à facettes | 4 |
| Hiérarchie des catégories | 6 |
| Synchronisation | 3 |
| Index MongoDB | 7 |
| Catégories principales manquantes | 7 |
| Filtres invalides et catégorie inexistante | 8 |
| Total | 43 |

Résultat de la validation locale :

- 43 tests réussis.
- 0 test échoué.

Les tests couvrent les fonctionnalités principales, les valeurs manquantes, la compatibilité des index et plusieurs cas de filtres invalides.

Les scripts de tests et de génération des données de test doivent uniquement être exécutés sur les bases locales dédiées.

## 8. Provenance du dataset

L'analyse du fichier officiel asin2category.json a permis de comparer les 5 000 identifiants avec 35 393 189 entrées du mapping Amazon Reviews 2023.

| Indicateur | Résultat |
|---|---:|
| Identifiants retrouvés | 5 000 |
| Identifiants non retrouvés | 0 |
| Taux de correspondance | 100 % |
| Beauty and Personal Care | 5 000 |
| All Beauty | 0 |

La catégorie source officielle des produits est Beauty and Personal Care.

La compatibilité effective avec les reviews doit encore être confirmée.

Voir [Dataset Origin Validation](dataset_origin_validation.md).

## 9. Compatibilité avec MongoDB Atlas

La structure des produits et des requêtes initiales ont été vérifiées en lecture seule sur la base Atlas partagée.

Le module a ensuite été validé localement avec le dataset final de 5 000 produits.

Au 27 novembre 2026, un import temporaire des 5 000 produits sur Atlas a été signalé comme réussi par le membre responsable du catalogue.

Le remplacement définitif de la collection products, la création des index et la synchronisation des catégories restent en attente de validation collective.

Aucune modification des données ou des index Atlas n'a été effectuée par le module Search & Categories.

## 10. Limites et perspectives

- Les mesures de performance ont été effectuées sur un serveur local.
- Les stratégies du benchmark de recherche sont exécutées dans un ordre fixe.
- Le temps du plan automatique peut inclure le coût de sélection du plan.
- Les statistiques explain ne représentent pas la latence complète d'une application.
- Le benchmark de recherche compare le nombre de résultats, mais pas l'identité de chaque produit retourné.
- Certains tests reproduisent les requêtes plutôt que d'exécuter directement les scripts.
- La validation des filtres numériques est implémentée dans facet_search.js et ne couvre pas tous les scripts.
- Les facettes utilisent simultanément tous les filtres sélectionnés.
- Les performances sur des volumes plus importants restent à étudier.
- L'intégration finale sur Atlas reste à valider.

## 11. Conclusion

Le module permet la recherche multicritère, la recherche à facettes dynamiques et l'optimisation des requêtes grâce aux index MongoDB.

La validation sur 5 000 produits réels et les 43 tests réussis confirment le fonctionnement des principales fonctionnalités.

Les benchmarks montrent l'intérêt des index pour réduire le nombre de documents examinés, tout en soulignant que leur efficacité dépend du volume des données et de la requête utilisée.

Voir [Final Validation Report](final_validation.md) pour les résultats détaillés et les instructions de reproduction.