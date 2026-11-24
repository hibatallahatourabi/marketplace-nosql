
/*
 * Member 4 — Stock Operations
 * MongoDB Shell (mongosh)
 *
 * WARNING: These are demonstration functions.
 * Do not execute stock modifications until authorized.
 */

use("marketplace_db");

const inventory = db.inventory;

// Q1. Read current stock
function checkStock(productId) {
  return inventory.findOne(
    { product_id: productId },
    { _id: 0, product_id: 1, quantity: 1, reserved: 1 }
  );
}

// Q2. Add stock after restocking
function addStock(productId, amount) {
  if (!Number.isInteger(amount) || amount <= 0) {
    throw new Error("Amount must be a positive integer");
  }

  return inventory.updateOne(
    { product_id: productId },
    {
      $inc: { quantity: amount },
      $currentDate: { last_updated: true }
    }
  );
}

// Q3. Remove stock safely
function removeStock(productId, amount) {
  if (!Number.isInteger(amount) || amount <= 0) {
    throw new Error("Amount must be a positive integer");
  }

  return inventory.updateOne(
    {
      product_id: productId,
      $expr: {
        $gte: [
          { $subtract: ["$quantity", "$reserved"] },
          amount
        ]
      }
    },
    {
      $inc: { quantity: -amount },
      $currentDate: { last_updated: true }
    }
  );
}

// Q4. Example (read-only)
// printjson(checkStock("B08BLDKYHB"));

// Do not call addStock() or removeStock()
// on the shared database without authorization.
