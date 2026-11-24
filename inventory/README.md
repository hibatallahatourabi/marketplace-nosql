# Inventory, Stock and Price History

**Member 4 — Aya**

## Objective

This module manages product stock, price updates, and price history for the MongoDB marketplace.

## Main functionalities

- Check available stock for a product.
- Increase and decrease product stock.
- Prevent stock from becoming negative.
- Update product prices.
- Record the history of price changes.
- Handle concurrent stock updates safely.
- Create indexes and evaluate query performance.
- Discuss replication, sharding, and the CAP theorem.

## Integration

Database: `marketplace_db`

Main product collection: `products`

Proposed collections:
- `inventory`
- `price_history`

All collections will be linked using the common `product_id` field.

## Technologies

- MongoDB Atlas
- MongoDB Shell (mongosh)
- Python with PyMongo for application code
- GitHub

