# Search & Categories — Final Local Validation

This report documents the local validation of the Search & Categories module and summarizes its subsequent integration into MongoDB Atlas.

For detailed remote validation results, see [Atlas Validation Report](atlas_validation.md).

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

All 5,000 products belong to the official Beauty and Personal Care source category according to the ASIN mapping.

The internal `category.main` field must not be confused with the official source category.

Actual review compatibility is managed separately by the team and is not established by this mapping analysis.

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

Synchronization uses batched `bulkWrite` operations with upsert to avoid duplicate categories during repeated sequential executions.

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

- `product_id` — unique
- `brand`
- `price`
- `rating.average`
- `category.main`
- `category.path`
- Compound index: `category.main`, `price`, `rating.average`

Category indexes:

- `category_id` — unique
- `parent_id`
- `ancestors`

Existing compatible indexes are reused. Incompatible index specifications generate an explicit error. No existing indexes are automatically deleted.

## 6. Local search performance benchmark

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

The compound index reduces examined documents by 70.56% compared with a collection scan and reduces average execution time by 82.03% compared with the automatic plan.

However, the collection scan remains slightly faster on this relatively small dataset. Index traversal overhead and query complexity may explain this result.

The results demonstrate reduced document examination but do not establish that the compound index is always faster.

## 7. Local hierarchy performance benchmark

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
| Median | 8 ms | 4 ms |

Both methods returned exactly the same 564 descendants during all five executions.

Ancestors Array reduced the average execution time by 47.62%, providing an acceleration factor of approximately 1.91.

These results support the selected hybrid hierarchy model for the tested workload.

The benchmark compares two query strategies within the same hybrid category collection rather than two independently stored category models.

## 8. Automated tests

### Local validation

| Test suite | Passed | Failed |
|---|---:|---:|
| Search and Categories | 35 | 0 |
| Invalid Filters | 8 | 0 |
| Total | 43 | 0 |

Tests cover search filters, facets, category hierarchy, category synchronization, index compatibility, missing main categories, invalid numeric filters and nonexistent category identifiers.

### Atlas validation

The eight invalid-filter and nonexistent-category checks were repeated successfully on MongoDB Atlas.

| Test suite | Passed | Failed |
|---|---:|---:|
| Invalid Filters | 8 | 0 |

The nonexistent category check verifies the absence of the specified category identifier rather than directly testing the exception handling of `category_hierarchy.js`.

The fixture-based test suite was executed only on dedicated local databases.

## 9. Local reproduction

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

The import script requires an empty dedicated local products collection.

If the final dataset has already been imported and verified, skip the import command.

To reproduce the isolated automated tests:

```powershell
mongosh "mongodb://localhost:27017/marketplace_search_test" --file mongosh/seed_tests.js

mongosh "mongodb://localhost:27017/marketplace_search_test" --file mongosh/test_search.js
```

Seed scripts and fixture-based tests must only be executed on dedicated local test databases.

Never execute local import or fixture seeding scripts on the shared Atlas database.

## 10. Limitations

- Performance measurements depend on dataset size, query selectivity and execution environment.
- Search explain statistics do not represent complete application latency.
- Search benchmark consistency checks compare result counts rather than product identifiers.
- Hierarchy performance results concern the selected category.
- Hierarchy benchmarks compare two query strategies within the same hybrid category model.
- Remote hierarchy measurements include client-side retrieval and network communication.
- Dynamic facets use all selected filters simultaneously.
- Automated tests do not provide exhaustive input validation coverage.
- Synchronization does not automatically remove obsolete categories.
- Dataset files are excluded from Git.
- Results obtained with 5,000 products cannot be generalized to substantially larger datasets without additional testing.

## 11. Atlas integration status

As of November 27, 2026, the Search & Categories module has been successfully integrated into the shared MongoDB Atlas database.

### 11.1 Atlas environment

- Database: `marketplace_db`
- Platform: MongoDB Atlas Free Tier (M0)
- MongoDB version: 8.0.39
- Shell: mongosh 2.14.0
- Cloud provider: AWS
- Region: Paris (eu-west-3)

### 11.2 Integration and integrity

| Indicator | Final result |
|---|---:|
| Total products | 5,000 |
| Unique product IDs | 5,000 |
| Local product IDs missing on Atlas | 0 |
| Additional product IDs on Atlas | 0 |
| Total categories | 1,470 |
| Unique category IDs | 1,470 |
| Products indexes | 8 |
| Categories indexes | 4 |
| Preserved backup products | 117,000 |
| Invalid-filter tests passed | 8/8 |

