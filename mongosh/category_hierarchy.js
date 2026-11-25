// Navigation dans la hierarchie des categories
// Implementation avec mongosh

const main = "Beauty & Personal Care";

const path = [
  "Beauty & Personal Care",
  "Hair Care"
];

// Construire l'identifiant stable
const categoryId = JSON.stringify([main, ...path]);

print("=== Categorie selectionnee ===");

const category = db.categories.findOne({
  category_id: categoryId
});

// Verifier l'existence de la categorie
if (!category) {
  throw new Error("Categorie introuvable.");
}

printjson(category);

// Rechercher la categorie et ses descendants
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
).sort({
  depth: 1,
  name: 1
}).toArray();

printjson(categories);

// Construire le filtre de categorie effective
const filter = {
  $or: [
    {
      "category.main": main
    },
    {
      "category.main": null,
      "category.path.0": main
    },
    {
      "category.main": /^\s*$/,
      "category.path.0": main
    }
  ]
};

// Respecter le chemin hierarchique exact
path.forEach((name, index) => {
  filter["category.path." + index] = name;
});

// Rechercher les produits de la categorie
// et de toutes ses sous-categories
print("=== Produits de la categorie et ses descendants ===");

const products = db.products.find(
  filter,
  {
    _id: 0,
    product_id: 1,
    title: 1,
    category: 1
  }
).sort({
  product_id: 1
}).toArray();

printjson(products);

// Afficher le resume
print("=== RESULTATS ===");

printjson({
  categories_found: categories.length,
  products_found: products.length
});