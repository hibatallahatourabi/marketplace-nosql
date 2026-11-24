
/*
 * Member 4 — Stock Tests
 * mongosh / JavaScript
 *
 * Uses a temporary test collection.
 * DO NOT execute against marketplace_db.inventory.
 */

// Execute only in a designated test database.
const testDb = db.getSiblingDB("marketplace_aya_test");
const inventory = testDb.inventory_tests;

// Prepare an isolated test document
inventory.deleteMany({ product_id: "TEST001" });

inventory.insertOne({
  product_id: "TEST001",
  quantity: 20,
  reserved: 3
});

// Test 1 — Check available stock
printjson(inventory.findOne({
  product_id: "TEST001"
}));

// Test 2 — Add 5 units
printjson(inventory.updateOne(
  { product_id: "TEST001" },
  { $inc: { quantity: 5 } }
));

// Test 3 — Sell 2 units safely
printjson(inventory.updateOne(
  {
    product_id: "TEST001",
    $expr: {
      $gte: [
        { $subtract: ["$quantity", "$reserved"] },
        2
      ]
    }
  },
  { $inc: { quantity: -2 } }
));

// Test 4 — Try to sell more than available
printjson(inventory.updateOne(
  {
    product_id: "TEST001",
    $expr: {
      $gte: [
        { $subtract: ["$quantity", "$reserved"] },
        100
      ]
    }
  },
  { $inc: { quantity: -100 } }
));

// Verify final inventory
printjson(inventory.findOne({
  product_id: "TEST001"
}));
