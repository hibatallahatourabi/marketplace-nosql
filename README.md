# Marketplace NoSQL Project

Multi-Category Product Catalog for an Online Marketplace.

This repository contains the work developed by the project team.

## Search & Categories — Member 2

This module implements product search and category management using MongoDB and mongosh.

### Features

- Multi-criteria product search (category, brand, price, rating).
- Faceted search using MongoDB aggregation.
- Hierarchical category management using `parent_id` and `ancestors`.
- MongoDB indexes for search optimization.
- Query performance comparison using `explain("executionStats")`.
- Automated tests using mongosh.

### Requirements

- MongoDB Community Server
- MongoDB Shell (mongosh)

### Run the scripts

```powershell
mongosh "mongodb://localhost:27017/marketplace_db" --file mongosh/search_indexes.js
mongosh "mongodb://localhost:27017/marketplace_db" --file mongosh/search_products.js
mongosh "mongodb://localhost:27017/marketplace_db" --file mongosh/facet_search.js
mongosh "mongodb://localhost:27017/marketplace_db" --file mongosh/category_hierarchy.js
mongosh "mongodb://localhost:27017/marketplace_db" --file mongosh/search_benchmark.js
```

### Run the tests

```powershell
mongosh "mongodb://localhost:27017/marketplace_db" --file mongosh/test_search.js
```

The scripts have been tested using a local demonstration database. Integration with the team's complete dataset remains to be validated.

### Documentation

- `docs/search_design.md`
- `docs/category_design.md`