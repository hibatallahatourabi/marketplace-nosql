// Comparaison Parent References vs Ancestors Array

print("=== BENCHMARK DE LA HIERARCHIE ===");

const categoryId = JSON.stringify([
    "All Beauty",
    "Beauty & Personal Care"
]);

const category = db.categories.findOne({
    category_id: categoryId
});

if (!category) {
    throw new Error("Categorie introuvable.");
}

const REPEATS = 5;

function parentReferences() {
    return db.categories.aggregate([
        {
            $match: {
                category_id: categoryId
            }
        },
        {
            $graphLookup: {
                from: "categories",
                startWith: "$category_id",
                connectFromField: "category_id",
                connectToField: "parent_id",
                as: "descendants"
            }
        },
        {
            $unwind: "$descendants"
        },
        {
            $project: {
                _id: 0,
                category_id: "$descendants.category_id"
            }
        }
    ]).toArray();
}

function ancestorsArray() {
    return db.categories.find(
        { ancestors: categoryId },
        { _id: 0, category_id: 1 }
    ).toArray();
}

function measure(fn) {
    const start = Date.now();
    const results = fn();

    return {
        time: Date.now() - start,
        results: results
    };
}

function average(values) {
    return values.reduce((a, b) => a + b, 0)
        / values.length;
}

// Echauffement
parentReferences();
ancestorsArray();

const parentTimes = [];
const ancestorsTimes = [];

for (let i = 0; i < REPEATS; i++) {

    // Alterner l'ordre des mesures
    let parent;
    let ancestors;

    if (i % 2 === 0) {
        parent = measure(parentReferences);
        ancestors = measure(ancestorsArray);
    } else {
        ancestors = measure(ancestorsArray);
        parent = measure(parentReferences);
    }

    parentTimes.push(parent.time);
    ancestorsTimes.push(ancestors.time);

    const parentIds = parent.results
        .map(c => c.category_id).sort();

    const ancestorIds = ancestors.results
        .map(c => c.category_id).sort();

    const sameResults =
        JSON.stringify(parentIds) ===
        JSON.stringify(ancestorIds);

    print("\n=== EXECUTION " + (i + 1) + " ===");

    printjson({
        parent_references_ms: parent.time,
        ancestors_array_ms: ancestors.time,
        descendants_parent: parentIds.length,
        descendants_ancestors: ancestorIds.length,
        resultats_identiques: sameResults
    });

    if (!sameResults) {
        throw new Error("Resultats incoherents.");
    }
}

print("\n=== RESULTATS FINAUX ===");

printjson({
    total_categories: db.categories.countDocuments({}),
    executions: REPEATS,
    parent_times_ms: parentTimes,
    ancestors_times_ms: ancestorsTimes,
    parent_average_ms: average(parentTimes),
    ancestors_average_ms: average(ancestorsTimes)
});