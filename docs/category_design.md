# Category Design — Marketplace NoSQL

## 1. Objectif

Ce module permet de représenter les catégories hiérarchiques du catalogue et de rechercher les produits appartenant à une catégorie ou à ses descendants.

L'implémentation utilise MongoDB, JavaScript et mongosh.

## 2. Compatibilité avec le catalogue

La collection products utilise deux champs :

- category.main : catégorie principale interne du catalogue.
- category.path : chemin hiérarchique du produit.

Exemple :

```json
{
  "category": {
    "main": "All Beauty",
    "path": [
      "Beauty & Personal Care",
      "Hair Care",
      "Hair Coloring Products",
      "Hair Chalk"
    ]
  }
}
```

Le schéma défini par le membre responsable du catalogue est conservé sans modification.

### 2.1 Gestion des catégories principales manquantes

Lorsque category.main est absent, null ou vide, le premier élément du chemin hiérarchique valide est utilisé comme catégorie principale dérivée.

Cette stratégie permet de conserver les produits dont la catégorie principale est manquante sans modifier les documents de la collection products.

Sur le dataset réel de 5 000 produits, 39 produits sont concernés.

### 2.2 Distinction entre classification interne et catégorie source

Le champ category.main représente la classification interne du catalogue.

L'analyse du mapping officiel asin2category.json a confirmé que les 5 000 produits appartiennent à la catégorie source Beauty and Personal Care d'Amazon Reviews 2023.

La classification interne et la catégorie source officielle sont donc deux informations distinctes.

Voir [Dataset Origin Validation](dataset_origin_validation.md).

## 3. Modèle de la collection categories

Chaque document contient les champs suivants :

| Champ | Type | Description |
|---|---|---|
| category_id | String | Identifiant unique |
| name | String | Nom de la catégorie |
| main | String | Catégorie principale interne ou dérivée |
| path | Array | Chemin hiérarchique complet |
| parent_id | String ou null | Identifiant du parent direct |
| ancestors | Array | Identifiants des ancêtres |
| depth | Number | Profondeur dans la hiérarchie |

Le modèle combine les références parentales et le tableau des ancêtres.

Une catégorie racine possède un parent_id égal à null, un tableau ancestors vide et une profondeur égale à 0.

## 4. Identifiants stables

Les identifiants sont générés à partir de la catégorie principale et du chemin complet :

```javascript
function categoryId(main, path) {
  return JSON.stringify([main, ...path]);
}
```

Cette méthode permet de distinguer les catégories qui possèdent le même nom mais appartiennent à des branches différentes.

Exemple :

- All Beauty / Beauty & Personal Care / Hair Care / Accessories
- All Beauty / Beauty & Personal Care / Skin Care / Accessories

Ces deux catégories possèdent des identifiants différents malgré leur nom identique.

Les identifiants restent stables tant que la catégorie principale et le chemin ne changent pas.

## 5. Comparaison des modèles hiérarchiques

### 5.1 Parent References

Chaque catégorie contient une référence vers son parent direct dans le champ parent_id.

Avantages :

- Structure simple.
- Faible espace de stockage.
- Recherche directe des enfants.

Limites :

- La recherche de tous les descendants nécessite une navigation récursive ou $graphLookup.

### 5.2 Ancestors Array

Chaque catégorie contient les identifiants de tous ses ancêtres dans le tableau ancestors.

Avantages :

- Recherche directe des descendants.
- Requêtes simples.
- Adapté aux opérations fréquentes de lecture.

Limites :

- Espace de stockage supplémentaire.
- Mise à jour des descendants lors du déplacement d'une branche.

### 5.3 Comparaison théorique

| Critère | Parent References | Ancestors Array |
|---|---|---|
| Parent direct | Simple | Possible |
| Enfants directs | Simple | Moins direct |
| Tous les descendants | Récursion | Requête directe |
| Complexité des requêtes profondes | Plus élevée | Plus faible |
| Stockage des relations | Faible | Plus élevé |
| Modification de la hiérarchie | Plus simple | Plus coûteuse |

### 5.4 Modèle retenu

Le modèle hybride parent_id et ancestors est retenu afin de faciliter les recherches directes et les recherches hiérarchiques.

