// Tests automatiques - Search & Categories
// Implementation avec mongosh

const database = db;

let passed = 0;
let failed = 0;

function test(name, condition) {
  if (condition) {
    print("PASS : " + name);
    passed++;
  } else {
    print("FAIL : " + name);
    failed++;
  }
}

print("=== Tests Search & Categories ===");

// Test 1 : nombre total de produits
test(
  "Nombre total de produits",
  database.products.countDocuments({}) === 5
);

// Test 2 : recherche par marque
test(
  "Recherche par marque",
  database.products.countDocuments({
    brand: "TestC"
  }) === 1
);

// Test 3 : recherche par prix
test(
  "Recherche par prix",
  database.products.countDocuments({
    price: {
      $type: "number",
      $gte: NumberDecimal("0"),
      $lte: NumberDecimal("100")
    }
  }) === 2
);

// Test 4 : recherche par note
test(
  "Recherche par note",
  database.products.countDocuments({
    "rating.average": { $gte: 4 }
  }) === 4
);

// Test 5 : prix null ou absent
test(
  "Prix null ou absent",
  database.products.countDocuments({
    price: null
  }) === 2
);

// Test 6 : prix negatif
test(
  "Detection des prix negatifs",
  database.products.countDocuments({
    price: { $lt: NumberDecimal("0") }
  }) === 1
);

// Test 7 : recherche multicritere
test(
  "Recherche multicritere",
  database.products.countDocuments({
    brand: "TestC",
    price: {
      $type: "number",
      $gte: NumberDecimal("0"),
      $lte: NumberDecimal("100")
    },
    "rating.average": { $gte: 4 }
  }) === 1
);

// Test 8 : exclusion des prix invalides
const validProducts = database.products.find({
  price: {
    $type: "number",
    $gte: NumberDecimal("0"),
    $lte: NumberDecimal("100")
  },
  "rating.average": { $gte: 4 }
}).toArray();

test(
  "Exclusion des prix invalides",
  validProducts.length === 2 &&
  validProducts.every(
    product => ["TestC", "TestD"].includes(product.brand)
  )
);



// Tests de la recherche a facettes

const facets = database.products.aggregate([
  {
    $facet: {
      brands: [
        { $match: { brand: { $exists: true, $ne: null } } },
        { $group: { _id: "$brand", count: { $sum: 1 } } }
      ],
      price_ranges: [
        {
          $match: {
            price: {
              $type: "number",
              $gte: NumberDecimal("0")
            }
          }
        },
        {
          $bucket: {
            groupBy: "$price",
            boundaries: [
              NumberDecimal("0"),
              NumberDecimal("50"),
              NumberDecimal("100"),
              NumberDecimal("200"),
              NumberDecimal("500")
            ],
            default: "500+",
            output: { count: { $sum: 1 } }
          }
        }
      ],
      missing_prices: [
        { $match: { price: null } },
        { $count: "count" }
      ],
      ratings: [
        { $match: { "rating.average": { $type: "number" } } },
        {
          $bucket: {
            groupBy: "$rating.average",
            boundaries: [0, 2, 3, 4, 5.01],
            default: "Other",
            output: { count: { $sum: 1 } }
          }
        }
      ]
    }
  }
]).toArray()[0];

// Test 9 : facette des marques
test(
  "Facette des marques",
  facets.brands.length === 5 &&
  facets.brands.every(brand => brand.count === 1)
);

// Test 10 : facette des prix
test(
  "Facette des prix",
  facets.price_ranges.length === 2 &&
  facets.price_ranges.every(range => range.count === 1)
);

// Test 11 : facette des prix manquants
test(
  "Facette des prix manquants",
  facets.missing_prices[0]?.count === 2
);

// Test 12 : facette des notes
test(
  "Facette des notes",
  facets.ratings.some(
    range => range._id === 3 && range.count === 1
  ) &&
  facets.ratings.some(
    range => range._id === 4 && range.count === 4
  )
);
// Tests de la hierarchie des categories

const categoryDb = db.getSiblingDB("marketplace_category_test");

const rootId = JSON.stringify([
  "All Beauty",
  "Beauty & Personal Care"
]);

const hairCareId = JSON.stringify([
  "All Beauty",
  "Beauty & Personal Care",
  "Hair Care"
]);

// Test 13 : nombre de categories
test(
  "Nombre total de categories",
  categoryDb.categories.countDocuments({}) === 7
);

