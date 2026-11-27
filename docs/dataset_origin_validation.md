# Dataset Origin Validation

## 1. Objective

Identify the official source category of the final 5,000 products and investigate the absence of matching reviews in the All_Beauty review dataset.

## 2. Data Sources

- Product dataset: `data/beauty_products_final_5000.json`
- Official mapping: `data/asin2category.json`
- Source: Amazon Reviews 2023 — McAuley Lab
- Mapping file size: 1,246,846,569 bytes
- Official dataset: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023

Both local JSON files were verified using SHA256.

## 3. Tools and Methodology

- Python 3.12.10
- ijson 3.6.0
- Python collections.Counter
- PowerShell
- Visual Studio Code

The analysis extracts the 5,000 unique product IDs and compares them against the official ASIN-to-category mapping.

The ijson library enables streaming JSON parsing without loading the entire mapping file into memory.

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

## 5. Conclusion

All 5,000 products are associated with the official Beauty and Personal Care source category.

This finding explains the likely cause of the absence of matching reviews in the All_Beauty review dataset.

The recommended review dataset is `Beauty_and_Personal_Care.jsonl.gz`.

The actual correspondence between product IDs and review parent_asin values must still be validated before importing reviews.

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

## 7. Integration Status

- Product source category: Confirmed.
- Product dataset integrity: Confirmed.
- Review compatibility: Pending validation.
- MongoDB Atlas integration: Pending team approval.

No MongoDB collections or product identifiers were modified during this analysis.

This standalone Python utility is independent of the Search & Categories module, which remains implemented using mongosh.