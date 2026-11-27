# MongoDB Atlas — Search & Categories Validation

## 1. Environment

- Project: Multi-Category Product Catalog for an Online Marketplace
- Module: Search & Categories — Member 2
- Validation date: November 27, 2026
- Database: marketplace_db
- Platform: MongoDB Atlas Free Tier (M0)
- MongoDB version: 8.0.39
- Mongosh version: 2.14.0
- Cloud provider: AWS
- Region: Paris (eu-west-3)
- Git branch: feature/search-categories

All database operations for this module were performed using mongosh.

## 2. Dataset Integrity

Before integration, the final dataset was verified against the local dataset.

| Indicator | Result |
|---|---:|
| Total products | 5,000 |
| Unique product IDs | 5,000 |
| Duplicate product IDs | 0 |
| Local IDs missing on Atlas | 0 |
| Additional IDs on Atlas | 0 |
| Products with missing main category | 39 |
| Products with null prices | 2,545 |
| Products with Decimal128 prices | 2,455 |
| Backup products | 117,000 |

The comparison confirmed that the local and Atlas datasets contain the same product identifiers. It did not compare every individual product field.

The official Amazon ASIN mapping also confirmed that all 5,000 products belong to the Beauty and Personal Care source category.

See [dataset_origin_validation.md](dataset_origin_validation.md) for details.

## 3. Index Integration

The search_indexes.js script was executed successfully on Atlas.

Existing compatible indexes were reused without duplication.

### Products collection

| Index | Fields | Purpose |
|---|---|---|
| _id_ | _id | MongoDB identifier |
| product_id_1 | product_id | Unique product identifier |
| brand_1 | brand | Brand filtering |
| category.path_1 | category.path | Category path filtering |
| idx_price | price | Price filtering |
| idx_rating | rating.average | Rating filtering |
| idx_category_main | category.main | Main category filtering |
| idx_category_price_rating | category.main, price, rating.average | Compound search index |

Total: 8 indexes.

### Categories collection

| Index | Fields | Purpose |
|---|---|---|
| _id_ | _id | MongoDB identifier |
| category_id_1 | category_id | Unique category identifier |
| idx_parent_id | parent_id | Parent References traversal |
| idx_ancestors | ancestors | Array of Ancestors queries |

Total: 4 indexes.

## 4. Category Synchronization

The sync_categories.js script generated the category hierarchy from the existing product documents.

| Indicator | First execution | Second execution |
|---|---:|---:|
| Categories detected | 1,470 | 1,470 |
| Inserted | 1,470 | 0 |
| Updated | 0 | 0 |
| Unchanged | 0 | 1,470 |
| Skipped products | 0 | 0 |
| Derived main categories | 39 | 39 |

The second execution confirmed sequential idempotence.

The missing main categories were derived from the first element of the category path without modifying the original product documents.

Category synchronization uses bulkWrite operations with upsert enabled.

## 5. Functional Validation

### 5.1 Multi-Criteria Search

The search_products.js script was executed successfully.

Selected category:

- Main: Beauty & Personal Care
- Path: Beauty & Personal Care / Hair Care

Four products were returned:

| Product ID | Rating |
|---|---:|
| B01BO4M88C | 5.0 |
| B073CBMGRP | 4.6 |
| B099255BXG | 4.1 |
| B08PC95NJ7 | 4.0 |

The results confirmed that products with missing main categories remain accessible through the category path fallback.

### 5.2 Faceted Search

The facet_search.js script was executed with the following criteria:

- Main category: All Beauty
- Category path: Beauty & Personal Care / Hair Care
- Minimum price: 0
- Maximum price: 100
- Minimum rating: 4

Results:

| Indicator | Count |
|---|---:|
| Matching products | 428 |
| Price range [0, 50) | 401 |
| Price range [50, 100) | 27 |
| Missing prices | 0 |
| Rating range [4, 5.01) | 428 |

Brand aggregation was also returned successfully.

The facet results are consistent with the search benchmark.

### 5.3 Category Hierarchy

The category_hierarchy.js script returned:

- Selected category: Hair Care
- Categories including the selected category: 8
- Descendant categories: 7
- Associated products: 4

The hierarchy and product identifiers matched the local validation results.

Both Parent References and Array of Ancestors are supported by the category model.

## 6. Search Performance Benchmark

