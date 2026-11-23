// Hierarchie des categories - Search & Categories
// Execution avec mongosh

db = db.getSiblingDB("marketplace_db");

print("=== Categories et sous-categories de Hair Care ===");

// Recuperer la categorie et tous ses descendants
const categories = db.categories.find(
  {
    $or: [
      { category_id: "hair_care" },
      { ancestors: "hair_care" }
    ]
  },
  {
    _id: 0,
    name: 1
  }
).toArray();

printjson(categories);

// Recuperer les noms des categories
const categoryNames = categories.map(c => c.name);

print("=== Produits de Hair Care et ses sous-categories ===");

// Rechercher tous les produits correspondants
db.products.find(
  {
    "category.path": { $in: categoryNames }
  },
  {
    _id: 0,
    product_id: 1,
    title: 1,
    category: 1
  }
).forEach(printjson);