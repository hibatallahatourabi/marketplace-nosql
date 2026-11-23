
# Multi-Category Product Catalogue

## Project Description

This project implements a multi-category product catalogue for an online marketplace using MongoDB.

The catalogue stores products from different categories in a single collection and supports CRUD operations, advanced product searches, indexing and performance benchmarking.

## Technologies

- Python
- MongoDB Atlas
- PyMongo
- Google Colab
- Amazon Reviews 2023 Dataset

## Project Structure

product-catalog/
│
├── catalog/
│   ├── __init__.py
│   ├── product_model.py
│   ├── product_crud.py
│   ├── product_queries.py
│   └── product_indexes.py
│
├── tests/
│   └── test_catalog.py
│
├── benchmarks/
│   └── catalog_benchmark.py
│
├── docs/
│   └── catalog_design.md
│
├── requirements.txt
└── README.md

## Features

### Product Management

- Create products
- Retrieve products by ID
- Update product information
- Delete products
- List products with pagination

### Product Search

- Search by category
- Search by brand
- Search by product characteristics

### Indexing

The catalogue uses indexes on:

- product_id (unique)
- brand
- category.path

### Performance Benchmarking

MongoDB execution statistics are used to analyze query execution plans and the number of documents examined.

## Testing

Run the automated tests using:

python -m unittest discover -s tests -v

## Database

Database name: marketplace_db

Collection name: products

## Dataset Source

Amazon Reviews 2023:
https://amazon-reviews-2023.github.io/

## Design Decision

The project uses a single-collection approach to simplify product management and support searches across different categories.
