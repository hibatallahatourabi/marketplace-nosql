# Marketplace NoSQL Project

Multi-Category Product Catalog for an Online Marketplace.

This repository contains the work developed by the project team.

## Search & Categories — Member 2

This module implements product search and hierarchical category management using MongoDB and mongosh.

### Features

- Multi-criteria search by category, brand, price and rating.
- Dynamic faceted search using MongoDB aggregation.
- Handling of missing prices and missing main categories.
- Validation of numeric filters in faceted search.
- Hierarchical categories using Parent References and Ancestors Array.
- Stable category identifiers based on complete category paths.
- Batched category synchronization using bulkWrite and upsert.
- Compatibility with existing product indexes.
- Simple and compound index management.
- Query performance comparison using explain("executionStats").
- Experimental comparison of hierarchical category models.
- Automated and reproducible local tests.

### Requirements

- MongoDB Community Server
- MongoDB Shell (mongosh)
- Python 3.12 and ijson 3.6.0 for the standalone dataset origin analysis only.

### Module structure

```text
mongosh/
├── search_products.js
├── facet_search.js
├── category_hierarchy.js
├── sync_categories.js
├── search_indexes.js
├── search_benchmark.js
├── hierarchy_benchmark.js
├── seed_benchmark.js
├── seed_tests.js
├── test_search.js
├── test_invalid_filters.js
├── validate_dataset.js
└── import_dataset.js

tools/
└── analyze_dataset_origin.py

docs/
├── search_design.md
├── category_design.md
├── final_validation.md
└── dataset_origin_validation.md
```

### Dataset validation

The module was validated locally using the final shared dataset.

| Metric | Result |
|---|---:|
| Total products | 5,000 |
| Unique product IDs | 5,000 |
| Duplicate IDs | 0 |
| Unique category paths | 574 |
| Invalid category paths | 0 |
| Missing main categories | 39 |
| Null prices | 2,545 |
| Decimal128 prices | 2,455 |
| Generated categories | 1,470 |

Missing main categories are derived from the first element of the validated category path without modifying the original product documents.

### Dataset origin validation

The official Amazon Reviews 2023 ASIN-to-category mapping was analyzed using a standalone Python utility and streaming JSON parsing.

| Metric | Result |
|---|---:|
| Mapping entries scanned | 35,393,189 |
| Products analyzed | 5,000 |
| Matched IDs | 5,000 |
| Unmatched IDs | 0 |
| Match rate | 100% |
| Beauty and Personal Care | 5,000 |
| All Beauty | 0 |

All selected products belong to the official Beauty and Personal Care source category.

The recommended review dataset is Beauty_and_Personal_Care.jsonl.gz. Actual review compatibility remains pending validation.

See [Dataset Origin Validation](docs/dataset_origin_validation.md).

### Automated tests

Run from the repository root using a local MongoDB server.

Prepare the dedicated test databases:

```powershell
mongosh "mongodb://localhost:27017/marketplace_search_test" --file mongosh/seed_tests.js
```

Run the main test suite:

```powershell
mongosh "mongodb://localhost:27017/marketplace_search_test" --file mongosh/test_search.js
```

After preparing the local real dataset and categories, run the additional validation tests:

```powershell
mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/test_invalid_filters.js
```

| Test group | Passed |
|---|---:|
| Product search | 8 |
| Faceted search | 4 |
| Category hierarchy | 6 |
| Category synchronization | 3 |
| MongoDB indexes | 7 |
| Missing main categories | 7 |
| Invalid filters and nonexistent category checks | 8 |
| Total | 43 |

Local validation: 43 passed, 0 failed.

### Search performance benchmark

Five executions were performed using the final 5,000-product dataset.

| Metric | Automatic plan | Forced compound index | Collection scan |
|---|---:|---:|---:|
| Average execution time | 59 ms | 10.6 ms | 9.4 ms |
| Median execution time | 61 ms | 11 ms | 9 ms |
| Documents examined | 2,368 | 1,472 | 5,000 |
| Index keys examined | 2,368 | 3,885 | 0 |
| Products returned | 428 | 428 | 428 |

The forced compound index reduced examined documents by 70.56% compared with a collection scan.

It also reduced average execution time by 82.03% compared with the automatic plan.

However, the collection scan remained slightly faster than the forced compound index on this relatively small dataset.

### Hierarchy performance benchmark

Parent References using $graphLookup were compared with direct Ancestors Array queries.

| Metric | Parent References | Ancestors Array |
|---|---:|---:|
| Average execution time | 8.4 ms | 4.4 ms |
| Median execution time | 8 ms | 4 ms |
| Returned descendants | 564 | 564 |

Both methods returned identical descendant identifiers.

Ancestors Array reduced average execution time by 47.62% for the selected category.

These results support the hybrid hierarchy model.

### Integration status

As of November 27, 2026:

- Product schema compatibility checked.
- Initial read-only queries validated on MongoDB Atlas.
- Final 5,000-product dataset validated locally.
- Product source category confirmed.
- Category synchronization validated locally.
- Index compatibility validated locally.
- Temporary Atlas import of 5,000 products reported successful by the Product Catalog member.
- Review compatibility pending validation.
- Final replacement of the shared products collection pending team approval.
- Shared category synchronization and index creation pending.
- Final integration tests pending.

No Atlas data or indexes have been modified by the Search & Categories module.

### Safety

- Dataset JSON files are excluded from Git.
- The local import script requires an empty dedicated local products collection.
- Seed scripts reset dedicated test collections.
- Run seed and automated test scripts only on local MongoDB test databases, never on the shared Atlas database.
- Shared index creation and category synchronization require team approval and storage verification.
- Existing compatible indexes are reused.
- Obsolete categories are not automatically deleted.

### Documentation

- [Search Design](docs/search_design.md)
- [Category Design](docs/category_design.md)
- [Final Validation Report](docs/final_validation.md)
- [Dataset Origin Validation](docs/dataset_origin_validation.md)

See the Final Validation Report for detailed results, limitations and reproduction instructions.