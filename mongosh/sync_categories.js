// Synchronisation des categories depuis les produits
// Implementation avec mongosh

print("=== Synchronisation des categories ===");

// Identifiant stable base sur le chemin complet
function categoryId(main, path) {
  return JSON.stringify([main, ...path]);
}

const categories = new Map();

let skipped = 0;
let derivedMain = 0;

// Parcourir les produits
db.products.find(
  {},
  { _id: 0, category: 1 }
).forEach(product => {

  const originalMain = product.category?.main;
  const path = product.category?.path;

  // Verifier la validite du chemin
  if (
    !Array.isArray(path) ||
    path.length === 0 ||
    !path.every(name =>
      typeof name === "string" && name.trim() !== ""
    )
  ) {
    skipped++;
    return;
  }

  // Verifier si la categorie principale est renseignee
  const hasValidMain =
    typeof originalMain === "string" &&
    originalMain.trim() !== "";

  // Deduire la categorie principale si elle est manquante
  const main = hasValidMain
    ? originalMain
    : path[0];

  // Compter chaque produit concerne une seule fois
  if (!hasValidMain) {
    derivedMain++;
  }

  // Construire chaque niveau de la hierarchie
  for (let i = 0; i < path.length; i++) {

    const currentPath = path.slice(0, i + 1);
    const id = categoryId(main, currentPath);

    // Identifier la categorie parente
    const parentId = i === 0
      ? null
      : categoryId(main, path.slice(0, i));

    // Construire la liste des ancetres
    const ancestors = [];

    for (let j = 0; j < i; j++) {
      ancestors.push(
        categoryId(main, path.slice(0, j + 1))
      );
    }

    // Ajouter la categorie sans doublon
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

// Compteurs de synchronisation
let inserted = 0;
let updated = 0;
let unchanged = 0;

// Taille maximale d'un lot
const BATCH_SIZE = 500;

let operations = [];

// Executer un lot d'operations
function executeBatch() {

  if (operations.length === 0) {
    return;
  }

  const result = db.categories.bulkWrite(
    operations,
    { ordered: false }
  );

  inserted += result.upsertedCount;
  updated += result.modifiedCount;

  unchanged +=
    result.matchedCount - result.modifiedCount;

  operations = [];
}

// Synchroniser les categories par lots
for (const category of categories.values()) {

  operations.push({
    updateOne: {
      filter: {
        category_id: category.category_id
      },
      update: {
        $set: category
      },
      upsert: true
    }
  });

  // Executer le lot lorsque la limite est atteinte
  if (operations.length >= BATCH_SIZE) {
    executeBatch();
  }
}

// Executer le dernier lot restant
executeBatch();

// Afficher les resultats
printjson({
  categories_detected: categories.size,
  inserted: inserted,
  updated: updated,
  unchanged: unchanged,
  skipped_products: skipped,
  derived_main_products: derivedMain
});