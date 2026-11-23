// Tests automatiques Search & Categories
// Execution avec mongosh, sans PyMongo

const database = db.getSiblingDB("marketplace_db");

let passed = 0;
let failed = 0;

function test(name, condition) {
  if (condition) {
    print("PASS : " + name);
    passed++;
  } else {
    print("FAIL : " + name);
    failed++;
  }
}

print("=== Tests Search & Categories ===");

// Test 1 : recherche par categorie
test(
  "Recherche par categorie",
  database.products.countDocuments({
    "category.path": "Hair Care"
  }) === 2
);

// Test 2 : recherche par prix
test(
  "Recherche par prix",
  database.products.countDocuments({
    price: {
      $gte: NumberDecimal("80"),
      $lte: NumberDecimal("130")
    }
  }) === 2
);

// Test 3 : recherche par note
test(
  "Recherche par note",
  database.products.countDocuments({
    "rating.average": { $gte: 4 }
  }) === 3
);

// Test 4 : hierarchie des categories
test(
  "Descendants de Hair Care",
  database.categories.countDocuments({
    ancestors: "hair_care"
  }) === 2
);

// Test 5 : verification des index
const indexes = database.products.getIndexes();

test(
  "Index de recherche",
  indexes.some(
    index => index.name === "idx_category_price_rating"
  )
);

print("\n=== RESULTATS ===");
print("Tests reussis : " + passed);
print("Tests echoues : " + failed);

if (failed > 0) {
  throw new Error("Certains tests ont echoue.");
}