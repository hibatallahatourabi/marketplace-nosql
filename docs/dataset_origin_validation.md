# Dataset Origin Validation

## 1. Objective

Identify the official source category of the final 5,000 products, investigate the absence of matching reviews in the All_Beauty review dataset and document the subsequent reviews integration.

## 2. Data Sources

- Product dataset: `data/beauty_products_final_5000.json`
- Official mapping: `data/asin2category.json`
- Source: Amazon Reviews 2023 — McAuley Lab
- Mapping file size: 1,246,846,569 bytes
- Official dataset: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- Matching review dataset: `Beauty_and_Personal_Care.jsonl.gz`

Both local JSON files were verified using SHA256.

## 3. Tools and Methodology

- Python 3.12.10
- ijson 3.6.0
- Python collections.Counter
- PowerShell
- Visual Studio Code

The analysis extracts the 5,000 unique product IDs and compares them against the official ASIN-to-category mapping.

The ijson library enables streaming JSON parsing without loading the entire mapping file into memory.

This analysis was performed independently of MongoDB and did not require a database connection.

## 4. Results

| Metric | Result |
|---|---:|
| Products analyzed | 5,000 |
| Unique product IDs | 5,000 |
| Mapping entries scanned | 35,393,189 |
| Matched IDs | 5,000 |
| Unmatched IDs | 0 |
| Match rate | 100% |
| Beauty and Personal Care | 5,000 |
| All Beauty | 0 |
| Initial execution time | 13.54 seconds |

All 5,000 product identifiers were found in the official mapping and assigned to Beauty and Personal Care.

The official source category must not be confused with the internal classification stored in `category.main`.

## 5. Dataset Origin Conclusion

All 5,000 products are associated with the official Beauty and Personal Care source category.

This finding explains the likely cause of the absence of matching reviews in the All_Beauty review dataset.

Based on this analysis, the recommended review dataset was `Beauty_and_Personal_Care.jsonl.gz`.

The mapping analysis establishes the official category assignment of the product identifiers. Actual compatibility with review records requires a separate validation.

This subsequent validation was performed by the team member responsible for reviews integration.

## 6. Reproduction

Place both JSON input files in the data directory.

Install the required dependency:

```bash
python -m pip install ijson==3.6.0
```

Run the analysis:

```bash
python tools/analyze_dataset_origin.py
```

The detailed results are generated in:

`data/dataset_origin_results.json`

## 7. Reviews Compatibility and Integration

### 7.1 Review Dataset Confirmation

On November 27, 2026, the team member responsible for reviews confirmed that the Beauty and Personal Care review dataset was successfully used to import reviews associated with the final 5,000 products.

The All_Beauty review dataset did not contain matching product identifiers according to the team's earlier investigation.

The successful import is consistent with the conclusions of the ASIN-to-category mapping analysis.

### 7.2 Reported Reviews Import Results

| Metric | Result |
|---|---:|
| Review source | Beauty and Personal Care |
| Imported reviews | 44,938 |
| Total products | 5,000 |
| Products with at least one review | 5,000 |
| Product coverage | 100% |
| Maximum imported reviews per product | 20 |
| Average imported reviews per product | 8.99 |
| Target collection | reviews |
| Target database | marketplace_db |

These results were communicated by the team member responsible for reviews integration.

They were not independently reproduced by the Search & Categories module.

### 7.3 Review Query Validation

The reviews team member reported successful validation of:

- Paginated review retrieval.
- Rating statistics computed from imported reviews.
- Product and reviews lookup.

The implementation is available in the `feature/queries` branch.

Pull Request:

https://github.com/hibatallahatourabi/marketplace-nosql/pull/2

The Pull Request is under team review and should not be considered merged until the review process is completed.

### 7.4 Original Amazon Ratings and Imported Review Sample

The product documents contain original Amazon rating information.

The field `products.rating.count` represents the original Amazon rating count, not the number of review documents imported into MongoDB.

The imported reviews collection contains a limited sample of up to 20 reviews per product.

Consequently:

- Product rating information represents the original Amazon metadata.
- Review statistics calculated from the reviews collection describe the imported sample.
- The number of imported reviews should not be expected to equal `products.rating.count`.
- Rating averages calculated from the imported sample may differ from `products.rating.average`.

The Search & Categories module continues to use the original product rating fields for rating filters and rating facets.

This distinction must be documented in the final project report.

## 8. MongoDB Atlas Integration

Following the final product import, the Search & Categories module was successfully integrated into the shared MongoDB Atlas database on November 27, 2026.

The local and Atlas product identifier sets were compared.

| Metric | Result |
|---|---:|
| Local product IDs | 5,000 |
| Atlas product IDs | 5,000 |
| Missing IDs on Atlas | 0 |
| Additional IDs on Atlas | 0 |
| Synchronized categories | 1,470 |
| Unique category IDs | 1,470 |
| Product indexes | 8 |
| Category indexes | 4 |
| Invalid-filter and nonexistent-category checks passed | 8/8 |

The identifier comparison confirms that the same product IDs are present in both environments.

It does not constitute an exhaustive comparison of all product fields.

The Search & Categories integration preserved the original product documents and the existing backup collection containing 117,000 products.

See [Atlas Validation Report](atlas_validation.md) for detailed integration results.

## 9. Final Integration Status

| Component | Status |
|---|---|
| Official product source category | Confirmed |
| Local product identifier integrity | Confirmed |
| Local and Atlas product ID correspondence | Confirmed |
| Compatible review dataset | Confirmed by reviews team member |
| Reviews import | Completed according to team update |
| Product coverage by imported reviews | 100% according to team update |
| Search & Categories Atlas integration | Completed and validated |
| Category synchronization | Completed |
| Synchronization idempotence | Verified |
| Search indexes | Created or reused |
| Reviews Pull Request | Under team review |

No MongoDB collections or product identifiers were modified during the standalone dataset origin analysis.

The subsequent Atlas integration was performed separately using the mongosh scripts of the Search & Categories module.

This standalone Python utility remains independent of the Search & Categories implementation, which uses mongosh and JavaScript.

## 10. Limitations

- The ASIN mapping confirms official category assignments but does not establish the complete extraction history of the product dataset.
- The reviews import results were reported by the responsible team member and were not independently reproduced by this module.
- Imported reviews represent a limited sample rather than the complete Amazon review history.
- The comparison between local and Atlas products verifies identifier equality rather than complete document equality.
- Atlas storage measurements documented during the Search & Categories integration are historical measurements and may differ from the current cluster usage following the reviews import and other team operations.

## 11. Final Conclusion

The streaming analysis of 35,393,189 mapping entries successfully identified the official source category of all 5,000 products.

The analysis established a 100% correspondence with Beauty and Personal Care and no correspondence with All Beauty in the official category mapping.

The subsequent reviews import reported by the team confirmed the practical compatibility of the recommended review dataset, with 44,938 imported reviews covering all 5,000 products.

The Search & Categories module has been successfully integrated and validated on MongoDB Atlas.

The dataset origin investigation is complete.

Related documentation:

- [Search Design](search_design.md)
- [Category Design](category_design.md)
- [Final Local Validation Report](final_validation.md)
- [Atlas Validation Report](atlas_validation.md)