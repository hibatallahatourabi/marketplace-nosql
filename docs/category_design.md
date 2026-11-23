# Category Design — Marketplace NoSQL

## 1. Objectif

Ce module permet de représenter la hiérarchie des catégories dans MongoDB et de rechercher les produits appartenant à une catégorie ou à ses sous-catégories.

L'implémentation utilise directement MongoDB Shell (`mongosh`), sans PyMongo.

## 2. Hiérarchie des catégories

La collection `categories` contient six catégories de test :

```text
All Beauty
├── Hair Care
│   ├── Hair Chalk
│   └── Shampoo
└── Skin Care
    └── Moisturizers
```

## 3. Modèle parent_id

Chaque catégorie possède un champ `parent_id` qui référence sa catégorie parente directe.

Exemple :

```json
{
  "category_id": "hair_chalk",
  "name": "Hair Chalk",
  "parent_id": "hair_care"
}
```

**Avantage :** structure simple et maintenance facile des relations directes.

**Limite :** la recherche de tous les descendants nécessite une navigation récursive ou l'opérateur `$graphLookup`.

## 4. Modèle ancestors

Chaque catégorie possède un tableau `ancestors` contenant les identifiants de tous ses ancêtres.

Exemple :

```json
{
  "category_id": "hair_chalk",
  "name": "Hair Chalk",
  "ancestors": ["beauty", "hair_care"]
}
```

**Avantage :** recherche directe de tous les descendants avec une requête MongoDB.

**Limite :** déplacer une catégorie peut nécessiter la mise à jour du tableau `ancestors` de plusieurs documents.

## 5. Compatibilité avec les produits

Les produits utilisent les noms des catégories dans `category.path`.

Exemple :

```json
{
  "category": {
    "main": "All Beauty",
    "path": ["All Beauty", "Hair Care", "Hair Chalk"]
  }
}
```

Les identifiants internes des catégories ne sont pas stockés directement dans `category.path`.

## 6. Recherche hiérarchique avec mongosh

**Fichier :** `mongosh/category_hierarchy.js`

Le script utilise `db.categories.find()` pour récupérer une catégorie et ses descendants.

Exemple :

```javascript
db.categories.find({
  $or: [
    { category_id: "hair_care" },
    { ancestors: "hair_care" }
  ]
});
```

Les noms des catégories trouvées sont ensuite utilisés pour rechercher les produits correspondants avec `$in` sur `category.path`.

**Résultats validés :**

Catégories trouvées :

- Hair Care
- Hair Chalk
- Shampoo

Produits trouvés :

- B001 : Hair Chalk Pink
- B002 : Hair Shampoo

## 7. Index MongoDB

**Fichier :** `mongosh/search_indexes.js`

Index de la collection `categories` :

- `category_id_1` : index unique sur `category_id`
- `idx_parent_id` : recherche des catégories enfants
- `idx_ancestors` : recherche des descendants

Index de la collection `products` :

- `idx_category_main`
- `idx_category_path`

## 8. Comparaison des modèles

| Critère | parent_id | ancestors |
|---|---|---|
| Parent direct | Simple | Moins direct |
| Tous les descendants | Récursion ou `$graphLookup` | Requête directe |
| Stockage | Plus faible | Plus élevé |
| Déplacement d'une branche | Plus simple | Mises à jour multiples |

## 9. Exécution et validation

Le script a été exécuté avec succès dans MongoDB Shell :

```powershell
mongosh "mongodb://localhost:27017/marketplace_db" --file mongosh/category_hierarchy.js
```

La validation a été réalisée sur six catégories et trois produits fictifs.

## 10. Limites

La hiérarchie actuelle est utilisée pour les tests.

La correspondance entre les noms stockés dans `category.path` et les catégories enregistrées doit être maintenue.

Des vérifications complémentaires seront nécessaires avec les données réelles du dataset Amazon Reviews 2023.