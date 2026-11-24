
/*
 TP-style MongoDB operations
 Member 4 — Price History
 Read-only queries
*/

use("marketplace_db");

// Select a product with a known price
const productId = "B0BWJGQ32Y";

// 1. Read its current price
db.products.findOne(
  { product_id: productId },
  { _id: 0, product_id: 1, title: 1, price: 1 }
);

// 2. Read its price history
db.price_history.find(
  { product_id: productId }
).sort({ changed_at: -1 });
