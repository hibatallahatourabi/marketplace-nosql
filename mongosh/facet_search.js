// Recherche a facettes avec MongoDB
// Execution : mongosh marketplace_db --file mongosh/facet_search.js

db = db.getSiblingDB("marketplace_db");

print("=== Recherche a facettes ===");

const result = db.products.aggregate([
  {
    $facet: {
      // Nombre de produits par marque
      brands: [
        { $match: { brand: { $exists: true, $ne: null } } },
        { $group: { _id: "$brand", count: { $sum: 1 } } },
        { $sort: { count: -1, _id: 1 } }
      ],

      // Nombre de produits par tranche de prix
      price_ranges: [
        { $match: { price: { $type: "decimal" } } },
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

      // Nombre de produits par tranche de note
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
]).toArray();

printjson(result);