// Test 14 : categorie racine
test(
  "Categorie racine",
  categoryDb.categories.countDocuments({
    category_id: rootId,
    parent_id: null,
    ancestors: { $size: 0 },
    depth: 0
  }) === 1
);

// Test 15 : descendants de Hair Care
test(
  "Descendants de Hair Care",
  categoryDb.categories.countDocuments({
    ancestors: hairCareId
  }) === 3
);

// Test 16 : relation parent-enfant
test(
  "Relation parent-enfant",
  categoryDb.categories.countDocuments({
    parent_id: hairCareId
  }) === 3
);

// Test 17 : categories homonymes
const accessories = categoryDb.categories.find({
  name: "Accessories"
}).toArray();

test(
  "Distinction des categories homonymes",
  accessories.length === 2 &&
  accessories[0].category_id !== accessories[1].category_id &&
  accessories[0].parent_id !== accessories[1].parent_id
);

// Test 18 : produits de la categorie et descendants
test(
  "Produits de Hair Care et descendants",
  categoryDb.products.countDocuments({
    "category.main": "All Beauty",
    "category.path.0": "Beauty & Personal Care",
    "category.path.1": "Hair Care"
  }) === 4
);

// Tests de synchronisation des categories

const beforeSync = categoryDb.categories.countDocuments({});

// Executer deux fois le script de synchronisation
const originalDb = db;

try {
  db = categoryDb;

  load("mongosh/sync_categories.js");
  load("mongosh/sync_categories.js");
} finally {
  db = originalDb;
}

const afterSync = categoryDb.categories.countDocuments({});

// Test 19 : idempotence de la synchronisation
test(
  "Synchronisation idempotente",
  beforeSync === 7 && afterSync === beforeSync
);

// Test 20 : absence de doublons
const duplicateCategories = categoryDb.categories.aggregate([
  {
    $group: {
      _id: "$category_id",
      count: { $sum: 1 }
    }
  },
  {
    $match: {
      count: { $gt: 1 }
    }
  }
]).toArray();

test(
  "Absence de doublons de categories",
  duplicateCategories.length === 0
);

// Test 21 : validite des relations parent-enfant
const allCategories = categoryDb.categories.find({}).toArray();

test(
  "Integrite des references parent_id",
  allCategories.every(category =>
    category.parent_id === null ||
    allCategories.some(parent =>
      parent.category_id === category.parent_id
    )
  )
);

// Tests des index MongoDB

const indexDb = db.getSiblingDB("marketplace_indexes_test");

const productIndexes = indexDb.products.getIndexes();
const categoryIndexes = indexDb.categories.getIndexes();

// Test 22 : conservation de l'index du membre 1
test(
  "Conservation de product_id_1",
  productIndexes.some(index =>
    index.name === "product_id_1" &&
    index.unique === true
  )
);

// Test 23 : reutilisation de l'index brand
test(
  "Reutilisation de brand_1",
  productIndexes.some(index =>
    index.name === "brand_1"
  ) &&
  !productIndexes.some(index =>
    index.name === "idx_brand"
  )
);

// Test 24 : reutilisation de l'index category.path
test(
  "Reutilisation de category.path_1",
  productIndexes.some(index =>
    index.name === "category.path_1"
  ) &&
  !productIndexes.some(index =>
    index.name === "idx_category_path"
  )
);

// Test 25 : index compose de recherche
test(
  "Index compose de recherche",
  productIndexes.some(index =>
    JSON.stringify(index.key) === JSON.stringify({
      "category.main": 1,
      price: 1,
      "rating.average": -1
    })
  )
);

// Test 26 : unicite des identifiants de categories
test(
  "Index unique category_id",
  categoryIndexes.some(index =>
    index.key.category_id === 1 &&
    index.unique === true
  )
);

// Test 27 : index de hierarchie
test(
  "Index de hierarchie",
  categoryIndexes.some(index =>
    index.key.parent_id === 1
  ) &&
  categoryIndexes.some(index =>
    index.key.ancestors === 1
  )
);

// Test 28 : index de prix et de note
test(
  "Index de prix et de note",
  productIndexes.some(index =>
    index.key.price === 1 &&
    Object.keys(index.key).length === 1
  ) &&
  productIndexes.some(index =>
    index.key["rating.average"] === -1 &&
    Object.keys(index.key).length === 1
  )
);


print("\n=== RESULTATS ===");
print("Tests reussis : " + passed);
print("Tests echoues : " + failed);

if (failed > 0) {
  throw new Error("Certains tests ont echoue.");
}
