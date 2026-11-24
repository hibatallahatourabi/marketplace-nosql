// Recherche hierarchique des categories avec mongosh

const main = "All Beauty";

const path = [
  "Beauty & Personal Care",
  "Hair Care"
];

// Identifiant stable de la categorie
const categoryId = JSON.stringify([main, ...path]);

print("=== Categorie selectionnee ===");

const category = db.categories.findOne({
  category_id: categoryId
});

if (!category) {
  throw new Error("Categorie introuvable");
}

printjson(category);

print("=== Categorie et ses descendants ===");

const categories = db.categories.find(
  {
    $or: [
      { category_id: categoryId },
      { ancestors: categoryId }
    ]
  },
  {
    _id: 0,
    category_id: 1,
    name: 1,
    path: 1,
    depth: 1
  }
).sort({ depth: 1, name: 1 }).toArray();

printjson(categories);

print("=== Produits de la categorie et ses descendants ===");

// Recherche par prefixe exact du chemin
const filter = {
  "category.main": main
};

path.forEach((name, index) => {
  filter["category.path." + index] = name;
});

const products = db.products.find(
  filter,
  {
    _id: 0,
    product_id: 1,
    title: 1,
    category: 1
  }
).sort({ product_id: 1 }).toArray();

printjson(products);

printjson({
  categories_found: categories.length,
  products_found: products.length
});
