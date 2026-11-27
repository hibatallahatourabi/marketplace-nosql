# Marketplace NoSQL Project

Multi-Category Product Catalog for an Online Marketplace.

This repository contains the work developed by the project team.

## Search & Categories — Member 2

This module implements product search and hierarchical category management using MongoDB and mongosh.

The module has been successfully validated locally and integrated into the shared MongoDB Atlas database.

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
- Experimental comparison of hierarchical category query strategies.
- Automated and reproducible local tests.
- MongoDB Atlas integration and validation.
- Storage overhead and quota analysis.

### Requirements

- MongoDB Community Server for local validation.
- MongoDB Shell (mongosh).
- Authorized MongoDB Atlas access for shared database integration.
- Python 3.12 and ijson 3.6.0 for the standalone dataset origin analysis only.

### Module structure

```
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
├── dataset_origin_validation.md
└── atlas_validation.md
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

The final Atlas dataset was also verified against the local product identifiers, with no missing or additional IDs.

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

All selected products belong to the official Beauty and Personal Care source category according to the ASIN mapping.

The recommended review dataset is Beauty_and_Personal_Care.jsonl.gz. Actual review compatibility is handled separately by the team and is not established by this mapping analysis.

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

The eight invalid-filter and nonexistent-category checks were also successfully executed on MongoDB Atlas.

Atlas validation: 8 passed, 0 failed.

The fixture-based test suite remains restricted to dedicated local test databases.

### Local search performance benchmark

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

### Local hierarchy performance benchmark

Parent References using $graphLookup were compared with direct Ancestors Array queries.

| Metric | Parent References | Ancestors Array |
|---|---:|---:|
| Average execution time | 8.4 ms | 4.4 ms |
| Median execution time | 8 ms | 4 ms |
| Returned descendants | 564 | 564 |

Both methods returned identical descendant identifiers.

Ancestors Array reduced average execution time by 47.62% for the selected category.

These results support the hybrid hierarchy model.

### MongoDB Atlas validation

The module was successfully integrated into the shared marketplace_db database on November 27, 2026.

Environment:

- MongoDB Atlas Free Tier (M0).
- MongoDB 8.0.39.
- Mongosh 2.14.0.
- AWS Paris (eu-west-3).

#### Integration results

| Indicator | Result |
|---|---:|
| Total products | 5,000 |
| Unique product IDs | 5,000 |
| Total categories | 1,470 |
| Unique category IDs | 1,470 |
| Products indexes | 8 |
| Categories indexes | 4 |
| Preserved backup products | 117,000 |
| Invalid-filter tests passed | 8/8 |

Category synchronization was executed twice.

The first execution inserted 1,470 categories. The second execution inserted no new categories and left all 1,470 categories unchanged, confirming sequential idempotence.

Multi-criteria search, faceted search and hierarchical navigation were successfully validated on Atlas.

#### Atlas search performance

| Metric | Automatic plan | Forced compound index | Collection scan |
|---|---:|---:|---:|
| Execution time | 80 ms | 13 ms | 12 ms |
| Documents examined | 2,368 | 1,472 | 5,000 |
| Index keys examined | 2,368 | 3,885 | 0 |
| Products returned | 428 | 428 | 428 |

The compound index reduced document examination by 70.56% compared with the collection scan.

It also reduced execution time by 83.75% compared with the automatic plan in this execution.

These Atlas measurements represent one execution per strategy and should not be interpreted as average application response times.

#### Atlas hierarchy performance

Two benchmark series of five executions were performed.

| Metric | Parent References | Ancestors Array |
|---|---:|---:|
| First series mean | 110.4 ms | 231.4 ms |
| Second series mean | 104.6 ms | 101.4 ms |
| Overall mean | 107.5 ms | 166.4 ms |
| Overall median | 104.5 ms | 99.5 ms |
| Returned descendants | 564 | 564 |
| Identical result sets | 10/10 | 10/10 |

An unusually high measurement of 766 ms affected the first Ancestors Array series.

All original measurements were retained. The exact cause of this variation could not be established.

Remote hierarchy measurements include client-side retrieval and network communication.

The overall median slightly favors Ancestors Array, although both methods showed similar performance during the second benchmark series.

#### Atlas storage analysis

| Collection | Documents | Total allocated storage |
|---|---:|---:|
| products | 5,000 | 9.813 MiB |
| categories | 1,470 | 0.875 MiB |
| products_backup_117000 | 117,000 | 180.504 MiB |

The measured additional allocated storage associated with the Search & Categories integration was approximately 1.121 MiB.

The Atlas Logical Size metric was visually estimated at approximately 410 MB after integration, remaining below the 512 MB quota.

The quota value is an approximate graphical reading. Allocated collection storage and Atlas Logical Size are different metrics.

The shared backup collection was preserved.

See [Atlas Validation Report](docs/atlas_validation.md) for detailed results, limitations and reproduction instructions.

### Integration status

As of November 27, 2026:

- [x] Product schema compatibility checked.
- [x] Final 5,000-product dataset validated locally.
- [x] Official product source category confirmed.
- [x] Local category synchronization validated.
- [x] Local index compatibility validated.
- [x] All 43 local automated checks passed.
- [x] Final shared product dataset imported by the Product Catalog member.
- [x] Local and Atlas product identifiers verified.
- [x] Shared search indexes integrated.
- [x] Shared category hierarchy synchronized.
- [x] Sequential synchronization idempotence verified.
- [x] Atlas multi-criteria search validated.
- [x] Atlas faceted search validated.
- [x] Atlas hierarchical navigation validated.
- [x] Atlas search benchmark completed.
- [x] Atlas hierarchy benchmark completed.
- [x] All eight Atlas invalid-filter and nonexistent-category checks passed.
- [x] Final data integrity verified.
- [x] Storage overhead measured.
- [x] Atlas quota checked.
- [x] Existing backup preserved.

The Search & Categories module is technically complete and ready for team-level integration.

Review compatibility and the remaining project modules are managed separately by the corresponding team members.

### Safety

- Dataset JSON files are excluded from Git.
- Database credentials must not be committed to Git.
- The local import script requires an empty dedicated local products collection.
- Seed scripts reset dedicated test collections.
- Run seed scripts and the fixture-based test suite only on dedicated local MongoDB test databases.
- Never run local import or fixture seeding scripts on the shared Atlas database.
- Shared index creation and category synchronization require team approval and storage verification.
- Existing compatible indexes are reused.
- The validated search, hierarchy, benchmark and invalid-filter scripts are read-only.
- Obsolete categories are not automatically deleted.
- Backup collections must not be deleted without team authorization.

### Documentation

- [Search Design](docs/search_design.md)
- [Category Design](docs/category_design.md)
- [Final Local Validation Report](docs/final_validation.md)
- [Dataset Origin Validation](docs/dataset_origin_validation.md)
- [Atlas Validation Report](docs/atlas_validation.md)

See the local and Atlas validation reports for detailed results, limitations and reproduction instructions.