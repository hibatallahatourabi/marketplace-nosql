// Index MongoDB - Search & Categories

db = db.getSiblingDB("marketplace_db");

// Index pour la recherche de produits
db.products.createIndex(
  { brand: 1 },
  { name: "idx_brand" }
);

db.products.createIndex(
  { price: 1 },
  { name: "idx_price" }
);

db.products.createIndex(
  { "rating.average": -1 },
  { name: "idx_rating" }
);

db.products.createIndex(
  { "category.main": 1 },
  { name: "idx_category_main" }
);

db.products.createIndex(
  { "category.path": 1 },
  { name: "idx_category_path" }
);

db.products.createIndex(
  {
    "category.main": 1,
    price: 1,
    "rating.average": -1
  },
  { name: "idx_category_price_rating" }
);

// Index pour la hierarchie des categories
db.categories.createIndex(
  { category_id: 1 },
  { name: "category_id_1", unique: true }
);

db.categories.createIndex(
  { parent_id: 1 },
  { name: "idx_parent_id" }
);

db.categories.createIndex(
  { ancestors: 1 },
  { name: "idx_ancestors" }
);

print("=== Index MongoDB verifies ===");

print("Produits :");
printjson(db.products.getIndexes());

print("Categories :");
printjson(db.categories.getIndexes());