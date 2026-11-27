// Importation locale du dataset final avec mongosh

const fs = require("fs");

const filePath = "data/beauty_products_final_5000.json";

// Protection contre une importation sur Atlas
// Protection contre une importation sur Atlas
const uri = db.getMongo().getURI();

if (
  db.getName() !== "marketplace_real_test" ||
  !uri.startsWith(
    "mongodb://localhost:27017/marketplace_real_test?"
  )
) {
  throw new Error("Importation autorisee uniquement en local.");
}

// Eviter une importation en double
if (db.products.countDocuments({}) !== 0) {
  throw new Error("La collection products contient deja des donnees.");
}

print("=== LECTURE DU DATASET ===");

const products = EJSON.parse(
  fs.readFileSync(filePath, "utf8")
);

// Verifier le nombre de produits
if (!Array.isArray(products) || products.length !== 5000) {
  throw new Error("Le dataset doit contenir 5000 produits.");
}

// Verifier les identifiants
const ids = products.map(p => p.product_id);

if (
  ids.some(id =>
    typeof id !== "string" || id.trim() === ""
  ) ||
  new Set(ids).size !== 5000
) {
  throw new Error("Identifiants invalides ou dupliques.");
}

// Creer l'index unique sur les identifiants
db.products.createIndex(
  { product_id: 1 },
  { unique: true }
);

print("=== IMPORTATION DES PRODUITS ===");

const BATCH_SIZE = 500;
let inserted = 0;

// Importer les produits par lots
for (let i = 0; i < products.length; i += BATCH_SIZE) {

  const batch = products.slice(i, i + BATCH_SIZE);

  const result = db.products.insertMany(batch);

  inserted += Object.keys(result.insertedIds).length;

  print("Produits importes : " + inserted + "/5000");
}

// Verification finale
print("=== IMPORTATION TERMINEE ===");

printjson({
  database: db.getName(),
  inserted_products: inserted,
  total_products: db.products.countDocuments({}),
  null_prices: db.products.countDocuments({
    price: null
  }),
  decimal_prices: db.products.countDocuments({
    price: { $type: "decimal" }
  }),
  missing_main: db.products.countDocuments({
    "category.main": null
  })
});