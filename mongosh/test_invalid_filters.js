// Tests des filtres invalides de facet_search.js

const fs = require("fs");

const source = fs.readFileSync(
    "mongosh/facet_search.js",
    "utf8"
);

let passed = 0;
let failed = 0;

function testInvalid(name, criteria, expectedError) {

    const modified = source.replace(
        /const criteria = \{[\s\S]*?\};/,
        "const criteria = " +
        JSON.stringify(criteria) + ";"
    );

    if (modified === source) {
        throw new Error("Impossible de remplacer les criteres.");
    }

    try {
        new Function(modified)();

        print("FAIL : " + name);
        failed++;

    } catch (error) {

        if (error.message.includes(expectedError)) {
            print("PASS : " + name);
            passed++;
        } else {
            print("FAIL : " + name + " - " + error.message);
            failed++;
        }
    }
}

const base = {
    main: null,
    path: null,
    brand: null,
    minPrice: null,
    maxPrice: null,
    minRating: null
};

testInvalid(
    "Prix minimum negatif",
    { ...base, minPrice: -10 },
    "Prix invalide"
);

testInvalid(
    "Prix maximum negatif",
    { ...base, maxPrice: -20 },
    "Prix invalide"
);

testInvalid(
    "Prix minimum superieur au maximum",
    { ...base, minPrice: 100, maxPrice: 50 },
    "Le prix minimum depasse"
);

testInvalid(
    "Prix non numerique",
    { ...base, minPrice: "abc" },
    "Prix invalide"
);

testInvalid(
    "Note negative",
    { ...base, minRating: -1 },
    "La note doit etre comprise"
);

testInvalid(
    "Note superieure a 5",
    { ...base, minRating: 6 },
    "La note doit etre comprise"
);

testInvalid(
    "Note non numerique",
    { ...base, minRating: "abc" },
    "La note doit etre comprise"
);

// Verification d'une categorie inexistante

const count = db.categories.countDocuments({
    category_id: JSON.stringify([
        "CategorieInexistante",
        "CategorieInexistante"
    ])
});

if (count === 0) {
    print("PASS : Categorie inexistante");
    passed++;
} else {
    print("FAIL : Categorie inexistante");
    failed++;
}

print("\n=== RESULTATS ===");
print("Tests reussis : " + passed);
print("Tests echoues : " + failed);

if (failed > 0) {
    throw new Error("Certains tests ont echoue.");
}