// Recherche a facettes avec filtres selectionnes

print("=== Recherche a facettes ===");

const criteria = {
    main: "All Beauty",
    path: ["Beauty & Personal Care", "Hair Care"],
    brand: null,
    minPrice: 0,
    maxPrice: 100,
    minRating: 4
};

// Validation des filtres
for (const key of ["minPrice", "maxPrice"]) {
    if (criteria[key] != null &&
        (!Number.isFinite(criteria[key]) || criteria[key] < 0)) {
        throw new Error("Prix invalide : " + key);
    }
}

if (
    criteria.minPrice != null &&
    criteria.maxPrice != null &&
    criteria.minPrice > criteria.maxPrice
) {
    throw new Error("Le prix minimum depasse le prix maximum.");
}

if (
    criteria.minRating != null &&
    (!Number.isFinite(criteria.minRating) ||
    criteria.minRating < 0 ||
    criteria.minRating > 5)
) {
    throw new Error("La note doit etre comprise entre 0 et 5.");
}

// Construction des filtres
const filter = {};

if (criteria.main) {
    filter.$or = [
        { "category.main": criteria.main },
        {
            "category.main": null,
            "category.path.0": criteria.main
        },
        {
            "category.main": /^\s*$/,
            "category.path.0": criteria.main
        }
    ];
}

if (criteria.path && criteria.path.length > 0) {
    criteria.path.forEach((name, index) => {
        filter["category.path." + index] = name;
    });
}

if (criteria.brand) {
    filter.brand = criteria.brand;
}

if (criteria.minPrice != null || criteria.maxPrice != null) {
    filter.price = {
        $type: "number",
        $gte: NumberDecimal(String(criteria.minPrice ?? 0))
    };

    if (criteria.maxPrice != null) {
        filter.price.$lte =
            NumberDecimal(String(criteria.maxPrice));
    }
}

if (criteria.minRating != null) {
    filter["rating.average"] = {
        $gte: criteria.minRating
    };
}

print("=== Filtres appliques ===");
printjson(filter);

// Pipeline d'agregation
const result = db.products.aggregate([
    {
        $match: filter
    },
    {
        $facet: {
            total: [
                { $count: "count" }
            ],

            brands: [
                {
                    $match: {
                        brand: { $exists: true, $ne: null }
                    }
                },
                {
                    $group: {
                        _id: "$brand",
                        count: { $sum: 1 }
                    }
                },
                {
                    $sort: { count: -1, _id: 1 }
                }
            ],

            price_ranges: [
                {
                    $match: {
                        price: {
                            $type: "number",
                            $gte: NumberDecimal("0")
                        }
                    }
                },
                {
                    $bucket: {
                        groupBy: "$price",
                        boundaries: [
                            NumberDecimal("0"),
                            NumberDecimal("50"),
                            NumberDecimal("100"),
                            NumberDecimal("200"),
                            NumberDecimal("500")
                        ],
                        default: "500+",
                        output: {
                            count: { $sum: 1 }
                        }
                    }
                }
            ],

            missing_prices: [
                { $match: { price: null } },
                { $count: "count" }
            ],

            ratings: [
                {
                    $match: {
                        "rating.average": { $type: "number" }
                    }
                },
                {
                    $bucket: {
                        groupBy: "$rating.average",
                        boundaries: [0, 2, 3, 4, 5.01],
                        default: "Other",
                        output: {
                            count: { $sum: 1 }
                        }
                    }
                }
            ]
        }
    },
    {
        $set: {
            total: {
                $ifNull: [
                    { $arrayElemAt: ["$total.count", 0] },
                    0
                ]
            },
            missing_prices: {
                $ifNull: [
                    { $arrayElemAt: ["$missing_prices.count", 0] },
                    0
                ]
            }
        }
    }
]).toArray();

print("=== RESULTATS DES FACETTES ===");
printjson(result);