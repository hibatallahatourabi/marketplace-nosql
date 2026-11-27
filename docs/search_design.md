# Search Design — Marketplace NoSQL

## 1. Objectif

Le module Search & Categories permet de rechercher des produits selon plusieurs critères, de calculer des facettes dynamiques et d'optimiser les requêtes MongoDB.

L'implémentation utilise MongoDB Shell (mongosh) et JavaScript.

Le module a été validé localement puis intégré avec succès dans la base MongoDB Atlas partagée.

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

Le champ `category.main` représente une classification interne du catalogue et ne doit pas être confondu avec la catégorie source officielle Amazon Reviews 2023.

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

Les positions du tableau `category.path` permettent de respecter le chemin hiérarchique exact et de récupérer les produits des sous-catégories.

Lorsque `category.main` est absent, null ou vide, le premier élément du chemin peut être utilisé comme catégorie principale dérivée.

Dans l'exemple précédent, la catégorie principale sélectionnée est All Beauty alors que le chemin commence par Beauty & Personal Care. Les branches de récupération des catégories principales manquantes ne correspondent donc pas à cette combinaison particulière de critères.

Les prix null, absents ou non numériques sont exclus lorsqu'un filtre de prix est appliqué. Les prix négatifs sont exclus avec des bornes valides non négatives.

Les résultats sont triés par note décroissante, puis par identifiant du produit.

### 3.1 Validation de la catégorie principale dérivée

La recherche suivante a été validée localement et sur Atlas :

- Catégorie principale : Beauty & Personal Care.
- Chemin : Beauty & Personal Care / Hair Care.
- Aucun filtre de prix.
- Aucun filtre de marque.
- Aucun filtre de note.

| Identifiant du produit | Note |
|---|---:|
| B01BO4M88C | 5,0 |
| B073CBMGRP | 4,6 |
| B099255BXG | 4,1 |
| B08PC95NJ7 | 4,0 |

Les quatre produits possèdent une catégorie principale null dans les documents d'origine.

La recherche les retrouve grâce au mécanisme de récupération de la catégorie principale à partir du chemin hiérarchique.

Ce mécanisme ne nécessite aucune modification des documents produits.

## 4. Recherche à facettes dynamiques

Fichier : `mongosh/facet_search.js`

La recherche à facettes utilise le pipeline d'agrégation MongoDB.

Un premier opérateur `$match` applique les critères sélectionnés. L'opérateur `$facet` calcule ensuite plusieurs agrégations sur les produits correspondants.

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

Le script `facet_search.js` vérifie :

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

