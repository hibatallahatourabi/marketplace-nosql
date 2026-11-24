
/*
 * Member 4 — Validation Queries
 * TP 3.2 / TP 3.3 style
 *
 * Read-only checks for marketplace_db.
 */

const database = db.getSiblingDB("marketplace_db");

print("=== 1. VERIFY COLLECTIONS ===");
printjson(database.getCollectionNames());

print("=== 2. COUNT PRODUCTS ===");
print(database.products.countDocuments({}));

print("=== 3. COUNT INVENTORY RECORDS ===");
print(database.inventory.countDocuments({}));

print("=== 4. COUNT PRICE HISTORY RECORDS ===");
print(database.price_history.countDocuments({}));

print("=== 5. CHECK A PRODUCT'S STOCK ===");
printjson(
  database.inventory.findOne({
    product_id: "B08BLDKYHB"
  })
);

print("=== 6. CHECK PRICE HISTORY ===");
printjson(
  database.price_history
    .find({ product_id: "B0BWJGQ32Y" })
    .sort({ changed_at: -1 })
    .toArray()
);

print("=== 7. CHECK INVENTORY INDEXES ===");
printjson(database.inventory.getIndexes());

print("=== 8. CHECK PRICE HISTORY INDEXES ===");
printjson(database.price_history.getIndexes());