Ce choix est adapté à un catalogue orienté principalement vers les opérations de lecture.

Le benchmark expérimental présenté dans la section 11 permet d'évaluer les deux méthodes de recherche des descendants.

## 6. Synchronisation automatique

Fichier : `mongosh/sync_categories.js`

Le script construit la collection categories à partir des chemins présents dans products.

Les étapes sont :

1. Lecture des catégories des produits.
2. Validation des chemins hiérarchiques.
3. Détermination de la catégorie principale originale ou dérivée.
4. Extraction de chaque niveau du chemin.
5. Génération des identifiants stables.
6. Construction de parent_id et ancestors.
7. Suppression des doublons en mémoire avec Map.
8. Préparation des opérations updateOne avec upsert.
9. Exécution des opérations avec bulkWrite par lots de 500.

Exemple d'opération :

```javascript
{
  updateOne: {
    filter: {
      category_id: category.category_id
    },
    update: {
      $set: category
    },
    upsert: true
  }
}
```

Les opérations sont exécutées par lots :

```javascript
db.categories.bulkWrite(
  operations,
  { ordered: false }
);
```

Cette approche permet de regrouper plusieurs opérations d'écriture au lieu d'exécuter une requête individuelle pour chaque catégorie.

La synchronisation doit être exécutée après les nouveaux imports de produits.

Le script ne modifie pas la collection products et ne supprime pas automatiquement les catégories obsolètes.

## 7. Idempotence de la synchronisation

### 7.1 Validation sur les données synthétiques

Les tests locaux utilisent six produits, dont un produit sans catégorie valide.

Première synchronisation :

| Indicateur | Résultat |
|---|---:|
| Catégories détectées | 7 |
| Catégories insérées | 7 |
| Catégories modifiées | 0 |
| Produits ignorés | 1 |

Deuxième synchronisation :

| Indicateur | Résultat |
|---|---:|
| Catégories détectées | 7 |
| Catégories insérées | 0 |
| Catégories modifiées | 0 |
| Catégories inchangées | 7 |
| Produits ignorés | 1 |

La répétition séquentielle de la synchronisation ne crée pas de doublons sur les données testées.

### 7.2 Validation sur les données réelles

La synchronisation a également été exécutée sur le dataset réel de 5 000 produits.

| Indicateur | Résultat |
|---|---:|
| Produits analysés | 5 000 |
| Chemins hiérarchiques distincts | 574 |
| Chemins invalides | 0 |
| Catégories détectées | 1 470 |
| Catégories insérées | 1 470 |
| Catégories modifiées | 0 |
| Produits ignorés | 0 |
| Produits avec catégorie principale dérivée | 39 |

Tous les produits disposent d'un chemin hiérarchique valide.

La gestion des catégories principales manquantes permet de conserver les 39 produits concernés.

## 8. Hiérarchie de test

```text
Beauty & Personal Care
├── Hair Care
│   ├── Hair Chalk
│   ├── Shampoo
│   └── Accessories
└── Skin Care
    └── Accessories
```

La catégorie principale interne utilisée dans ce jeu de test est All Beauty.

La hiérarchie contient sept catégories.

Les deux catégories Accessories appartiennent à des branches différentes et possèdent des identifiants distincts.

## 9. Requêtes hiérarchiques

Fichier : `mongosh/category_hierarchy.js`

### 9.1 Enfants directs

```javascript
db.categories.find({
  parent_id: categoryId
});
```

### 9.2 Tous les descendants

```javascript
db.categories.find({
  ancestors: categoryId
});
```

### 9.3 Catégorie et descendants

```javascript
db.categories.find({
  $or: [
    { category_id: categoryId },
    { ancestors: categoryId }
  ]
});
```

### 9.4 Produits de la catégorie et de ses descendants

```javascript
const main = "Beauty & Personal Care";

const path = [
  "Beauty & Personal Care",
  "Hair Care"
];

const filter = {
  $or: [
    { "category.main": main },
    {
      "category.main": null,
      "category.path.0": main
    },
    {
      "category.main": /^\s*$/,
      "category.path.0": main
    }
  ]
};

path.forEach((name, index) => {
  filter["category.path." + index] = name;
});

db.products.find(filter);
```

