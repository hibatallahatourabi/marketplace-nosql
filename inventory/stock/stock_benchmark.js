
/*
 * Member 4 — Inventory Performance Benchmark
 * TP 3.3 style: explain("executionStats")
 *
 * Read-only: no stock modification.
 */

use("marketplace_db");

const productId = "B08BLDKYHB";

// Q1 — Search WITH the inventory index
const withIndex = db.inventory
  .find({ product_id: productId })
  .hint("idx_inventory_product_id")
  .explain("executionStats");

print("=== WITH INDEX ===");

printjson({
  executionTimeMillis:
    withIndex.executionStats.executionTimeMillis,

  totalDocsExamined:
    withIndex.executionStats.totalDocsExamined,

  totalKeysExamined:
    withIndex.executionStats.totalKeysExamined
});

// Q2 — Search WITHOUT the inventory index
const withoutIndex = db.inventory
  .find({ product_id: productId })
  .hint({ $natural: 1 })
  .explain("executionStats");

print("=== WITHOUT INDEX ===");

printjson({
  executionTimeMillis:
    withoutIndex.executionStats.executionTimeMillis,

  totalDocsExamined:
    withoutIndex.executionStats.totalDocsExamined,

  totalKeysExamined:
    withoutIndex.executionStats.totalKeysExamined
});
