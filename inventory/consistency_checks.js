
/*
 * Member 4 — Data Consistency Checks
 * MongoDB Shell (mongosh)
 *
 * Read-only checks.
 */

const database = db.getSiblingDB("marketplace_db");

// Q1 — Inventory records without a matching product
print("=== INVENTORY WITHOUT PRODUCT ===");

printjson(
  database.inventory.aggregate([
    {
      $lookup: {
        from: "products",
        localField: "product_id",
        foreignField: "product_id",
        as: "matching_product"
      }
    },
    {
      $match: {
        matching_product: { $size: 0 }
      }
    },
    {
      $project: {
        _id: 0,
        product_id: 1
      }
    }
  ]).toArray()
);

// Q2 — Invalid stock quantities
print("=== INVALID STOCK ===");

printjson(
  database.inventory.find({
    $or: [
      { quantity: { $lt: 0 } },
      { reserved: { $lt: 0 } },
      {
        $expr: {
          $gt: ["$reserved", "$quantity"]
        }
      }
    ]
  }).toArray()
);

// Q3 — Price-history records without a product
print("=== PRICE HISTORY WITHOUT PRODUCT ===");

printjson(
  database.price_history.aggregate([
    {
      $lookup: {
        from: "products",
        localField: "product_id",
        foreignField: "product_id",
        as: "matching_product"
      }
    },
    {
      $match: {
        matching_product: { $size: 0 }
      }
    },
    {
      $project: {
        _id: 0,
        product_id: 1
      }
    }
  ]).toArray()
);
