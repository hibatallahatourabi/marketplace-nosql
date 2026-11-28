# Member 3 demo plan (about 6 minutes) and likely questions

Goal: show how the marketplace finds information, then explain the design choices.
Run `python scripts/demo_queries.py` before the demo and keep `docs/sample_outputs.md` open as a fallback.

## Sequence
| # | Show | Say |
| --- | --- | --- |
| 1 | Product by ID (`B00BOJO7ZU`) | One unique `product_id` index; the same key links products, reviews, inventory and price history. |
| 2 | Keyword search "hair chalk" | With the text index: any word, ranked by relevance (1,086 results). Without it: title fallback, all words (3 results). The index costs 1.16 MB. |
| 3 | Filter: category, price 0-100, rating 4+ (428 products) | One filter built from optional criteria; prices are `Decimal128`; products without a price are excluded. |
| 4 | Facets on Hair Care (1,320 products) | One `$facet` aggregation returns brands, price ranges, missing prices and rating buckets in a single pass. |
| 5 | Category and subcategories (104 categories, 1,158 products) | The category path is matched as a prefix, so descendants come with the parent; the tree uses `ancestors` and `depth`. |
| 6 | Reviews, page 1 then page 2, and rating stats | Reviews are a separate collection; every sort option has its own index and `explain()` shows no in-memory sort. |
| 7 | Product with reviews (`$lookup`) and available stock | Reviews are joined only when needed; stock is `quantity - reserved`. |

## Likely questions
- **Why a separate `reviews` collection?** A product can have thousands of reviews; embedding them would make product documents grow without bound and rewrite them on every review.
- **Why is the average different from Amazon's?** Amazon's `rating.count` is the full total; we loaded at most 20 reviews per product to fit the 512 MB free tier. Our statistics describe that sample.
- **Why did the first review file not work?** `All_Beauty` reviews matched none of our products, because they come from `Beauty_and_Personal_Care` metadata. We switched to the matching review file.
- **Why only one text index?** MongoDB allows one per collection. We agreed on it with Search & Categories, who confirmed none of her 8 indexes was a text index.
- **What did the text index cost?** +1.16 MB (index total 0.832 MB to 1.992 MB); the 8 existing indexes are unchanged.
- **Is the text search faster?** Not measured yet; we only claim ranking and index support. Benchmark it with Member 4.
- **How do you avoid overselling?** The availability check is part of the update filter, so one atomic write either reserves the stock or does nothing.
- **Why does pagination use `_id` as a second sort key?** It makes the order stable when two reviews share the same value, and it is part of each index.
- **What is the main limitation?** The review sample (20 per product, in file order) and the free-tier size.
- **What would you improve?** An "all words" mode on top of the text index, a benchmark of keyword search, and reviews chosen by recency or helpfulness.
