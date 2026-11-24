
/*
 * Member 4 — Price History Benchmark
 * TP-style performance analysis
 *
 * Read-only: does not modify data.
 */

use("marketplace_db");

const productId = "B0BWJGQ32Y";

// Q1. Explain the query execution
const result = db.price_history
  .find({ product_id: productId })
  .sort({ changed_at: -1 })
  .explain("executionStats");

printjson({
  executionTimeMillis:
    result.executionStats.executionTimeMillis,

  totalDocsExamined:
    result.executionStats.totalDocsExamined,

  totalKeysExamined:
    result.executionStats.totalKeysExamined,

  winningPlan:
    result.queryPlanner.winningPlan
});
// Q2. Compare with a natural collection scan
const withoutIndex = db.price_history
  .find({ product_id: productId })
  .sort({ changed_at: -1 })
  .hint({ $natural: 1 })
  .explain("executionStats");

printjson({
  executionTimeMillis:
    withoutIndex.executionStats.executionTimeMillis,
  totalDocsExamined:
    withoutIndex.executionStats.totalDocsExamined,
  totalKeysExamined:
    withoutIndex.executionStats.totalKeysExamined
});
