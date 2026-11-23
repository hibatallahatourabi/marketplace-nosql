// Benchmark MongoDB : avec et sans index
// Execution : mongosh "mongodb://localhost:27017/marketplace_db" --file mongosh/search_benchmark.js

db = db.getSiblingDB("marketplace_db");

const filtre = {
  "category.main": "All Beauty",
  price: {
    $gte: NumberDecimal("80"),
    $lte: NumberDecimal("130")
  }
};

function afficherResultats(nom, stats) {
  print("\n=== " + nom + " ===");

  printjson({
    temps_ms: stats.executionStats.executionTimeMillis,
    documentsExamines: stats.executionStats.totalDocsExamined,
    clesExaminees: stats.executionStats.totalKeysExamined,
    produitsTrouves: stats.executionStats.nReturned
  });
}

const avecIndex = db.products.find(filtre)
  .hint("idx_category_price_rating")
  .explain("executionStats");

afficherResultats("AVEC INDEX", avecIndex);

const sansIndex = db.products.find(filtre)
  .hint({ $natural: 1 })
  .explain("executionStats");

afficherResultats("SANS INDEX", sansIndex);