The search_benchmark.js script compared three execution strategies using the same query and sorting criteria.

### 6.1 Atlas Results

| Metric | Automatic plan | Compound index | Collection scan |
|---|---:|---:|---:|
| Execution time (ms) | 80 | 13 | 12 |
| Documents examined | 2,368 | 1,472 | 5,000 |
| Index keys examined | 2,368 | 3,885 | 0 |
| Products returned | 428 | 428 | 428 |

The automatic plan selected idx_price.

The forced compound index was idx_category_price_rating.

The collection scan used COLLSCAN.

### 6.2 Performance Analysis

The compound index reduced the number of examined documents from 5,000 to 1,472.

- Documents saved: 3,528
- Document examination reduction: 70.56%
- Execution time reduction compared with the automatic plan: 83.75%

All three strategies returned the same number of matching products.

The collection scan was slightly faster than the compound index in this particular execution. Therefore, the results demonstrate reduced document examination, but do not establish that the compound index is always faster.

### 6.3 Local and Atlas Comparison

| Strategy | Local mean — 5 runs | Atlas — 1 run |
|---|---:|---:|
| Automatic plan | 59 ms | 80 ms |
| Compound index | 10.6 ms | 13 ms |
| Collection scan | 9.4 ms | 12 ms |

Atlas search measurements represent one execution per strategy.

Execution statistics from explain() do not represent complete application response times.

## 7. Category Hierarchy Benchmark

The hierarchy_benchmark.js script compared two approaches on the same category collection:

- Parent References using $graphLookup.
- Array of Ancestors using an indexed ancestors field.

### 7.1 First Benchmark

| Execution | Parent References (ms) | Array of Ancestors (ms) |
|---|---:|---:|
| 1 | 129 | 766 |
| 2 | 110 | 99 |
| 3 | 103 | 96 |
| 4 | 104 | 95 |
| 5 | 106 | 101 |
| Mean | 110.4 | 231.4 |
| Median | 106 | 99 |

The first Array of Ancestors measurement showed an unusually high execution time of 766 ms.

Its exact cause could not be determined. Network latency, server load and caching are possible explanations.

The original measurement was retained.

### 7.2 Second Benchmark

| Execution | Parent References (ms) | Array of Ancestors (ms) |
|---|---:|---:|
| 1 | 102 | 102 |
| 2 | 103 | 107 |
| 3 | 105 | 100 |
| 4 | 104 | 99 |
| 5 | 109 | 99 |
| Mean | 104.6 | 101.4 |
| Median | 104 | 100 |

The second benchmark showed similar execution times for both approaches.

Array of Ancestors was approximately 3.06% faster on average during this second series.

### 7.3 Combined Results

| Indicator | Parent References | Array of Ancestors |
|---|---:|---:|
| Total executions | 10 | 10 |
| Overall mean | 107.5 ms | 166.4 ms |
| Overall median | 104.5 ms | 99.5 ms |
| Descendants returned | 564 | 564 |
| Identical result sets | 10/10 | 10/10 |

All ten comparisons returned identical descendant identifiers.

The median slightly favors Array of Ancestors, while the overall mean is affected by the unusually high first measurement.

### 7.4 Local and Atlas Comparison

| Indicator | Local | Atlas — 10 runs |
|---|---:|---:|
| Total categories | 1,470 | 1,470 |
| Descendants | 564 | 564 |
| Parent References mean | 8.4 ms | 107.5 ms |
| Array of Ancestors mean | 4.4 ms | 166.4 ms |
| Parent References median | 8 ms | 104.5 ms |
| Array of Ancestors median | 4 ms | 99.5 ms |

Unlike the search benchmark based on explain(), hierarchy measurements include client-side retrieval and communication with the remote database.

The comparison evaluates two query strategies on the same hybrid category model rather than two independently stored collections.

## 8. Invalid Filter Tests

The test_invalid_filters.js script was executed successfully on Atlas.

| Test | Result |
|---|---|
| Negative minimum price | PASS |
| Negative maximum price | PASS |
| Minimum price greater than maximum | PASS |
| Non-numeric price | PASS |
| Negative rating | PASS |
| Rating greater than 5 | PASS |
| Non-numeric rating | PASS |
| Nonexistent category | PASS |

Summary:

- Passed: 8
- Failed: 0
- Success rate: 100%

