
/*
 * Member 4 — Distribution Analysis
 * MongoDB Shell (mongosh)
 *
 * Observation only.
 * Does not change cluster configuration.
 */

use("marketplace_db");

// Q1. Identify the MongoDB deployment
print("=== SERVER INFORMATION ===");
printjson(db.hello());

// Q2. Observe available replica-set information
print("=== REPLICA SET ===");
try {
  printjson(rs.status());
} catch (e) {
  print("Replica-set status unavailable: " + e.message);
}

// Q3. Check whether the deployment is sharded
print("=== SHARDING INFORMATION ===");
try {
  printjson(db.adminCommand({ listShards: 1 }));
} catch (e) {
  print("Shard information unavailable: " + e.message);
}

// Q4. Show inventory indexes
print("=== INVENTORY INDEXES ===");
printjson(db.inventory.getIndexes());
