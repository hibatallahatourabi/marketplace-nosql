# Price History — Data Modeling

## Objective

Store product price changes while keeping the current product price accessible in the `products` collection.

## Model A: Embedding

Price changes are stored in an array inside each product document.

**Advantages:**
- Product and price history can be read together.
- Updating the price and adding a history entry in the same document can be atomic.

**Disadvantages:**
- Product documents grow over time.
- Long histories increase document size and may eventually exceed MongoDB's 16 MB document limit.

## Model B: Referencing

Price changes are stored in a separate `price_history` collection.

Each history document contains:
- `product_id`
- `old_price`
- `new_price`
- `changed_at`

**Advantages:**
- History growth does not enlarge product documents.
- Historical records can be queried and indexed independently.
- Suitable for products with many price changes.

**Disadvantages:**
- Retrieving a product and its history requires multiple queries or `$lookup`.
- Updating the current price and recording its history requires coordinated writes, preferably a MongoDB transaction.

## Final Decision

We selected **Model B: Referencing**.

The `products` collection stores the current price, while `price_history` stores historical changes linked by `product_id`.

A compound index on `{ product_id: 1, changed_at: -1 }` supports efficient retrieval of recent price changes.

This choice is motivated by document growth, query patterns, and separation of responsibilities between the catalogue and price-history modules.

## Integration

Database: `marketplace_db`

Collections:
- `products`
- `price_history`

Current prices use MongoDB Decimal128. Price-history records must also use Decimal128 and native Date values.

The implementation and performance measurements will be validated against the shared database.
