// Synchronisation des categories depuis les produits
// Implementation avec mongosh

print("=== Synchronisation des categories ===");

// Identifiant stable base sur le chemin complet
function categoryId(main, path) {
  return JSON.stringify([main, ...path]);
}

const categories = new Map();
let skipped = 0;

// Parcourir les produits
db.products.find(
  {},
  { _id: 0, category: 1 }
).forEach(product => {

  const main = product.category?.main;
  const path = product.category?.path;

  // Verifier la validite des categories
  if (
    typeof main !== "string" ||
    main.trim() === "" ||
    !Array.isArray(path) ||
    path.length === 0 ||
    !path.every(name =>
      typeof name === "string" && name.trim() !== ""
    )
  ) {
    skipped++;
    return;
  }

  // Construire chaque niveau de la hierarchie
  for (let i = 0; i < path.length; i++) {

    const currentPath = path.slice(0, i + 1);
    const id = categoryId(main, currentPath);

    const parentId = i === 0
      ? null
      : categoryId(main, path.slice(0, i));

    const ancestors = [];

    for (let j = 0; j < i; j++) {
      ancestors.push(
        categoryId(main, path.slice(0, j + 1))
      );
    }

    categories.set(id, {
      category_id: id,
      name: path[i],
      main: main,
      path: currentPath,
      parent_id: parentId,
      ancestors: ancestors,
      depth: i
    });
  }
});

let inserted = 0;
let updated = 0;
let unchanged = 0;

// Synchroniser sans creer de doublons
for (const category of categories.values()) {

  const result = db.categories.updateOne(
    { category_id: category.category_id },
    { $set: category },
    { upsert: true }
  );

  inserted += result.upsertedCount;
  updated += result.modifiedCount;
  unchanged += result.matchedCount - result.modifiedCount;
}

printjson({
  categories_detected: categories.size,
  inserted: inserted,
  updated: updated,
  unchanged: unchanged,
  skipped_products: skipped
});
