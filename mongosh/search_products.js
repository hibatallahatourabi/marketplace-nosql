// Recherche multicritere - Search & Categories
// Implementation avec mongosh

print("=== Recherche multicritere ===");

// Criteres de recherche
const criteria = {
  main: "All Beauty",
  path: ["Beauty & Personal Care", "Hair Care"],
  brand: null,
  minPrice: 0,
  maxPrice: 100,
  minRating: 4
};

const filter = {};

// Categorie principale
if (criteria.main) {
  filter["category.main"] = criteria.main;
}

// Chemin hierarchique
if (criteria.path && criteria.path.length > 0) {
  criteria.path.forEach((name, index) => {
    filter["category.path." + index] = name;
  });
}

// Marque optionnelle
if (criteria.brand) {
  filter.brand = criteria.brand;
}

// Intervalle de prix
if (criteria.minPrice != null || criteria.maxPrice != null) {

  filter.price = {
    $type: "number",
    $gte: NumberDecimal(
      String(criteria.minPrice ?? 0)
    )
  };

  if (criteria.maxPrice != null) {
    filter.price.$lte = NumberDecimal(
      String(criteria.maxPrice)
    );
  }
}

// Note minimale
if (criteria.minRating != null) {
  filter["rating.average"] = {
    $gte: criteria.minRating
  };
}

print("=== Filtres appliques ===");

printjson(filter);

// Recherche des produits
const products = db.products.find(
  filter,
  {
    _id: 0,
    product_id: 1,
    title: 1,
    brand: 1,
    category: 1,
    price: 1,
    rating: 1
  }
).sort({
  "rating.average": -1,
  product_id: 1
}).toArray();

print("=== Produits trouves ===");

printjson(products);

printjson({
  products_found: products.length
});
