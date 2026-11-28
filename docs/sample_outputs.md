# Sorties d'exemple - requetes du Membre 3

Generees le 2026-11-28 09:53 UTC sur la base `marketplace_db` (5000 produits, 44938 reviews). Lecture seule. Textes longs raccourcis. Temps = une seule execution, indicatif.

## 1. Produit par ID

`find_product_by_id('B00BOJO7ZU')`  
Statut : ok - temps indicatif : 87 ms

```json
{
  "product_id": "B00BOJO7ZU",
  "attributes": {
    "Brand": "Hermes",
    "Item Form": "Spray",
    "Item Volume": "1 Fluid Ounces",
    "Age Range (Description)": "Adult",
    "Style": "Modern",
    "Item Weight": "1 Ounces",
    "Manufacturer": "Hermes"
  },
  "brand": "Hermes",
  "category": {
    "main": "All Beauty",
    "path": [
      "Beauty & Personal Care",
      "Fragrance",
      "Women's",
      "Cologne"
    ]
  },
  "description": [
    "Product Description",
    "Elixir Des Merveilles Perfume Eau De Parfum Spray 1.0 Oz / 30 Ml for Women by Hermes."
  ],
  "features": [],
  "images": {
    "hi_res": [
      "https://m.media-amazon.com/images/I/51crbncYwJL._SL1000_.jpg"
    ],
    "large": [
      "https://m.media-amazon.com/images/I/416GqmfCu2L.jpg"
    ],
    "thumb": [
      "https://m.media-amazon.com/images/I/416GqmfCu2L._SS40_.jpg"
    ],
    "variant": [
      "MAIN"
    ]
  },
  "price": null,
  "rating": {
    "average": 3.9,
    "count": 13
  },
  "source": "Amazon Reviews 2023",
  "title": "Hermes Eau Des Merveilles Elixir Eau De Parfum Spray - 30ml/1oz"
}
```

## 2. Recherche par mots-cles

`search_by_keywords('hair chalk', page_size=3)`  
Statut : ok - temps indicatif : 175 ms

```json
{
  "total": 1086,
  "page": 1,
  "page_size": 3,
  "items": [
    {
      "product_id": "B074MBJ33D",
      "brand": "TOPNaturePlus",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Hair Coloring Products",
          "Hair Chalk"
        ]
      },
      "price": null,
      "rating": {
        "average": 4.4,
        "count": 2
      },
      "title": "Pretty See Colorful Hair Chalk Set Blendable Hair Color Pens Temporary Hair Chalks with 6 Different Colors, Suitable for Adolescent",
      "score": 18.541666666666668
    },
    {
      "product_id": "B0B8C7DYPJ",
      "brand": "Byhoo",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Hair Coloring Products",
          "Hair Chalk"
        ]
      },
      "price": "11.99",
      "rating": {
        "average": 3.4,
        "count": 12
      },
      "title": "Temporary Hair Dye, Hair Dye Glow in the Dark Paint Can Dye More 55% Hair Than Hair Chalk on Christmas, Birthday and Music Festival Party Supplies, Gifts for Gi...",
      "score": 16.222826086956523
    },
    {
      "product_id": "B084G8CWH8",
      "brand": "Hair",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Shave & Hair Removal",
          "Women's",
          "Bleaching"
        ]
      },
      "price": null,
      "rating": {
        "average": 4.4,
        "count": 83
      },
      "title": "Dust Free Bleach powder for hair, hair bleach, hair toner, hair bleach powder - 500g, 17.64 oz",
      "score": 15.01875
    }
  ]
}
```

## 3. Filtre categorie, prix et note

`filter_products({'main': 'All Beauty', 'path': ['Beauty & Personal Care', 'Hair Care'], 'min_price': 0, 'max_price': 100, 'min_rating': 4}, page_size=3)`  
Statut : ok - temps indicatif : 282 ms

```json
{
  "total": 428,
  "page": 1,
  "page_size": 3,
  "items": [
    {
      "product_id": "B000VHENGE",
      "brand": "ClassicCloseouts",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Hair Perms, Relaxers & Texturizers",
          "Home Perm Kits"
        ]
      },
      "price": "23.99",
      "rating": {
        "average": 5.0,
        "count": 5
      },
      "title": "Ogilvie Body & Volume Booster Hair Texturizing Treatment for All Hair Types One Application"
    },
    {
      "product_id": "B000W3UJEW",
      "brand": "Hunter Jack",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Hair Accessories",
          "Headbands"
        ]
      },
      "price": "24.99",
      "rating": {
        "average": 5.0,
        "count": 3
      },
      "title": "SMOOTH N SHINE Therapy Silk Fusion Silkener Leave-In Styling Lotion 6.7oz/200ml"
    },
    {
      "product_id": "B0016PZRAQ",
      "brand": "L'Oreal Paris",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Shampoo & Conditioner",
          "Shampoos"
        ]
      },
      "price": "29.99",
      "rating": {
        "average": 5.0,
        "count": 3
      },
      "title": "LOreal VIVE Shampoo, Fresh-Shine - 13 fl oz"
    }
  ]
}
```

