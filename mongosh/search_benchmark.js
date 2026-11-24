// Benchmark MongoDB - Search & Categories
// Implementation avec mongosh

print("=== Benchmark des performances ===");

const filtre = {
  "category.main": "All Beauty",
  "category.path.0": "Beauty & Personal Care",
  "category.path.1": "Hair Care",
  price: {
    $type: "number",
    $gte: NumberDecimal("0"),
    $lte: NumberDecimal("100")
  },
  "rating.average": { $gte: 4 }
};

const tri = {
  "rating.average": -1,
  product_id: 1
};

print("Nombre total de produits : " +
      db.products.countDocuments({}));

print("Filtres appliques :");
printjson(filtre);

function afficherResultats(nom, stats) {
  print("\n=== " + nom + " ===");

  printjson({
    temps_ms: stats.executionStats.executionTimeMillis,
    documentsExamines: stats.executionStats.totalDocsExamined,
    clesExaminees: stats.executionStats.totalKeysExamined,
    produitsTrouves: stats.executionStats.nReturned
  });

  print("Plan d'execution :");
  printjson(stats.queryPlanner.winningPlan);
}

// 1. Plan choisi automatiquement par MongoDB
const automatique = db.products.find(filtre)
  .sort(tri)
  .explain("executionStats");

afficherResultats("PLAN AUTOMATIQUE", automatique);

// 2. Recherche avec index compose
const avecIndex = db.products.find(filtre)
  .sort(tri)
  .hint({
    "category.main": 1,
    price: 1,
    "rating.average": -1
  })
  .explain("executionStats");

afficherResultats("AVEC INDEX COMPOSE", avecIndex);

// 3. Recherche sans utilisation d'index
const sansIndex = db.products.find(filtre)
  .sort(tri)
  .hint({ $natural: 1 })
  .explain("executionStats");

afficherResultats("SANS INDEX", sansIndex);

// Verification de la coherence des resultats
const nAuto = automatique.executionStats.nReturned;
const nAvec = avecIndex.executionStats.nReturned;
const nSans = sansIndex.executionStats.nReturned;

print("\n=== COMPARAISON ===");

printjson({
  resultats_coherents:
    nAuto === nAvec && nAvec === nSans,

  documents_avec_index:
    avecIndex.executionStats.totalDocsExamined,

  documents_sans_index:
    sansIndex.executionStats.totalDocsExamined,

  documents_economises:
    sansIndex.executionStats.totalDocsExamined -
    avecIndex.executionStats.totalDocsExamined
});

if (nAuto !== nAvec || nAvec !== nSans) {
  throw new Error("Resultats incoherents.");
}