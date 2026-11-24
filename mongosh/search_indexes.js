// Index MongoDB - Search & Categories
// Implementation avec mongosh

print("=== Configuration des index MongoDB ===");

// Verifier les index existants avant creation
function ensureIndex(collection, keys, options) {
  if (!db.getCollectionNames().includes(collection.getName())) {
  db.createCollection(collection.getName());
}

  const existing = collection.getIndexes().find(index =>
    JSON.stringify(index.key) === JSON.stringify(keys) &&
    Boolean(index.unique) === Boolean(options.unique) &&
    !index.sparse &&
    !index.partialFilterExpression &&
    !index.hidden &&
    !index.collation
  );

  if (existing) {
    print("[EXISTANT] " + collection.getName() +
          " : " + existing.name);

    return existing.name;
  }

  const name = collection.createIndex(keys, options);

  print("[CREE] " + collection.getName() +
        " : " + name);

  return name;
}

// Index pour la recherche de produits

ensureIndex(
  db.products,
  { brand: 1 },
  { name: "idx_brand" }
);

ensureIndex(
  db.products,
  { price: 1 },
  { name: "idx_price" }
);

ensureIndex(
  db.products,
  { "rating.average": -1 },
  { name: "idx_rating" }
);

ensureIndex(
  db.products,
  { "category.main": 1 },
  { name: "idx_category_main" }
);

ensureIndex(
  db.products,
  { "category.path": 1 },
  { name: "idx_category_path" }
);

// Index compose pour la recherche multicritere

ensureIndex(
  db.products,
  {
    "category.main": 1,
    price: 1,
    "rating.average": -1
  },
  { name: "idx_category_price_rating" }
);

// Index pour la hierarchie des categories

ensureIndex(
  db.categories,
  { category_id: 1 },
  { name: "category_id_1", unique: true }
);

ensureIndex(
  db.categories,
  { parent_id: 1 },
  { name: "idx_parent_id" }
);

ensureIndex(
  db.categories,
  { ancestors: 1 },
  { name: "idx_ancestors" }
);

print("=== Index MongoDB verifies ===");

print("Produits :");
printjson(db.products.getIndexes());

print("Categories :");
printjson(db.categories.getIndexes());