## 5. Recherche a facettes (Hair Care)

`facets({'path': ['Beauty & Personal Care', 'Hair Care']})`  
Statut : ok - temps indicatif : 257 ms

```json
{
  "total": 1320,
  "brands": [
    {
      "_id": "Suave",
      "count": 12
    },
    {
      "_id": "L'Oreal Paris",
      "count": 9
    },
    {
      "_id": "Zotos",
      "count": 8
    },
    {
      "_id": "Paisle Botanics",
      "count": 6
    },
    {
      "_id": "S-noilite",
      "count": 6
    },
    {
      "_id": "Aveda",
      "count": 5
    },
    {
      "_id": "Conair",
      "count": 5
    },
    {
      "_id": "Garnier",
      "count": 5
    },
    "..."
  ],
  "price_ranges": [
    {
      "_id": "0",
      "count": 601
    },
    {
      "_id": "50",
      "count": 56
    },
    {
      "_id": "100",
      "count": 21
    },
    {
      "_id": "200",
      "count": 4
    },
    {
      "_id": "500+",
      "count": 2
    }
  ],
  "missing_prices": 636,
  "ratings": [
    {
      "_id": 0,
      "count": 22
    },
    {
      "_id": 2,
      "count": 63
    },
    {
      "_id": 3,
      "count": 354
    },
    {
      "_id": 4,
      "count": 881
    }
  ]
}
```

## 4. Filtre marque et note minimale

`filter_products({path, brand: <marque la plus frequente>, min_rating: 4})`  
Statut : ok - temps indicatif : 183 ms

```json
{
  "brand": "Suave",
  "total": 12,
  "page": 1,
  "page_size": 3,
  "items": [
    {
      "product_id": "B00HA7YE9O",
      "brand": "Suave",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Hair Loss Products"
        ]
      },
      "price": null,
      "rating": {
        "average": 5.0,
        "count": 1
      },
      "title": "Suave Kids 2 in 1 Shampoo Smoothers Orange Mango Outburst, Orange Mango Outburst 12 oz (Pack of 3)"
    },
    {
      "product_id": "B01MY7W3SI",
      "brand": "Suave",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Shampoo & Conditioner",
          "Shampoos"
        ]
      },
      "price": null,
      "rating": {
        "average": 4.8,
        "count": 64
      },
      "title": "Suave Professionals Strengthening Shampoo, Honey Infusion 12.6 oz (Pack of 2)"
    },
    {
      "product_id": "B01N6QHL1Z",
      "brand": "Suave",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Shampoo & Conditioner",
          "3-in-1 Shampoo, Conditioner & Body Wash"
        ]
      },
      "price": null,
      "rating": {
        "average": 4.7,
        "count": 641
      },
      "title": "Suave Kids 3 in 1 Shampoo Conditioner Body Wash For Tear-Free Bath Time, Fresh Spider-Sense, Dermatologist-Tested Kids Shampoo 3 in 1 Formula 28 oz"
    }
  ]
}
```

## 6a. Categorie et descendants

`category_with_descendants('All Beauty', ['Beauty & Personal Care', 'Hair Care'])`  
Statut : ok - temps indicatif : 172 ms

