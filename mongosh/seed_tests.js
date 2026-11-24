// Preparation des donnees de tests
// Execution uniquement en local

if (db.getName() !== "marketplace_search_test") {
  throw new Error("Base de test incorrecte.");
}

const searchDb = db.getSiblingDB("marketplace_search_test");
const hierarchyDb = db.getSiblingDB("marketplace_category_test");
const indexesDb = db.getSiblingDB("marketplace_indexes_test");

// 1. Donnees de recherche et facettes

searchDb.products.deleteMany({});

searchDb.products.insertMany([
  {
    brand: "TestA",
    price: null,
    rating: { average: 4.2 }
  },
  {
    brand: "TestB",
    rating: { average: 3.5 }
  },
  {
    brand: "TestC",
    price: NumberDecimal("45.65"),
    rating: { average: 4.1 }
  },
  {
    brand: "TestD",
    price: 75.5,
    rating: { average: 4.5 }
  },
  {
    brand: "TestE",
    price: NumberDecimal("-10"),
    rating: { average: 4.0 }
  }
]);

// 2. Donnees de hierarchie

hierarchyDb.products.deleteMany({});
hierarchyDb.categories.deleteMany({});

function makeProduct(id, path) {
  return {
    product_id: id,
    category: {
      main: "All Beauty",
      path: ["Beauty & Personal Care", ...path]
    }
  };
}

hierarchyDb.products.insertMany([
  makeProduct("CAT001", ["Hair Care", "Hair Chalk"]),
  makeProduct("CAT002", ["Hair Care", "Shampoo"]),
  makeProduct("CAT003", ["Skin Care", "Accessories"]),
  makeProduct("CAT004", ["Hair Care", "Accessories"]),
  makeProduct("CAT005", ["Hair Care", "Shampoo"]),
  { product_id: "CAT006" }
]);

hierarchyDb.categories.createIndex(
  { category_id: 1 },
  { unique: true }
);

// 3. Simulation des index du membre 1

if (!indexesDb.getCollectionNames().includes("products")) {
  indexesDb.createCollection("products");
}

indexesDb.products.createIndex(
  { product_id: 1 },
  { unique: true }
);

indexesDb.products.createIndex({ brand: 1 });
indexesDb.products.createIndex({ "category.path": 1 });

// 4. Synchronisation et creation des index

const initialDb = db;

try {
  db = hierarchyDb;
  load("mongosh/sync_categories.js");

  db = indexesDb;
  load("mongosh/search_indexes.js");
} finally {
  db = initialDb;
}

// 5. Resume

print("\n=== PREPARATION TERMINEE ===");

printjson({
  produits_recherche: searchDb.products.countDocuments({}),
  produits_hierarchie: hierarchyDb.products.countDocuments({}),
  categories: hierarchyDb.categories.countDocuments({}),
  index_produits: indexesDb.products.getIndexes().length,
  index_categories: indexesDb.categories.getIndexes().length
});