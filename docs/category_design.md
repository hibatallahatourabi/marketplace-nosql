# Category Design — Marketplace NoSQL

## 1. Objectif

Ce module permet de représenter les catégories
hiérarchiques du catalogue et de rechercher les
produits appartenant à une catégorie ou à ses
descendants.

L'implémentation utilise MongoDB et mongosh.

## 2. Compatibilité avec le catalogue

La collection products utilise deux champs :

- category.main : catégorie générale du dataset.
- category.path : chemin hiérarchique réel du produit.

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

Le schéma défini par le membre responsable du
catalogue est conservé sans modification.

## 3. Modèle de la collection categories

Chaque document contient les champs suivants :

| Champ | Type | Description |
|---|---|---|
| category_id | String | Identifiant unique |
| name | String | Nom de la catégorie |
| main | String | Catégorie générale du dataset |
| path | Array | Chemin hiérarchique complet |
| parent_id | String ou null | Identifiant du parent direct |
| ancestors | Array | Identifiants des ancêtres |
| depth | Number | Profondeur dans la hiérarchie |

Le modèle combine les références parentales
et le tableau des ancêtres.

## 4. Identifiants stables

Les identifiants sont générés à partir de la
catégorie principale et du chemin complet :

```javascript
function categoryId(main, path) {
  return JSON.stringify([main, ...path]);
}
```

Cette méthode permet de distinguer les catégories
qui possèdent le même nom mais appartiennent
à des branches différentes.

Exemple :

- All Beauty / Beauty & Personal Care / Hair Care / Accessories
- All Beauty / Beauty & Personal Care / Skin Care / Accessories

Ces deux catégories possèdent des identifiants
différents malgré leur nom identique.

## 5. Comparaison des modèles hiérarchiques

### 5.1 Référence parent_id

Chaque catégorie contient une référence vers
son parent direct.

Avantages :

- Structure simple.
- Faible espace de stockage.
- Recherche directe des enfants.

Limites :

- La recherche de tous les descendants nécessite
  une navigation récursive ou $graphLookup.

### 5.2 Tableau ancestors

Chaque catégorie contient les identifiants
de tous ses ancêtres.

Avantages :

- Recherche directe des descendants.
- Requêtes simples.
- Adapté aux opérations fréquentes de lecture.

Limites :

- Espace de stockage supplémentaire.
- Mise à jour des descendants lors du déplacement
  d'une branche.

### 5.3 Comparaison

| Critère | parent_id | ancestors |
|---|---|---|
| Parent direct | Simple | Possible |
| Enfants directs | Simple | Moins direct |
| Tous les descendants | Récursion | Requête directe |
| Complexité des requêtes profondes | Plus élevée | Plus faible |
| Stockage | Faible | Plus élevé |
| Modification de la hiérarchie | Plus simple | Plus coûteuse |

### 5.4 Modèle retenu

Le modèle hybride parent_id et ancestors
est retenu afin de faciliter les recherches
directes et les recherches hiérarchiques.

Ce choix est adapté à un catalogue orienté
principalement vers les opérations de lecture.

## 6. Synchronisation automatique

Fichier : `mongosh/sync_categories.js`

Le script construit la collection categories
à partir des chemins présents dans products.

Les étapes sont :

1. Lecture des catégories des produits.
2. Validation des chemins hiérarchiques.
3. Extraction de chaque niveau du chemin.
4. Génération des identifiants stables.
5. Construction de parent_id et ancestors.
6. Suppression des doublons en mémoire avec Map.
7. Insertion ou mise à jour avec upsert.

Exemple :

```javascript
db.categories.updateOne(
  { category_id: category.category_id },
  { $set: category },
  { upsert: true }
);
```

La synchronisation doit être exécutée après
les nouveaux imports de produits.

Le script ne modifie pas la collection products.

## 7. Idempotence de la synchronisation

Les tests locaux utilisent six produits,
dont un produit sans catégorie valide.

La première synchronisation donne :

| Indicateur | Résultat |
|---|---:|
| Catégories détectées | 7 |
| Catégories insérées | 7 |
| Catégories modifiées | 0 |
| Produits ignorés | 1 |

La deuxième synchronisation donne :

| Indicateur | Résultat |
|---|---:|
| Catégories détectées | 7 |
| Catégories insérées | 0 |
| Catégories modifiées | 0 |
| Catégories inchangées | 7 |
| Produits ignorés | 1 |

La répétition de la synchronisation ne crée
pas de doublons sur les données testées.

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

La catégorie générale du dataset est All Beauty.

La hiérarchie contient sept catégories.

Les deux catégories Accessories appartiennent
à des branches différentes.

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

### 9.4 Produits de la catégorie et des descendants

```javascript
db.products.find({
  "category.main": "All Beauty",
  "category.path.0": "Beauty & Personal Care",
  "category.path.1": "Hair Care"
});
```

Le filtrage utilise les positions du tableau
pour respecter le chemin hiérarchique.

Cette méthode évite de mélanger les produits
de catégories homonymes.

### 9.5 Résultats locaux

Pour la catégorie Hair Care :

- 3 catégories descendantes.
- 4 catégories en incluant Hair Care.
- 4 produits retournés.

Les produits retournés sont CAT001, CAT002,
CAT004 et CAT005.

Le produit de Skin Care et le produit sans
catégorie sont exclus.

## 10. Index MongoDB

Fichier : `mongosh/search_indexes.js`

Index de la collection categories :

| Index | Utilité |
|---|---|
| category_id_1 | Unicité des identifiants |
| idx_parent_id | Recherche des enfants directs |
| idx_ancestors | Recherche des descendants |

L'index unique sur category_id contribue
à empêcher les doublons.

Index de la collection products :

- Index sur category.main.
- Index sur category.path.
- Index composé sur category.main, price et rating.average.

Les index compatibles déjà présents sont réutilisés.

Le benchmark de recherche est documenté dans
search_design.md.

## 11. Tests automatiques

Fichiers :

- `mongosh/seed_tests.js`
- `mongosh/test_search.js`

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

Les neuf tests de hiérarchie et de synchronisation
ont réussi.

La suite complète du module contient 28 tests
réussis et aucun échec.

## 12. Intégration avec MongoDB Atlas

La structure des produits a été vérifiée sur
la base Atlas partagée avec l'équipe.

Le modèle de catégories est compatible avec
les chemins hiérarchiques observés.

La synchronisation et la création des index
sur Atlas restent à effectuer après validation
avec le membre responsable du catalogue.

Aucune modification de la base Atlas partagée
n'a été effectuée par ce module.

## 13. Limites et perspectives

- Les tests de hiérarchie utilisent des données
  synthétiques locales.
- Les catégories obsolètes ne sont pas supprimées
  automatiquement par la synchronisation.
- Le déplacement d'une branche peut nécessiter
  des mises à jour supplémentaires.
- La synchronisation conserve les catégories
  détectées en mémoire avant les upserts.
- Les performances de synchronisation doivent
  être évaluées sur le dataset complet.
- La comparaison parent_id et ancestors reste
  qualitative et ne constitue pas un benchmark
  expérimental des deux modèles.
- L'intégration finale sur Atlas reste à valider.

## 14. Conclusion

Le modèle hybride permet de représenter les
relations hiérarchiques et de retrouver les
produits d'une catégorie et de ses descendants.

Les identifiants stables et la synchronisation
avec upsert permettent de maintenir une structure
cohérente sans modifier le schéma du catalogue.

Les tests locaux valident les fonctionnalités
principales du modèle retenu.
