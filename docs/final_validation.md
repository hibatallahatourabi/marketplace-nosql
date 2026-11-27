# Search & Categories — Final Validation

## 1. Environment

- Database: MongoDB Community Edition 9.0.4
- Shell: mongosh 2.14.0
- Implementation: JavaScript with mongosh
- Local database: `marketplace_real_test`
- Branch: `feature/search-categories`

## 2. Final dataset

The final shared dataset contains 5,000 products.

| Metric | Result |
|---|---:|
| Total products | 5,000 |
| Unique product IDs | 5,000 |
| Duplicate product IDs | 0 |
| Unique category paths | 574 |
| Invalid category paths | 0 |
| Missing main categories | 39 |
| Null prices | 2,545 |
| Decimal128 prices | 2,455 |

Missing main categories are derived from the first element of the validated category path without modifying the original product documents.
### Dataset origin validation

The official Amazon Reviews 2023 ASIN-to-category mapping was analyzed using a standalone Python utility with streaming JSON parsing.

| Metric | Result |
|---|---:|
| Mapping entries scanned | 35,393,189 |
| Products analyzed | 5,000 |
| Matched product IDs | 5,000 |
| Unmatched product IDs | 0 |
| Match rate | 100% |
| Beauty and Personal Care | 5,000 |
| All Beauty | 0 |

All 5,000 products belong to the official Beauty and Personal Care source category.

The internal category.main field must not be confused with the official source category.

Actual review compatibility remains pending validation.

See [Dataset Origin Validation](dataset_origin_validation.md) for the methodology and reproduction instructions.

## 3. Category synchronization

The categories collection uses a hybrid hierarchy model combining Parent References and Ancestors Array.

| Metric | Result |
|---|---:|
| Generated categories | 1,470 |
| Inserted categories | 1,470 |
| Skipped products | 0 |
| Derived main categories | 39 |

Category identifiers are generated from the complete category path and main category namespace.

Synchronization uses batched bulkWrite operations with upsert to avoid duplicate categories during repeated sequential executions.

## 4. Search and dynamic facets

The module supports filtering by:

- Main category
- Category path and descendants
- Brand
- Minimum and maximum price
- Minimum rating

Dynamic facets are computed using an aggregation pipeline containing `$match`, `$facet`, `$group`, `$bucket` and `$count`.

### Real dataset validation

Selected criteria:

- Main category: All Beauty
- Path: Beauty & Personal Care / Hair Care
- Price: 0–100
- Minimum rating: 4

| Result | Count |
|---|---:|
| Matching products | 428 |
| Price range [0, 50) | 401 |
| Price range [50, 100) | 27 |
| Missing prices | 0 |
| Rating bucket [4, 5.01) | 428 |

## 5. Index strategy

Product indexes:

- product_id — unique
- brand
- price
- rating.average
- category.main
- category.path
- Compound index: category.main, price, rating.average

Category indexes:

- category_id — unique
- parent_id
- ancestors

Existing compatible indexes are reused. Incompatible index specifications generate an explicit error. No existing indexes are automatically deleted.

## 6. Search performance benchmark

Five executions were performed using MongoDB explain execution statistics.

All three execution strategies returned 428 products.

| Execution | Automatic plan | Compound index | Collection scan |
|---|---:|---:|---:|
| 1 | 54 ms | 10 ms | 10 ms |
| 2 | 61 ms | 11 ms | 12 ms |
| 3 | 62 ms | 11 ms | 8 ms |
| 4 | 62 ms | 10 ms | 9 ms |
| 5 | 56 ms | 11 ms | 8 ms |
| Average | 59 ms | 10.6 ms | 9.4 ms |
| Median | 61 ms | 11 ms | 9 ms |

| Metric | Automatic plan | Compound index | Collection scan |
|---|---:|---:|---:|
| Documents examined | 2,368 | 1,472 | 5,000 |
| Index keys examined | 2,368 | 3,885 | 0 |
| Returned products | 428 | 428 | 428 |

The compound index reduces examined documents by 70.56% compared with a collection scan and reduces execution time by 82.03% compared with the automatic plan.

However, the collection scan remains slightly faster on this relatively small dataset. Index traversal overhead and query complexity may explain this result.

## 7. Hierarchy performance benchmark

Parent References using `$graphLookup` were compared with direct Ancestors Array queries.

The benchmark includes warm-up executions, alternating measurement order and verification of returned category identifiers.

| Execution | Parent References | Ancestors Array |
|---|---:|---:|
| 1 | 8 ms | 4 ms |
| 2 | 8 ms | 5 ms |
| 3 | 9 ms | 4 ms |
| 4 | 8 ms | 5 ms |
| 5 | 9 ms | 4 ms |
| Average | 8.4 ms | 4.4 ms |

Both methods returned exactly the same 564 descendants during all five executions.

Ancestors Array reduced the average execution time by 47.62%, providing an acceleration factor of approximately 1.91.

These results support the selected hybrid hierarchy model.

## 8. Automated tests

| Test suite | Passed | Failed |
|---|---:|---:|
| Search and Categories | 35 | 0 |
| Invalid Filters | 8 | 0 |
| Total | 43 | 0 |

Tests cover search filters, facets, category hierarchy, category synchronization, index compatibility, missing main categories, invalid numeric filters and nonexistent category identifiers.

## 9. Reproduction

Place the final dataset in:

`data/beauty_products_final_5000.json`

Run the following commands from the repository root using PowerShell.

```powershell
mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/validate_dataset.js

mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/import_dataset.js

mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/search_indexes.js

mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/sync_categories.js

mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/search_products.js

mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/facet_search.js

mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/category_hierarchy.js

mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/search_benchmark.js

mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/hierarchy_benchmark.js

mongosh "mongodb://localhost:27017/marketplace_real_test" --file mongosh/test_invalid_filters.js
```

To reproduce the isolated automated tests:

```powershell
mongosh "mongodb://localhost:27017/marketplace_search_test" --file mongosh/seed_tests.js

mongosh "mongodb://localhost:27017/marketplace_search_test" --file mongosh/test_search.js
```

The import script requires an empty local products collection. Seed scripts must only be executed on dedicated local test databases.

## 10. Limitations

- Performance measurements depend on dataset size, query selectivity and execution environment.
- Search explain statistics do not represent complete application latency.
- Search benchmark consistency checks compare result counts rather than product identifiers.
- Hierarchy performance results concern the selected category.
- Dynamic facets use all selected filters simultaneously.
- Automated tests do not provide exhaustive input validation coverage.
- Synchronization does not automatically remove obsolete categories.
- Dataset files are excluded from Git.

## 11. Atlas integration status

As of November 27, 2026:

- The original shared products collection contained 117,000 products during the previous read-only verification.
- The final 5,000-product dataset has been validated locally.
- A temporary import into products_import_test_5000 was reported successful by the Product Catalog member.
- The official source category has been confirmed as Beauty and Personal Care for all 5,000 products.
- Actual compatibility with the corresponding review dataset remains pending validation.
- Final replacement of the shared products collection remains pending team approval.
- Available Atlas cluster storage must be verified before deployment.
- Shared index creation and category synchronization remain pending.
- Final integration tests must be performed after the approved dataset replacement.

No Atlas data or indexes have been modified by the Search & Categories module during this validation phase.

## 12. Conclusion

The Search & Categories module has been implemented and validated locally using mongosh and the final shared dataset.

The module provides multicriteria search, dynamic faceted search, hierarchical category navigation, category synchronization, index management and reproducible performance benchmarks.

Shared Atlas deployment remains pending team coordination.