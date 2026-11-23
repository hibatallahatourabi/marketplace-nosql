// Recherche multicritere - Search & Categories
// Execution : mongosh marketplace_db mongosh/search_products.js

db = db.getSiblingDB("marketplace_db");

print("=== Recherche multicritere ===");

db.products.find(
  {
    "category.main": "All Beauty",
    "category.path": "Hair Care",
    price: {
      $gte: NumberDecimal("80"),
      $lte: NumberDecimal("130")
    },
    "rating.average": { $gte: 4 }
  },
  {
    _id: 0,
    product_id: 1,
    title: 1,
    brand: 1,
    price: 1,
    rating: 1
  }
).forEach(printjson);