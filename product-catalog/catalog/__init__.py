
from .product_model import create_product_document

from .product_crud import (
    create_product,
    get_product_by_id,
    update_product,
    delete_product,
    list_products
)

from .product_queries import (
    find_products_by_category,
    find_products_by_brand,
    find_products_by_attribute
)

from .product_indexes import create_product_indexes
