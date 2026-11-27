const fs = require("fs");

const filePath = "data/beauty_products_final_5000.json";

const products = EJSON.parse(
  fs.readFileSync(filePath, "utf8")
);

if (!Array.isArray(products)) {
  throw new Error("Le dataset doit etre un tableau JSON.");
}

const ids = products.map(p => p.product_id);

const missingIds = ids.filter(
  id => typeof id !== "string" || id.trim() === ""
).length;

const validIds = ids.filter(
  id => typeof id === "string" && id.trim() !== ""
);

const uniqueIds = new Set(validIds);

const invalidPaths = products.filter(p =>
  !Array.isArray(p.category?.path) ||
  p.category.path.length === 0 ||
  !p.category.path.every(
    name => typeof name === "string" && name.trim() !== ""
  )
).length;

const missingMain = products.filter(p =>
  typeof p.category?.main !== "string" ||
  p.category.main.trim() === ""
).length;

const uniquePaths = new Set(
  products.map(p => JSON.stringify(p.category?.path))
);

print("=== VALIDATION DU DATASET ===");

printjson({
  total_products: products.length,
  unique_product_ids: uniqueIds.size,
  duplicate_ids: validIds.length - uniqueIds.size,
  missing_ids: missingIds,
  unique_category_paths: uniquePaths.size,
  invalid_category_paths: invalidPaths,
  missing_category_main: missingMain,
  null_prices: products.filter(p => p.price === null).length,
  missing_prices: products.filter(p => p.price === undefined).length,
  decimal_prices: products.filter(
    p => p.price?._bsontype === "Decimal128"
  ).length
});
print("\n=== PRODUITS SANS CATEGORIE PRINCIPALE ===");

const productsWithoutMain = products.filter(p =>
  typeof p.category?.main !== "string" ||
  p.category.main.trim() === ""
);

printjson(
  productsWithoutMain.slice(0, 5).map(p => ({
    product_id: p.product_id,
    title: p.title,
    category: p.category
  }))
);

print("\n=== RACINES DES CATEGORIES CONCERNEES ===");

printjson([
  ...new Set(
    productsWithoutMain.map(p => p.category.path[0])
  )
]);
print("\n=== DISTRIBUTION DES CATEGORIES PRINCIPALES ===");

const mainCounts = new Map();

for (const product of products) {
  const main = product.category?.main ?? null;

  mainCounts.set(
    main,
    (mainCounts.get(main) ?? 0) + 1
  );
}

printjson(
  Array.from(mainCounts, ([main, count]) => ({
    main,
    count
  })).sort((a, b) => b.count - a.count)
);