The final product dataset was imported by the Product Catalog member before the Search & Categories integration.

The shared index creation and category synchronization were performed with team authorization.

Existing compatible product indexes were reused.

The first category synchronization inserted 1,470 categories.

The second synchronization inserted no new categories and left all 1,470 categories unchanged, confirming sequential idempotence.

The original product documents were not modified by the category synchronization.

The product identifier comparison confirmed that the local and Atlas datasets contained the same IDs. It did not compare every individual product field.

### 11.3 Functional validation

| Functionality | Result |
|---|---|
| Multi-criteria search | Validated |
| Faceted search | Validated |
| Missing main category fallback | Validated |
| Hierarchical category navigation | Validated |
| Category synchronization | Validated |
| Sequential synchronization idempotence | Validated |
| Search indexes | Validated |
| Invalid-filter checks | 8/8 passed |

The multi-criteria search returned four products for the selected Hair Care category with the derived main category.

The faceted search returned 428 matching products.

The hierarchical navigation returned eight categories, including the selected category, and four associated products.

### 11.4 Atlas search benchmark

| Metric | Automatic plan | Compound index | Collection scan |
|---|---:|---:|---:|
| Execution time | 80 ms | 13 ms | 12 ms |
| Documents examined | 2,368 | 1,472 | 5,000 |
| Index keys examined | 2,368 | 3,885 | 0 |
| Returned products | 428 | 428 | 428 |

The compound index reduced the number of examined documents by 70.56% compared with the collection scan.

It reduced execution time by 83.75% compared with the automatic plan in the recorded execution.

These Atlas measurements represent one execution per strategy, not average application response times.

### 11.5 Atlas hierarchy benchmark

Two series of five executions were performed.

| Metric | Parent References | Ancestors Array |
|---|---:|---:|
| First series mean | 110.4 ms | 231.4 ms |
| Second series mean | 104.6 ms | 101.4 ms |
| Overall mean | 107.5 ms | 166.4 ms |
| Overall median | 104.5 ms | 99.5 ms |
| Returned descendants | 564 | 564 |
| Identical result sets | 10/10 | 10/10 |

All ten comparisons returned identical descendant identifiers.

The first Ancestors Array series included an unusually high measurement of 766 ms. This measurement was retained, and its exact cause remains unknown.

The overall median slightly favors Ancestors Array, while both methods showed similar performance during the second series.

### 11.6 Storage validation

| Collection | Documents | Total allocated storage |
|---|---:|---:|
| products | 5,000 | 9.813 MiB |
| categories | 1,470 | 0.875 MiB |
| products_backup_117000 | 117,000 | 180.504 MiB |

The additional allocated storage associated with the module integration was approximately 1.121 MiB.

The Atlas Logical Size metric was visually estimated at approximately 410 MB after integration, below the 512 MB quota.

This quota reading is approximate.

The overall Logical Size variation cannot be attributed exclusively to this module because the cluster is shared with other team members.

Allocated collection storage and Atlas Logical Size are different metrics.

The backup collection containing 117,000 products was preserved.

### 11.7 Final integration status

The Search & Categories module is technically complete.

All planned Atlas functional checks, performance benchmarks and final integrity checks were successfully performed.

Review compatibility and the remaining project modules are managed separately by the corresponding team members.

See [Atlas Validation Report](atlas_validation.md) for complete benchmark measurements, storage statistics, limitations and Atlas reproduction instructions.

## 12. Conclusion

The Search & Categories module has been implemented and validated locally using mongosh and the final shared dataset.

The module provides:

- Multi-criteria product search.
- Dynamic aggregation-based faceted search.
- Hierarchical category navigation.
- Parent References and Ancestors Array support.
- Idempotent category synchronization.
- Simple and compound index management.
- Numeric filter validation.
- Reproducible performance benchmarks.
- Storage overhead analysis.

Local validation resulted in 43 passed checks and zero failures.

The module was subsequently integrated and validated on MongoDB Atlas, with eight additional successful executions of the invalid-filter and nonexistent-category checks.

The final integration preserved all 5,000 products and the 117,000-product backup while generating 1,470 unique categories.

The Search & Categories module is ready for team-level integration.