```json
[
  {
    "category_id": "[\"All Beauty\",\"Beauty & Personal Care\",\"Hair Care\"]",
    "depth": 1,
    "name": "Hair Care",
    "path": [
      "Beauty & Personal Care",
      "Hair Care"
    ]
  },
  {
    "category_id": "[\"All Beauty\",\"Beauty & Personal Care\",\"Hair Care\",\"Hair Accessories\"]",
    "depth": 2,
    "name": "Hair Accessories",
    "path": [
      "Beauty & Personal Care",
      "Hair Care",
      "Hair Accessories"
    ]
  },
  {
    "category_id": "[\"All Beauty\",\"Beauty & Personal Care\",\"Hair Care\",\"Hair Coloring Products\"]",
    "depth": 2,
    "name": "Hair Coloring Products",
    "path": [
      "Beauty & Personal Care",
      "Hair Care",
      "Hair Coloring Products"
    ]
  },
  {
    "category_id": "[\"All Beauty\",\"Beauty & Personal Care\",\"Hair Care\",\"Hair Cutting Tools\"]",
    "depth": 2,
    "name": "Hair Cutting Tools",
    "path": [
      "Beauty & Personal Care",
      "Hair Care",
      "Hair Cutting Tools"
    ]
  },
  {
    "category_id": "[\"All Beauty\",\"Beauty & Personal Care\",\"Hair Care\",\"Hair Extensions, Wigs & Accessories\"]",
    "depth": 2,
    "name": "Hair Extensions, Wigs & Accessories",
    "path": [
      "Beauty & Personal Care",
      "Hair Care",
      "Hair Extensions, Wigs & Accessories"
    ]
  },
  {
    "category_id": "[\"All Beauty\",\"Beauty & Personal Care\",\"Hair Care\",\"Hair Loss Products\"]",
    "depth": 2,
    "name": "Hair Loss Products",
    "path": [
      "Beauty & Personal Care",
      "Hair Care",
      "Hair Loss Products"
    ]
  },
  {
    "category_id": "[\"All Beauty\",\"Beauty & Personal Care\",\"Hair Care\",\"Hair Masks\"]",
    "depth": 2,
    "name": "Hair Masks",
    "path": [
      "Beauty & Personal Care",
      "Hair Care",
      "Hair Masks"
    ]
  },
  {
    "category_id": "[\"All Beauty\",\"Beauty & Personal Care\",\"Hair Care\",\"Hair Perms, Relaxers & Texturizers\"]",
    "depth": 2,
    "name": "Hair Perms, Relaxers & Texturizers",
    "path": [
      "Beauty & Personal Care",
      "Hair Care",
      "Hair Perms, Relaxers & Texturizers"
    ]
  },
  "..."
]
```

## 6b. Produits de la categorie et sous-categories

`products_in_category('All Beauty', ['Beauty & Personal Care', 'Hair Care'], page_size=3)`  
Statut : ok - temps indicatif : 220 ms

```json
{
  "total": 1158,
  "page": 1,
  "page_size": 3,
  "items": [
    {
      "product_id": "B00008KA7Q",
      "brand": "No-Rinse",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Shampoo & Conditioner",
          "Conditioners"
        ]
      },
      "price": null,
      "rating": {
        "average": 3.7,
        "count": 68
      },
      "title": "No-Rinse Hair Conditioner, 8 fl oz - Leaves Hair Fresh, Clean and Odor-Free, Rinse-Free Formula"
    },
    {
      "product_id": "B00008XP0B",
      "brand": "WAHL",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Hair Cutting Tools",
          "Hair Cutting Kits"
        ]
      },
      "price": null,
      "rating": {
        "average": 3.5,
        "count": 3
      },
      "title": "Wahl 79232-517 HomePro 12-Piece Haircut Kit"
    },
    {
      "product_id": "B0000SW90G",
      "brand": "Progaine",
      "category": {
        "main": "All Beauty",
        "path": [
          "Beauty & Personal Care",
          "Hair Care",
          "Shampoo & Conditioner",
          "Shampoos"
        ]
      },
      "price": "199.99",
      "rating": {
        "average": 3.7,
        "count": 39
      },
      "title": "Progaine Volumizing Shampoo 12 Ounce"
    }
  ]
}
```

## 7a. Reviews paginees, page 1 (les plus recentes)

`get_reviews_page('B00BOJO7ZU', page=1, page_size=3)`  
Statut : ok - temps indicatif : 162 ms

```json
{
  "total": 4,
  "page": 1,
  "page_size": 3,
  "items": [
    {
      "_id": "6b09fe781ee3e784611d5c93",
      "product_id": "B00BOJO7ZU",
      "user_id": "AFYJT7NGEHQ673JYCWAMEBWHFQBQ",
      "rating": 1.0,
      "title": "This is a fake",
      "text": "Fake perfume",
      "helpful_vote": 0,
      "verified_purchase": false,
      "created_at": "2021-12-14 01:10:03.121000"
    },
    {
      "_id": "6b09fe3f1ee3e784611d25cd",
      "product_id": "B00BOJO7ZU",
      "user_id": "AE4HBRSTUBN6XZCDMS6SESKHYCGQ",
      "rating": 1.0,
      "title": "This is fake perfume",
      "text": "This is worst fragrance  i use. I using elicrt perfume doesn’t It does smell like original like<br />this copy<br /><br />I want refund back<br /><br />Thanks",
      "helpful_vote": 0,
      "verified_purchase": false,
      "created_at": "2021-11-06 20:54:36.411000"
    },
    {
      "_id": "6b09fe7d1ee3e784611d61c0",
      "product_id": "B00BOJO7ZU",
      "user_id": "AE47H5KIKDEM65WNJSR5VJR7WBUA",
      "rating": 1.0,
      "title": "Beware",
      "text": "Please DO NOT BUY FROM THIS PARTICULAR COMPANY.  PARFUM HAS ABSOLUTELY NO SMELL.  ITS JUST COLORED WATER.  WHAT A RIP OFF.....PLEASE 🙏PLEASE DO NOT BUY",
      "helpful_vote": 1,
      "verified_purchase": true,
      "created_at": "2021-07-13 18:16:47.055000"
    }
  ]
}
```