Le filtrage utilise les positions du tableau pour respecter le chemin hiérarchique.

Cette méthode évite de mélanger les produits de catégories homonymes et prend en charge les catégories principales dérivées.

### 9.5 Résultats sur les données synthétiques

Pour la catégorie Hair Care :

- 3 catégories descendantes.
- 4 catégories en incluant Hair Care.
- 4 produits retournés.

Les produits retournés sont CAT001, CAT002, CAT004 et CAT005.

Le produit de Skin Care et le produit sans catégorie valide sont exclus.

### 9.6 Résultats sur les données réelles

Pour la catégorie Hair Care dans l'espace de classification dérivé Beauty & Personal Care :

| Indicateur | Résultat |
|---|---:|
| Catégories trouvées, catégorie sélectionnée incluse | 8 |
| Produits trouvés | 4 |

Les identifiants des produits retournés sont :

- B01BO4M88C
- B073CBMGRP
- B08PC95NJ7
- B099255BXG

Ces résultats valident la recherche hiérarchique avec prise en charge des catégories principales dérivées.

## 10. Index MongoDB

Fichier : `mongosh/search_indexes.js`

Index de la collection categories :

| Index | Champs | Utilité |
|---|---|---|
| category_id_1 | category_id | Unicité des identifiants |
| idx_parent_id | parent_id | Recherche des enfants directs |
| idx_ancestors | ancestors | Recherche des descendants |

L'index unique sur category_id contribue à empêcher les doublons.

L'index sur ancestors est un index multikey, car ce champ contient un tableau.

Index de la collection products utilisés pour les recherches hiérarchiques :

- Index sur category.main.
- Index sur category.path.
- Index composé sur category.main, price et rating.average.

Les index compatibles déjà présents sont réutilisés.

Les conflits de spécifications génèrent une erreur explicite. Aucun index existant n'est automatiquement supprimé.

Le benchmark de recherche multicritère est documenté dans [Search Design](search_design.md).

## 11. Benchmark des modèles hiérarchiques

Fichier : `mongosh/hierarchy_benchmark.js`

### 11.1 Objectif

Comparer expérimentalement les performances de recherche de tous les descendants avec les deux modèles :

- Parent References avec $graphLookup.
- Ancestors Array avec une requête directe.

### 11.2 Données utilisées

Le benchmark utilise les 1 470 catégories générées à partir des 5 000 produits réels, en local et sur MongoDB Atlas.

La catégorie sélectionnée est :

- Catégorie principale interne : All Beauty.
- Chemin : Beauty & Personal Care.

### 11.3 Méthode Parent References

Exemple de recherche récursive :

```javascript
db.categories.aggregate([
  {
    $match: {
      category_id: categoryId
    }
  },
  {
    $graphLookup: {
      from: "categories",
      startWith: "$category_id",
      connectFromField: "category_id",
      connectToField: "parent_id",
      as: "descendants"
    }
  },
  {
    $unwind: "$descendants"
  },
  {
    $project: {
      _id: 0,
      category_id: "$descendants.category_id"
    }
  }
]);
```

### 11.4 Méthode Ancestors Array

```javascript
db.categories.find(
  { ancestors: categoryId },
  { _id: 0, category_id: 1 }
);
```

### 11.5 Méthodologie expérimentale

Le benchmark utilise :

- Des exécutions initiales de préchauffage.
- Cinq répétitions pour chaque méthode.
- Une alternance de l'ordre d'exécution.
- Une mesure du temps de récupération des résultats.
- Une comparaison des identifiants retournés.

### 11.6 Résultats expérimentaux locaux

| Exécution | Parent References | Ancestors Array |
|---|---:|---:|
| 1 | 8 ms | 4 ms |
| 2 | 8 ms | 5 ms |
| 3 | 9 ms | 4 ms |
| 4 | 8 ms | 5 ms |
| 5 | 9 ms | 4 ms |
| Moyenne | 8,4 ms | 4,4 ms |
| Médiane | 8 ms | 4 ms |

| Indicateur | Parent References | Ancestors Array |
|---|---:|---:|
| Descendants retournés | 564 | 564 |
| Identifiants identiques | Oui | Oui |

### 11.7 Analyse des résultats locaux