The nonexistent category test confirms the absence of the specified category identifier. It does not directly test the exception handling of category_hierarchy.js.

The local fixture-based test suite was not executed on the shared Atlas database because it performs database writes.

## 9. Final Data Integrity

After integration and testing:

| Indicator | Result |
|---|---:|
| Total products | 5,000 |
| Unique product IDs | 5,000 |
| Total categories | 1,470 |
| Unique category IDs | 1,470 |
| Products indexes | 8 |
| Categories indexes | 4 |
| Backup products | 117,000 |

Product and backup document counts were preserved.

No duplicate product or category identifiers were detected.

## 10. Storage Analysis

### 10.1 Final Collection Statistics

All values are expressed in MiB.

| Collection | Logical data size | Allocated data storage | Index size | Total allocated storage |
|---|---:|---:|---:|---:|
| products | 12.490 | 8.980 | 0.832 | 9.813 |
| categories | 0.852 | 0.344 | 0.531 | 0.875 |
| products_backup_117000 | 296.865 | 154.422 | 26.082 | 180.504 |

Total allocated storage for these three collections: approximately 191.191 MiB.

### 10.2 Module Storage Overhead

| Indicator | Before integration | After integration |
|---|---:|---:|
| Products indexes | 4 | 8 |
| Products index size | 0.586 MiB | 0.832 MiB |
| Products total storage | 9.566 MiB | 9.813 MiB |
| Categories total storage | 0 MiB | 0.875 MiB |

Additional allocated storage:

- Product indexes: approximately 0.246 MiB.
- Categories collection and indexes: 0.875 MiB.
- Total module overhead: approximately 1.121 MiB.

The categories collection's allocated storage increased after synchronization without an increase in its document count.

### 10.3 Atlas Quota

The Atlas Free Tier provides a storage limit of 512 MB.

Visual estimates from the Logical Size metric:

| Indicator | Before integration | After integration |
|---|---:|---:|
| Logical Size | Approximately 381 MB | Approximately 410 MB |
| Quota utilization | Approximately 74.4% | Approximately 80.1% |
| Remaining capacity | Approximately 131 MB | Approximately 102 MB |

These values are approximate graphical readings, not exact metric values.

The cluster remained below its storage limit at the time of verification.

The overall Logical Size variation cannot be attributed exclusively to this module because the Atlas cluster is shared with other team members.

Allocated collection storage and Atlas Logical Size are different metrics and must not be directly equated.

The backup collection was preserved.

## 11. Reproduction Instructions

Connect to the authorized Atlas database using mongosh and the credentials provided through the team's secure configuration.

From the repository root, execute the following scripts in order:

1. load("mongosh/search_indexes.js")
2. load("mongosh/sync_categories.js")
3. load("mongosh/search_products.js")
4. load("mongosh/facet_search.js")
5. load("mongosh/category_hierarchy.js")
6. load("mongosh/search_benchmark.js")
7. load("mongosh/hierarchy_benchmark.js")
8. load("mongosh/test_invalid_filters.js")

The first two scripts perform database writes and must only be executed with team authorization.

The remaining scripts are read-only in the validated implementation.

Do not execute dataset import or fixture seeding scripts on the shared Atlas database.

## 12. Limitations

- The Atlas search benchmark contains one execution per strategy.
- Remote hierarchy timings include network communication.
- The cause of the unusually high hierarchy measurement remains unknown.
- The search benchmark compares result counts rather than complete product identifier sets.
- The hierarchy benchmark compares query strategies within one hybrid category model.
- The Atlas quota readings are approximate.
- Category synchronization does not automatically remove obsolete categories.
- Results obtained with 5,000 products cannot be generalized to substantially larger datasets without additional testing.

## 13. Conclusion

The Search & Categories module was successfully integrated and validated on MongoDB Atlas.

The implementation provides:

- Multi-criteria product search.
- Aggregation-based faceted search.
- Hierarchical category navigation.
- Parent References and Array of Ancestors support.
- Single-field and compound indexing.
- Idempotent category synchronization.
- Invalid filter validation.
- Measured search and hierarchy performance.
- Storage overhead analysis.

The final validation confirmed the preservation of 5,000 products, the synchronization of 1,470 unique categories, the successful execution of all eight invalid-filter tests and the preservation of the 117,000-product backup.

The module is technically complete and ready for team-level integration.