## 7b. Reviews paginees, page 2 (les plus utiles)

`get_reviews_page('B00BOJO7ZU', page=2, page_size=3, sort='helpful')`  
Statut : ok - temps indicatif : 168 ms

```json
{
  "total": 4,
  "page": 2,
  "page_size": 3,
  "items": [
    {
      "_id": "6b09fe781ee3e784611d5c93",
      "product_id": "B00BOJO7ZU",
      "user_id": "AFYJT7NGEHQ673JYCWAMEBWHFQBQ",
      "rating": 1.0,
      "title": "This is a fake",
      "text": "Fake perfume",
      "helpful_vote": 0,
      "verified_purchase": false,
      "created_at": "2021-12-14 01:10:03.121000"
    }
  ]
}
```

## 8. Moyenne et nombre d'avis

`get_rating_stats('B00BOJO7ZU')`  
Statut : ok - temps indicatif : 81 ms

```json
{
  "product_id": "B00BOJO7ZU",
  "review_count": 4,
  "average_rating": 2.0,
  "distribution": {
    "5": 1,
    "4": 0,
    "3": 0,
    "2": 0,
    "1": 3
  }
}
```

## 9. Produit avec ses reviews ($lookup)

`get_product_with_reviews('B00BOJO7ZU', limit=2)`  
Statut : ok - temps indicatif : 84 ms

```json
{
  "_id": "6b0609dfd6bc0fb2039cdde9",
  "product_id": "B00BOJO7ZU",
  "attributes": {
    "Brand": "Hermes",
    "Item Form": "Spray",
    "Item Volume": "1 Fluid Ounces",
    "Age Range (Description)": "Adult",
    "Style": "Modern",
    "Item Weight": "1 Ounces",
    "Manufacturer": "Hermes"
  },
  "brand": "Hermes",
  "category": {
    "main": "All Beauty",
    "path": [
      "Beauty & Personal Care",
      "Fragrance",
      "Women's",
      "Cologne"
    ]
  },
  "description": [
    "Product Description",
    "Elixir Des Merveilles Perfume Eau De Parfum Spray 1.0 Oz / 30 Ml for Women by Hermes."
  ],
  "features": [],
  "images": {
    "hi_res": [
      "https://m.media-amazon.com/images/I/51crbncYwJL._SL1000_.jpg"
    ],
    "large": [
      "https://m.media-amazon.com/images/I/416GqmfCu2L.jpg"
    ],
    "thumb": [
      "https://m.media-amazon.com/images/I/416GqmfCu2L._SS40_.jpg"
    ],
    "variant": [
      "MAIN"
    ]
  },
  "price": null,
  "rating": {
    "average": 3.9,
    "count": 13
  },
  "source": "Amazon Reviews 2023",
  "title": "Hermes Eau Des Merveilles Elixir Eau De Parfum Spray - 30ml/1oz",
  "reviews": [
    {
      "_id": "6b09fe781ee3e784611d5c93",
      "product_id": "B00BOJO7ZU",
      "user_id": "AFYJT7NGEHQ673JYCWAMEBWHFQBQ",
      "rating": 1.0,
      "title": "This is a fake",
      "text": "Fake perfume",
      "helpful_vote": 0,
      "verified_purchase": false,
      "created_at": "2021-12-14 01:10:03.121000"
    },
    {
      "_id": "6b09fe3f1ee3e784611d25cd",
      "product_id": "B00BOJO7ZU",
      "user_id": "AE4HBRSTUBN6XZCDMS6SESKHYCGQ",
      "rating": 1.0,
      "title": "This is fake perfume",
      "text": "This is worst fragrance  i use. I using elicrt perfume doesn’t It does smell like original like<br />this copy<br /><br />I want refund back<br /><br />Thanks",
      "helpful_vote": 0,
      "verified_purchase": false,
      "created_at": "2021-11-06 20:54:36.411000"
    }
  ]
}
```

## 10. Stock disponible (lecture seule)

`get_available('B00BOJO7ZU')`  
Statut : ok - temps indicatif : 75 ms

```json
{
  "product_id": "B00BOJO7ZU",
  "available": null
}
```