Le modèle Ancestors Array permet :

- Une réduction du temps moyen de 47,62 %.
- Une accélération observée d'environ 1,91 fois.
- La récupération des mêmes 564 descendants que Parent References.

Ces résultats soutiennent le choix du modèle hybride pour les recherches hiérarchiques fréquentes.

Les mesures concernent la catégorie sélectionnée et l'environnement local utilisé. Elles ne constituent pas une garantie de performance pour toutes les hiérarchies.

### 11.8 Benchmark sur MongoDB Atlas

Le benchmark a été exécuté sur la base partagée marketplace_db après la synchronisation des catégories.

Deux séries de cinq répétitions ont été réalisées.

#### Première série

| Exécution | Parent References | Ancestors Array |
|---|---:|---:|
| 1 | 129 ms | 766 ms |
| 2 | 110 ms | 99 ms |
| 3 | 103 ms | 96 ms |
| 4 | 104 ms | 95 ms |
| 5 | 106 ms | 101 ms |
| Moyenne | 110,4 ms | 231,4 ms |
| Médiane | 106 ms | 99 ms |

La première mesure de 766 ms constitue une valeur inhabituellement élevée.

Sa cause exacte reste inconnue. La latence réseau, la charge du serveur et les mécanismes de cache constituent des explications possibles.

Cette mesure est conservée dans les résultats.

#### Deuxième série

| Exécution | Parent References | Ancestors Array |
|---|---:|---:|
| 1 | 102 ms | 102 ms |
| 2 | 103 ms | 107 ms |
| 3 | 105 ms | 100 ms |
| 4 | 104 ms | 99 ms |
| 5 | 109 ms | 99 ms |
| Moyenne | 104,6 ms | 101,4 ms |
| Médiane | 104 ms | 100 ms |

Les deux méthodes présentent des performances proches lors de cette deuxième série.

Ancestors Array réduit le temps moyen de 3,06 % pour cette série.

### 11.9 Résultats cumulés sur Atlas

| Indicateur | Parent References | Ancestors Array |
|---|---:|---:|
| Nombre de mesures | 10 | 10 |
| Moyenne globale | 107,5 ms | 166,4 ms |
| Médiane globale | 104,5 ms | 99,5 ms |
| Descendants retournés | 564 | 564 |
| Comparaisons avec identifiants identiques | 10/10 | 10/10 |

Les dix comparaisons ont retourné exactement les mêmes identifiants de catégories descendantes.

La médiane globale favorise légèrement Ancestors Array.

Cependant, la moyenne globale est affectée par la mesure de 766 ms et favorise Parent References.

Il est donc nécessaire de considérer les moyennes, les médianes et les mesures individuelles.

### 11.10 Comparaison locale et Atlas

| Indicateur | Local | Atlas |
|---|---:|---:|
| Nombre total de catégories | 1 470 | 1 470 |
| Descendants retournés | 564 | 564 |
| Nombre de mesures par méthode | 5 | 10 |
| Parent References - moyenne | 8,4 ms | 107,5 ms |
| Ancestors Array - moyenne | 4,4 ms | 166,4 ms |
| Parent References - médiane | 8 ms | 104,5 ms |
| Ancestors Array - médiane | 4 ms | 99,5 ms |

Les mesures distantes incluent la récupération des résultats par mongosh et les communications avec le serveur Atlas.

Les résultats locaux et distants ne sont donc pas directement comparables comme des mesures isolées du temps de traitement du serveur.

Le benchmark compare deux stratégies de recherche au sein de la même collection hybride. Il ne compare pas deux collections indépendantes utilisant exclusivement chacun des modèles.

Les résultats soutiennent la pertinence fonctionnelle du modèle hybride, sans garantir une supériorité systématique d'une méthode.

## 12. Tests automatiques

Fichiers :

- `mongosh/seed_tests.js`
- `mongosh/test_search.js`
- `mongosh/test_invalid_filters.js`

Les tests de hiérarchie vérifient :

1. Le nombre total de catégories.
2. La structure de la catégorie racine.
3. Les descendants de Hair Care.
4. Les relations parent-enfant.
5. La distinction des catégories homonymes.
6. La récupération des produits des descendants.

