# Marketplace NoSQL Project

Multi-Category Product Catalog for an Online Marketplace.

This repository contains the work developed by the project team.

## Search & Categories — Member 2

This module implements product search and hierarchical category management using MongoDB and mongosh.

### Features

- Multi-criteria search by category, brand, price and rating.
- Faceted search using MongoDB aggregation.
- Handling of missing and invalid prices.
- Hierarchical categories using parent references and ancestors arrays.
- Stable category identifiers based on complete category paths.
- Idempotent category synchronization using upsert.
- Compatibility with existing product indexes.
- Query performance comparison using explain("executionStats").
- Automated and reproducible local tests.

### Requirements

- MongoDB Community Server
- MongoDB Shell (mongosh)

### Module structure

```text
mongosh/
├── search_products.js
├── facet_search.js
├── category_hierarchy.js
├── sync_categories.js
├── search_indexes.js
├── search_benchmark.js
├── seed_benchmark.js
├── seed_tests.js
└── test_search.js

docs/
├── search_design.md
└── category_design.md
```

### Automated tests

Run from the repository root using a local MongoDB server.

Prepare the test databases:

```powershell
mongosh "mongodb://localhost:27017/marketplace_search_test" --file mongosh/seed_tests.js
```

Run the tests:

```powershell
mongosh "mongodb://localhost:27017/marketplace_search_test" --file mongosh/test_search.js
```

| Test group | Passed |
|---|---:|
| Product search | 8 |
| Faceted search | 4 |
| Category hierarchy | 6 |
| Category synchronization | 3 |
| MongoDB indexes | 7 |
| Total | 28 |

Local validation: 28 passed, 0 failed.

### Performance benchmark

Generate 10,000 synthetic products:

```powershell
mongosh "mongodb://localhost:27017/marketplace_benchmark_test" --file mongosh/seed_benchmark.js
```

Create indexes:

```powershell
mongosh "mongodb://localhost:27017/marketplace_benchmark_test" --file mongosh/search_indexes.js
```

Run the benchmark:

```powershell
mongosh "mongodb://localhost:27017/marketplace_benchmark_test" --file mongosh/search_benchmark.js
```

Results from five repeated executions:

| Metric | Automatic plan | Forced compound index | Without index |
|---|---:|---:|---:|
| Average execution time | 11.2 ms | 3.4 ms | 10.6 ms |
| Median execution time | 11 ms | 3 ms | 10 ms |
| Documents examined | 328 | 328 | 10000 |
| Index keys examined | 1223 | 1223 | 0 |
| Products returned | 221 | 221 | 221 |

The forced compound index reduced:

- Average execution time by 67.92%.
- Documents examined by 96.72%.

The automatic query planner also selected the compound index.

These measurements use synthetic local data and a fixed execution order. Performance must be confirmed on the real Amazon dataset.

### Integration status

- Product schema compatibility checked.
- Read-only search and facet queries validated on MongoDB Atlas.
- Category synchronization validated locally.
- Existing index compatibility validated locally.
- Shared Atlas database integration pending team approval.

### Safety

The seed scripts reset dedicated test collections.

Run seed and automated test scripts only on the local MongoDB server, never on the shared Atlas database.

### Documentation

- `docs/search_design.md`
- `docs/category_design.md`