| Indicateur | Local | Atlas |
|---|---:|---:|
| Produits correspondants | 428 | 428 |
| Prix dans [0, 50[ | 401 | 401 |
| Prix dans [50, 100[ | 27 | 27 |
| Prix manquants | 0 | 0 |
| Notes dans [4, 5.01[ | 428 | 428 |

Les résultats observés sur Atlas sont cohérents avec les résultats de la validation locale.

L'agrégation par marque a également été exécutée avec succès sur Atlas.

## 5. Stratégie d'indexation

Fichier : `mongosh/search_indexes.js`

### 5.1 Index des produits

| Index prévu | Champs |
|---|---|
| product_id_1 | product_id (unique) |
| idx_brand | brand |
| idx_price | price |
| idx_rating | rating.average |
| idx_category_main | category.main |
| idx_category_path | category.path |
| idx_category_price_rating | category.main, price, rating.average |

L'index sur `category.path` est un index multikey, car ce champ contient un tableau.

L'index composé est défini comme suit :

```javascript
{
  "category.main": 1,
  price: 1,
  "rating.average": -1
}
```

Le script recherche les index compatibles avant de créer de nouveaux index.

Les index compatibles déjà présents sont réutilisés, notamment `brand_1` et `category.path_1`.

L'index unique `product_id_1` appartient au catalogue et doit être conservé.

Les spécifications incompatibles détectées par le script génèrent une erreur explicite. Aucun index existant n'est automatiquement supprimé.

### 5.2 Index effectivement présents sur Atlas

| Index | Statut |
|---|---|
| _id_ | Index automatique conservé |
| product_id_1 | Index unique conservé |
| brand_1 | Index existant réutilisé |
| category.path_1 | Index existant réutilisé |
| idx_price | Créé |
| idx_rating | Créé |
| idx_category_main | Créé |
| idx_category_price_rating | Créé |

Nombre total d'index sur la collection products : 8.

Quatre nouveaux index de recherche ont été créés.

Les index existants sur la marque et le chemin hiérarchique ont été réutilisés sans duplication.

### 5.3 Index des catégories

| Index | Champ |
|---|---|
| _id_ | _id |
| category_id_1 | category_id (unique) |
| idx_parent_id | parent_id |
| idx_ancestors | ancestors |

Nombre total d'index sur la collection categories : 4.

Ces index permettent d'assurer l'unicité des identifiants des catégories et de faciliter les requêtes hiérarchiques.

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
2. Index composé imposé avec `hint()`.
3. Parcours sans index avec `hint({ $natural: 1 })`.

Les statistiques sont obtenues avec :

```javascript
explain("executionStats")
```

Les indicateurs étudiés sont :

- executionTimeMillis
- totalDocsExamined
- totalKeysExamined
- nReturned

### 6.3 Résultats expérimentaux locaux

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

### 6.4 Analyse des résultats locaux

L'index composé imposé permet :

- Une réduction de 70,56 % des documents examinés par rapport au parcours sans index.
- Une économie de 3 528 documents examinés.
- Une réduction de 82,03 % du temps moyen par rapport au plan automatique.
- Une accélération observée d'environ 5,57 fois par rapport au plan automatique.

Cependant, le parcours sans index reste légèrement plus rapide que l'index composé imposé sur ce dataset de taille limitée.

L'utilisation d'un index ne garantit donc pas systématiquement une réduction du temps d'exécution.

Les trois stratégies retournent le même nombre de produits : 428.

### 6.5 Résultats expérimentaux sur MongoDB Atlas

Le benchmark a été exécuté sur la base partagée `marketplace_db` après la création des index et la synchronisation des catégories.

| Indicateur | Automatique | Index composé | Sans index |
|---|---:|---:|---:|
| Temps d'exécution | 80 ms | 13 ms | 12 ms |
| Documents examinés | 2 368 | 1 472 | 5 000 |
| Clés examinées | 2 368 | 3 885 | 0 |
| Produits retournés | 428 | 428 | 428 |

Le plan automatique a sélectionné l'index `idx_price`.

La deuxième stratégie a imposé l'index `idx_category_price_rating`.

La troisième stratégie a utilisé un parcours de collection COLLSCAN.

Les trois stratégies comportent une étape de tri.

### 6.6 Analyse des résultats Atlas

L'index composé imposé permet :

- Une réduction de 70,56 % des documents examinés par rapport au parcours sans index.
- Une économie de 3 528 documents examinés.
- Une réduction de 83,75 % du temps d'exécution par rapport au plan automatique.
- Une accélération observée d'environ 6,15 fois par rapport au plan automatique.

Le parcours sans index reste légèrement plus rapide dans cette exécution : 12 ms contre 13 ms.

L'index composé examine davantage de clés que le plan automatique, mais moins de documents.

Les résultats confirment l'intérêt de l'index composé pour réduire le nombre de documents examinés.

Ils ne permettent pas d'affirmer que l'index composé est systématiquement plus rapide qu'un parcours de collection.

### 6.7 Comparaison locale et Atlas

| Stratégie | Local — moyenne de 5 exécutions | Atlas — 1 exécution |
|---|---:|---:|
| Plan automatique | 59 ms | 80 ms |
| Index composé | 10,6 ms | 13 ms |
| Sans index | 9,4 ms | 12 ms |

Les nombres de documents examinés, de clés examinées et de produits retournés sont identiques entre les deux environnements pour chaque stratégie.

Les mesures Atlas correspondent à une seule exécution par stratégie. Elles ne constituent pas des moyennes.

Les statistiques obtenues avec `explain("executionStats")` ne représentent pas la latence complète ressentie par une application cliente.

## 7. Tests automatiques

Fichiers :

- `mongosh/seed_tests.js`
- `mongosh/test_search.js`
- `mongosh/test_invalid_filters.js`

### 7.1 Validation locale

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

### 7.2 Validation sur Atlas

Le script `test_invalid_filters.js` a également été exécuté sur la base Atlas partagée.

| Test | Résultat |
|---|---|
| Prix minimum négatif | PASS |
| Prix maximum négatif | PASS |
| Prix minimum supérieur au maximum | PASS |
| Prix non numérique | PASS |
| Note négative | PASS |
| Note supérieure à 5 | PASS |
| Note non numérique | PASS |
| Catégorie inexistante | PASS |

Résultat :

- 8 tests réussis.
- 0 test échoué.
- Taux de réussite : 100 %.

Le test de catégorie inexistante vérifie l'absence de l'identifiant correspondant dans la collection categories. Il ne teste pas directement la gestion de l'exception dans `category_hierarchy.js`.

### 7.3 Précautions d'exécution

Les scripts `seed_tests.js` et `test_search.js` sont réservés aux bases locales dédiées.

Ils ne doivent pas être exécutés sur la base Atlas partagée.

Le script `test_invalid_filters.js`, dans sa version validée, ne modifie pas les documents et a pu être exécuté sur Atlas.

Les huit vérifications réalisées sur Atlas constituent une répétition distante des huit vérifications locales correspondantes, et non huit nouveaux cas de test distincts.

## 8. Provenance du dataset

L'analyse du fichier officiel `asin2category.json` a permis de comparer les 5 000 identifiants avec 35 393 189 entrées du mapping Amazon Reviews 2023.

| Indicateur | Résultat |
|---|---:|
| Identifiants retrouvés | 5 000 |
| Identifiants non retrouvés | 0 |
| Taux de correspondance | 100 % |
| Beauty and Personal Care | 5 000 |
| All Beauty | 0 |

La catégorie source officielle des produits est Beauty and Personal Care selon le mapping ASIN.

Cette classification officielle ne doit pas être confondue avec les catégories internes du catalogue.

Le fichier de reviews recommandé est `Beauty_and_Personal_Care.jsonl.gz`.

La compatibilité effective avec les reviews est gérée séparément par l'équipe et n'est pas démontrée par cette analyse du mapping.

Voir [Dataset Origin Validation](dataset_origin_validation.md).

## 9. Intégration avec MongoDB Atlas

### 9.1 Environnement

L'intégration finale a été réalisée le 27 novembre 2026.

- Plateforme : MongoDB Atlas Free Tier (M0).
- Base de données : marketplace_db.
- Version MongoDB : 8.0.39.
- Version mongosh : 2.14.0.
- Fournisseur cloud : AWS.
- Région : Paris (eu-west-3).

### 9.2 Étapes d'intégration

Après l'import définitif des 5 000 produits par le membre responsable du catalogue, les opérations suivantes ont été effectuées :

1. Vérification du nombre de produits et des identifiants uniques.
2. Vérification des index existants.
3. Vérification du stockage disponible.
4. Comparaison des identifiants locaux et Atlas.
5. Création des index de recherche manquants.
6. Synchronisation de la collection categories.
7. Vérification de l'idempotence de la synchronisation.
8. Validation de la recherche multicritère.
9. Validation de la recherche à facettes.
10. Validation de la navigation hiérarchique.
11. Exécution des benchmarks de recherche et de hiérarchie.
12. Exécution des tests de filtres invalides.
13. Vérification finale de l'intégrité et du stockage.

La création des index et la synchronisation ont été effectuées avec l'autorisation de l'équipe.

### 9.3 Résultats finaux

| Indicateur | Résultat |
|---|---:|
| Produits | 5 000 |
| Identifiants produits uniques | 5 000 |
| Identifiants locaux absents sur Atlas | 0 |
| Identifiants supplémentaires sur Atlas | 0 |
| Catégories | 1 470 |
| Identifiants catégories uniques | 1 470 |
| Index produits | 8 |
| Index catégories | 4 |
| Produits de sauvegarde conservés | 117 000 |
| Tests de filtres invalides réussis | 8/8 |

La comparaison des identifiants confirme que les datasets local et Atlas contiennent les mêmes identifiants produits. Elle ne constitue pas une comparaison exhaustive de tous les champs.

La synchronisation des catégories a été exécutée deux fois.

La première exécution a inséré 1 470 catégories.

La deuxième exécution n'a inséré aucune catégorie supplémentaire et a laissé les 1 470 catégories inchangées.

Les documents produits existants n'ont pas été modifiés par la synchronisation.

### 9.4 Analyse du stockage

Les statistiques finales des collections sont les suivantes :

| Collection | Documents | Stockage total alloué |
|---|---:|---:|
| products | 5 000 | 9,813 MiB |
| categories | 1 470 | 0,875 MiB |
| products_backup_117000 | 117 000 | 180,504 MiB |

Évolution du stockage associé aux index de recherche :

| Indicateur | Avant | Après |
|---|---:|---:|
| Nombre d'index produits | 4 | 8 |
| Taille des index produits | 0,586 MiB | 0,832 MiB |

Le stockage supplémentaire alloué aux index produits est d'environ 0,246 MiB.

Le stockage total alloué à la collection categories et à ses index est de 0,875 MiB.

Le surcoût total mesuré associé à l'intégration du module est donc d'environ 1,121 MiB.

### 9.5 Vérification du quota Atlas

| Indicateur | Avant intégration | Après intégration |
|---|---:|---:|
| Logical Size estimée | 381 MB | 410 MB |
| Utilisation du quota | 74,4 % | 80,1 % |
| Capacité restante estimée | 131 MB | 102 MB |

Le quota du cluster est de 512 MB.

Les valeurs Logical Size sont des estimations visuelles obtenues à partir du graphique Atlas.

La variation globale du stockage ne peut pas être attribuée exclusivement au module Search & Categories, car le cluster est partagé avec les autres membres de l'équipe.

Le stockage alloué aux collections et la métrique Logical Size d'Atlas sont deux indicateurs différents.

La collection de sauvegarde contenant 117 000 produits a été conservée.

Voir [Atlas Validation Report](atlas_validation.md) pour les mesures détaillées, les résultats des benchmarks et les instructions de reproduction.

## 10. Limites et perspectives

- Les mesures locales reposent sur cinq exécutions par stratégie.
- Les mesures du benchmark de recherche Atlas reposent sur une seule exécution par stratégie.
- Les stratégies du benchmark de recherche sont exécutées dans un ordre fixe.
- Le temps du plan automatique peut inclure le coût de sélection du plan.
- Les statistiques explain ne représentent pas la latence complète d'une application.
- Le benchmark de recherche compare le nombre de résultats, mais pas l'identité de chaque produit retourné.
- Certains tests reproduisent les requêtes plutôt que d'exécuter directement les scripts.
- La validation des filtres numériques est implémentée dans `facet_search.js` et ne couvre pas tous les scripts.
- Les facettes utilisent simultanément tous les filtres sélectionnés.
- Les agrégations à facettes restent soumises aux limites de mémoire et de taille des résultats de MongoDB.
- La vérification de compatibilité des index ne couvre pas toutes les options avancées d'indexation.
- Les lectures du quota Atlas sont approximatives.
- Les performances sur des volumes plus importants restent à étudier.
- La validation de la compatibilité avec les reviews relève des autres travaux de l'équipe.

## 11. Conclusion

Le module permet la recherche multicritère, la recherche à facettes dynamiques et l'optimisation des requêtes grâce aux index MongoDB.

La validation sur 5 000 produits réels et les 43 tests locaux réussis confirment le fonctionnement des principales fonctionnalités.

L'intégration sur MongoDB Atlas a également été réalisée avec succès.

Les résultats finaux confirment :

- La conservation des 5 000 produits et de leurs identifiants uniques.
- La création de quatre nouveaux index de recherche.
- La réutilisation des index compatibles existants.
- La synchronisation de 1 470 catégories uniques.
- La validation de la recherche multicritère et de la recherche à facettes.
- La réussite des huit vérifications de filtres invalides et de catégorie inexistante sur Atlas.
- La réduction de 70,56 % des documents examinés grâce à l'index composé par rapport au parcours de collection.
- Un surcoût de stockage alloué d'environ 1,121 MiB.
- La conservation de la collection de sauvegarde.

Les benchmarks montrent l'intérêt des index pour réduire le nombre de documents examinés, tout en soulignant que leur efficacité dépend du volume des données et de la requête utilisée.

Le module Search & Categories est techniquement terminé et prêt pour l'intégration globale du projet.

Documents complémentaires :

- [Category Design](category_design.md)
- [Final Local Validation Report](final_validation.md)
- [Dataset Origin Validation](dataset_origin_validation.md)
- [Atlas Validation Report](atlas_validation.md)