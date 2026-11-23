
# Product Catalogue Design

## Selected Design

Single Collection.

All products are stored in the MongoDB collection named products.

## Common Fields

- product_id
- title
- brand
- category
- price
- rating

## Category-Specific Fields

Category-specific characteristics are stored inside the attributes object.

## Justification

The single-collection approach simplifies product management, supports cross-category searches and allows new categories to be added without creating additional collections.

## Alternative Design

Separate collections were also considered. This approach offers specialized structures but makes cross-category searches and collection management more complex.
