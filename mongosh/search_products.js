// Recherche multicritere avec mongosh

print("=== Recherche multicritere ===");

const criteria = {
  main: "Beauty & Personal Care",
  path: ["Beauty & Personal Care", "Hair Care"],
  brand: null,
  minPrice: null,
  maxPrice: null,
  minRating: null
};

const filter = {};

// Filtrer selon la categorie principale effective
if (criteria.main) {
  filter.$or = [
    {
      "category.main": criteria.main
    },
    {
      "category.main": null,
      "category.path.0": criteria.main
    },
    {
      "category.main": /^\s*$/,
      "category.path.0": criteria.main
    }
  ];
}

// Filtrer selon le chemin hierarchique
if (criteria.path && criteria.path.length > 0) {
  criteria.path.forEach((name, index) => {
    filter["category.path." + index] = name;
  });
}

// Filtrer selon la marque
if (criteria.brand) {
  filter.brand = criteria.brand;
}

// Filtrer selon le prix
if (
  criteria.minPrice != null ||
  criteria.maxPrice != null
) {
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

// Filtrer selon la note
if (criteria.minRating != null) {
  filter["rating.average"] = {
    $gte: criteria.minRating
  };
}

print("=== Filtres appliques ===");
printjson(filter);

// Executer la recherche
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