Les tests de synchronisation vérifient :

1. L'idempotence.
2. L'absence de doublons.
3. L'intégrité des références parent_id.

Des tests supplémentaires vérifient la gestion des catégories principales manquantes, la conservation des documents originaux et la recherche avec des catégories dérivées.

Un contrôle supplémentaire vérifie l'absence de résultat pour un identifiant de catégorie inexistant.

Résultats globaux du module :

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

Résultat final : 43 tests réussis et aucun échec.

Les scripts seed_tests.js et test_search.js sont réservés aux bases locales dédiées. Le script test_invalid_filters.js, dans sa version validée en lecture seule, a également été exécuté sur Atlas : 8 tests réussis et aucun échec.

## 13. Intégration avec MongoDB Atlas

L'intégration finale du module Search & Categories a été réalisée le 27 novembre 2026 avec l'autorisation de l'équipe.

### 13.1 Environnement

- Plateforme : MongoDB Atlas Free Tier (M0).
- Base : marketplace_db.
- Version MongoDB : 8.0.39.
- Version mongosh : 2.14.0.
- Fournisseur : AWS.
- Région : Paris (eu-west-3).

### 13.2 Vérification du catalogue

Avant la synchronisation, les identifiants des produits locaux et Atlas ont été comparés.

| Indicateur | Résultat |
|---|---:|
| Produits sur Atlas | 5 000 |
| Identifiants uniques | 5 000 |
| Identifiants locaux absents sur Atlas | 0 |
| Identifiants supplémentaires sur Atlas | 0 |
| Catégories principales manquantes | 39 |

La comparaison confirme l'égalité des ensembles d'identifiants, sans constituer une comparaison exhaustive des champs des produits.

### 13.3 Synchronisation et idempotence

Le script sync_categories.js a été exécuté deux fois sur Atlas.

| Indicateur | Première exécution | Deuxième exécution |
|---|---:|---:|
| Catégories détectées | 1 470 | 1 470 |
| Catégories insérées | 1 470 | 0 |
| Catégories modifiées | 0 | 0 |
| Catégories inchangées | 0 | 1 470 |
| Produits ignorés | 0 | 0 |
| Produits avec catégorie principale dérivée | 39 | 39 |

La deuxième exécution confirme l'idempotence séquentielle de la synchronisation.

Les documents produits ne sont pas modifiés par cette opération.

### 13.4 Validation de la navigation hiérarchique

La catégorie sélectionnée est Hair Care dans l'espace de classification dérivé Beauty & Personal Care.

| Indicateur | Local | Atlas |
|---|---:|---:|
| Catégories incluant Hair Care | 8 | 8 |
| Catégories descendantes | 7 | 7 |
| Produits retournés | 4 | 4 |

Les identifiants des produits retournés sont identiques :

- B01BO4M88C
- B073CBMGRP
- B08PC95NJ7
- B099255BXG

Les quatre produits possèdent une catégorie principale null dans les documents originaux.

La navigation hiérarchique prend donc correctement en charge les catégories principales dérivées.

### 13.5 Index des catégories sur Atlas

| Index | Champ | Utilité |
|---|---|---|
| _id_ | _id | Identifiant MongoDB |
| category_id_1 | category_id | Unicité |
| idx_parent_id | parent_id | Recherche des enfants directs |
| idx_ancestors | ancestors | Recherche des descendants |

Nombre total d'index : 4.

L'index unique category_id_1 contribue à empêcher la création de catégories en double.

### 13.6 Intégrité finale

| Indicateur | Résultat |
|---|---:|
| Produits | 5 000 |
| Identifiants produits uniques | 5 000 |
| Catégories | 1 470 |
| Identifiants catégories uniques | 1 470 |
| Index produits | 8 |
| Index catégories | 4 |
| Produits de sauvegarde conservés | 117 000 |
| Tests de filtres invalides réussis | 8/8 |

Aucun doublon d'identifiant produit ou catégorie n'a été détecté.

La collection products_backup_117000 a été conservée.

### 13.7 Stockage de la collection categories

Statistiques finales obtenues avec db.categories.stats() :

