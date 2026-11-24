
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


/*
 * Price change using a MongoDB transaction.
 * Preparation only — do not execute on the shared database yet.
 */

function changeProductPrice(productId, newPrice) {
  const session = db.getMongo().startSession();

  try {
    const database = session.getDatabase("marketplace_db");
    const products = database.products;
    const history = database.price_history;

    session.withTransaction(() => {
      const product = products.findOne({
        product_id: productId
      });

      if (!product) {
        throw new Error("Product not found");
      }

      const oldPrice = product.price;

      if (oldPrice == null) {
        throw new Error("Current price is missing");
      }

      const result = products.updateOne(
        {
          product_id: productId,
          price: oldPrice
        },
        {
          $set: { price: NumberDecimal(newPrice) }
        }
      );

      if (result.matchedCount !== 1) {
        throw new Error("Price was changed concurrently");
      }

      history.insertOne({
        product_id: productId,
        old_price: oldPrice,
        new_price: NumberDecimal(newPrice),
        changed_at: new Date()
      });
    });

    print("Price changed successfully");
  } finally {
    session.endSession();
  }
}

// Example — DO NOT EXECUTE YET:
// changeProductPrice("B0BWJGQ32Y", "49.99");

