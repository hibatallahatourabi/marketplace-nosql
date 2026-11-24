
/*
 TP-style MongoDB queries
 Member 4 — Price History Analysis

 Read-only: does not modify any product or price.
*/

use("marketplace_db");

const productId = "B0BWJGQ32Y";

// Q1. Show all price changes for one product
db.price_history.find(
  { product_id: productId }
).sort({ changed_at: -1 });

// Q2. Count the price changes
db.price_history.countDocuments({
  product_id: productId
});

// Q3. Show the most recent price change
db.price_history.findOne(
  { product_id: productId },
  { _id: 0, old_price: 1, new_price: 1, changed_at: 1 },
  { sort: { changed_at: -1 } }
);

// Q4. Find all price increases
db.price_history.aggregate([
  {
    $match: {
      product_id: productId
    }
  },
  {
    $match: {
      $expr: {
        $gt: ["$new_price", "$old_price"]
      }
    }
  },
  {
    $sort: { changed_at: -1 }
  }
]);

// Q5. Count price changes per product
db.price_history.aggregate([
  {
    $group: {
      _id: "$product_id",
      number_of_changes: { $sum: 1 }
    }
  },
  {
    $sort: { number_of_changes: -1 }
  }
]);
