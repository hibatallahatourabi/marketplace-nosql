// Generation des donnees synthetiques pour le benchmark
// Implementation avec mongosh

// Protection de la base de production
if (db.getName() !== "marketplace_benchmark_test") {
  throw new Error("Base de benchmark incorrecte.");
}

print("=== Generation des produits de test ===");

const total = 10000;

const categories = [
  {
    main: "All Beauty",
    path: ["Beauty & Personal Care", "Hair Care", "Shampoo"]
  },
  {
    main: "All Beauty",
    path: ["Beauty & Personal Care", "Hair Care", "Hair Chalk"]
  },
  {
    main: "All Beauty",
    path: ["Beauty & Personal Care", "Skin Care", "Moisturizers"]
  },
  {
    main: "Software",
    path: ["Software", "Business & Office"]
  },
  {
    main: "Video Games",
    path: ["Video Games", "Accessories"]
  }
];

const brands = [
  "BrandA",
  "BrandB",
  "BrandC",
  "BrandD",
  "BrandE"
];

// Nettoyer uniquement la collection de benchmark
db.products.deleteMany({});

let batch = [];

for (let i = 0; i < total; i++) {

  const category = categories[i % categories.length];

  const product = {
    product_id: "BENCH_" + i,
    title: "Produit de benchmark " + i,
    brand: brands[Math.floor(i / 5) % brands.length],
    category: category,
    price: i % 17 === 0
      ? null
      : NumberDecimal(((i * 37 % 50000) / 100).toFixed(2)),
    rating: {
      average: Number((1 + (i * 13 % 41) / 10).toFixed(1)),
      count: 1 + (i * 19 % 2000)
    }
  };

  batch.push(product);

  if (batch.length === 1000) {
    db.products.insertMany(batch);
    batch = [];
  }
}

if (batch.length > 0) {
  db.products.insertMany(batch);
}

print("\n=== Generation terminee ===");

printjson({
  produits_total: db.products.countDocuments({}),
  prix_manquants: db.products.countDocuments({ price: null }),
  produits_beaute: db.products.countDocuments({
    "category.main": "All Beauty"
  }),
  produits_software: db.products.countDocuments({
    "category.main": "Software"
  }),
  produits_video_games: db.products.countDocuments({
    "category.main": "Video Games"
  })
});