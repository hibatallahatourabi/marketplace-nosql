# Replication, Sharding and CAP — Inventory Module

## 1. Replication

MongoDB replica sets maintain multiple copies of data.

The primary member accepts writes, while secondary members replicate changes. If the primary becomes unavailable, an eligible secondary can be elected as the new primary.

**Marketplace relevance:** Replication helps maintain service availability and data durability.

For critical stock operations, majority write concern can be used to improve durability across replica-set members.

## 2. Sharding

Sharding distributes a collection's data across multiple shards.

This is useful when the product catalogue and inventory grow beyond the capacity of a single server.

A possible inventory shard key is a hashed `product_id`, because stock operations usually target individual products by identifier.

However, the choice must be evaluated against query patterns, uniqueness constraints, and data distribution. Sharding is not necessary for the current three-product sample.

## 3. CAP Theorem

The CAP theorem concerns distributed systems during network partitions.

- **Consistency:** Clients observe a consistent view of the data.
- **Availability:** Every request receives a non-error response.
- **Partition tolerance:** The system continues to operate despite communication failures between nodes.

During a network partition, a MongoDB replica set with majority-based writes prioritizes consistency over accepting writes on a partition that lacks a majority.

For stock management, preventing inconsistent stock updates is more important than accepting every purchase during a network failure.

## 4. Application to Inventory

Stock updates use atomic conditional operations such as `$inc` and quantity checks.

The system should reject purchases when the available quantity is insufficient.

Replication improves resilience, while careful consistency settings reduce the risk of acknowledging stock changes that could be lost during failover.

## 5. Experimental Limitations

The team's current Atlas deployment must be inspected before making claims about its actual replication topology.

No sharding configuration or network partition experiment has yet been performed. The above discussion is an architectural analysis, not a verified benchmark.
