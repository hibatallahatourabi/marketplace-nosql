
/*
 * Member 4 — Concurrent Stock Updates
 * MongoDB Shell (mongosh)
 *
 * Demonstration of atomic conditional updates.
 * Use only in an authorized test environment.
 */

const testDb = db.getSiblingDB("marketplace_aya_test");
const stock = testDb.concurrency_tests;

// Prepare one simulated product
stock.updateOne(
  { product_id: "CONCURRENT_TEST" },
  {
    $set: {
      quantity: 1,
      reserved: 0
    }
  },
  { upsert: true }
);

// Client A attempts to buy 1 unit
const clientA = stock.updateOne(
  {
    product_id: "CONCURRENT_TEST",
    quantity: { $gte: 1 }
  },
  {
    $inc: { quantity: -1 }
  }
);

// Client B attempts to buy 1 unit
const clientB = stock.updateOne(
  {
    product_id: "CONCURRENT_TEST",
    quantity: { $gte: 1 }
  },
  {
    $inc: { quantity: -1 }
  }
);

print("Client A:");
printjson(clientA);

print("Client B:");
printjson(clientB);

print("Final stock:");
printjson(stock.findOne({
  product_id: "CONCURRENT_TEST"
}));