| Indicateur | Résultat |
|---|---:|
| Documents | 1 470 |
| Taille logique des documents | 0,852 MiB |
| Stockage des documents alloué | 0,344 MiB |
| Taille des index | 0,531 MiB |
| Stockage total alloué | 0,875 MiB |

La taille totale allouée à la collection categories et à ses index est de 0,875 MiB.

L'intégration des quatre nouveaux index produits a ajouté environ 0,246 MiB.

Le surcoût total de stockage alloué associé à l'intégration du module est donc d'environ 1,121 MiB.

Cette mesure concerne le module complet. Elle ne permet pas d'isoler le surcoût spécifique du tableau ancestors par rapport à un modèle utilisant uniquement parent_id.

### 13.8 Vérification du quota Atlas

| Indicateur | Avant intégration | Après intégration |
|---|---:|---:|
| Logical Size estimée | 381 MB | 410 MB |
| Utilisation du quota | 74,4 % | 80,1 % |
| Capacité restante estimée | 131 MB | 102 MB |

Le quota du cluster est de 512 MB.

Les valeurs Logical Size sont des estimations visuelles obtenues à partir du graphique Atlas.

Le stockage alloué aux collections et la métrique Logical Size représentent des indicateurs différents.

La variation globale ne peut pas être attribuée exclusivement au module Search & Categories, car le cluster est partagé.

Voir [Atlas Validation Report](atlas_validation.md) pour les résultats détaillés.

## 14. Limites et perspectives

- Les tests fonctionnels utilisent principalement des données synthétiques locales, complétées par des validations sur les données réelles.
- Les catégories obsolètes ne sont pas supprimées automatiquement par la synchronisation.
- Le déplacement d'une branche peut nécessiter des mises à jour supplémentaires.
- Les identifiants changent lorsque la catégorie principale ou le chemin hiérarchique change.
- La synchronisation conserve les catégories détectées en mémoire avant les upserts.
- Les opérations bulkWrite ne constituent pas une transaction globale.
- Les performances de synchronisation sur des volumes plus importants restent à évaluer.
- Le benchmark hiérarchique concerne une catégorie sélectionnée.
- Les mesures distantes incluent les communications réseau.
- La cause exacte de la mesure de 766 ms reste inconnue.
- Le benchmark compare deux stratégies de requêtes au sein du même modèle hybride.
- Le stockage total du modèle hybride a été mesuré sur Atlas, mais le surcoût spécifique de chaque représentation hiérarchique n'a pas été isolé expérimentalement.
- Les valeurs du quota Atlas sont approximatives.
- Les résultats obtenus sur 5 000 produits ne garantissent pas les mêmes performances sur des volumes plus importants.
- La compatibilité effective avec les reviews relève des autres travaux de l'équipe.

## 15. Conclusion

Le modèle hybride permet de représenter les relations hiérarchiques et de retrouver les produits d'une catégorie et de ses descendants.

Les identifiants stables et la synchronisation par bulkWrite avec upsert permettent de maintenir une structure cohérente sans modifier le schéma du catalogue.

La validation sur 5 000 produits réels a permis de générer 1 470 catégories et de prendre en charge les 39 produits dont la catégorie principale est manquante.

Le benchmark local montre que la stratégie Ancestors Array réduit de 47,62 % le temps moyen de recherche des descendants pour la catégorie étudiée.

Les benchmarks Atlas confirment que les deux stratégies retournent exactement les mêmes 564 descendants.

La médiane distante favorise légèrement Ancestors Array, tandis que la moyenne globale est affectée par une mesure exceptionnellement élevée.

Les 43 tests locaux et les huit vérifications répétées avec succès sur Atlas confirment le fonctionnement des principales fonctionnalités testées.

La synchronisation finale sur Atlas a généré 1 470 catégories uniques et son idempotence séquentielle a été vérifiée.

Les 5 000 produits et la sauvegarde de 117 000 produits ont été préservés.

Le stockage total alloué à la collection categories et à ses index est de 0,875 MiB.

Le module Search & Categories est techniquement terminé et prêt pour l'intégration globale du projet.

Documents complémentaires :

- [Search Design](search_design.md)
- [Final Local Validation Report](final_validation.md)
- [Dataset Origin Validation](dataset_origin_validation.md)
- [Atlas Validation Report](atlas_validation.md)
