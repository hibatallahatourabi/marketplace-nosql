"""Tests hors ligne des requetes produits (pytest tests/).
Limite : mongomock ne compare pas les Decimal128 -> le filtre de prix et les facettes de prix
sont testes seulement par la forme du filtre ; a verifier sur Atlas (voir README)."""
import sys
from pathlib import Path
from unittest import mock

import mongomock
import pytest
from bson.decimal128 import Decimal128
from pymongo.errors import OperationFailure

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.queries import products as P


def make_products():
    def prod(pid, title, brand, path, rating, price="9.99", main="All Beauty"):
        return {"product_id": pid, "title": title, "brand": brand, "price": Decimal128(price) if price else None,
                "category": {"main": main, "path": path}, "rating": {"average": rating, "count": 10}}
    hair = ["Beauty & Personal Care", "Hair Care"]
    return [
        prod("P1", "Hair Chalk for Girls", "Shiyeen", hair + ["Hair Color"], 4.5),
        prod("P2", "Wig Human Hair", "Ebbfurln", hair + ["Wigs"], 3.0),
        prod("P3", "Face Cream", "Nivea", ["Beauty & Personal Care", "Skin Care"], 4.2, price=None),
        prod("P4", "Hair Brush", "Nivea", hair, 4.8, main=None),          # main absent
        prod("P5", "Shampoo", "Nivea", hair, 2.0, main="  "),             # main vide
    ]


@pytest.fixture
def db():
    d = mongomock.MongoClient().marketplace_db
    d.products.insert_many(make_products())
    with mock.patch.object(P, "get_db", return_value=d):
        yield d


# ---------- build_filter : pur, sans base ----------
@pytest.mark.parametrize("bad", [
    {"min_price": -1}, {"max_price": "10"}, {"min_price": True},
    {"min_price": 50, "max_price": 10}, {"min_rating": 6}, {"min_rating": -0.1}, {"min_rating": "4"},
])
def test_criteres_invalides_refuses(bad):
    with pytest.raises(ValueError):
        P.build_filter(bad)


def test_filtre_forme():
    f = P.build_filter({"main": "All Beauty", "path": ["A", "B"], "brand": "X",
                        "min_price": 5, "max_price": 20.5, "min_rating": 4})
    assert f["category.path.0"] == "A" and f["category.path.1"] == "B"
    assert f["brand"] == "X" and f["rating.average"] == {"$gte": 4}
    assert f["price"]["$type"] == "number"
    assert f["price"]["$gte"] == Decimal128("5") and f["price"]["$lte"] == Decimal128("20.5")
    assert len(f["$or"]) == 3
    assert P.build_filter({}) == {} and P.build_filter(None) == {}


# ---------- requetes sur base simulee ----------
def test_produit_par_id(db):
    assert P.find_product_by_id("P1")["title"] == "Hair Chalk for Girls"
    assert P.find_product_by_id("NOPE") is None


def test_categorie_inclut_sous_categories(db):
    r = P.filter_products({"path": ["Beauty & Personal Care", "Hair Care"]}, page_size=100)
    assert {i["product_id"] for i in r["items"]} == {"P1", "P2", "P4", "P5"}


def test_main_effective_vide_ou_absente(db):
    r = P.filter_products({"main": "Beauty & Personal Care"}, page_size=100)
    assert {i["product_id"] for i in r["items"]} == {"P4", "P5"}   # ceux dont path[0] sert de main


def test_marque_et_note(db):
    r = P.filter_products({"brand": "Nivea", "min_rating": 4.5})
    assert [i["product_id"] for i in r["items"]] == ["P4"]


def test_tri_par_defaut_et_pagination(db):
    r = P.filter_products({}, page=1, page_size=2)
    assert r["total"] == 5 and [i["product_id"] for i in r["items"]] == ["P4", "P1"]
    r2 = P.filter_products({}, page=2, page_size=2)
    assert [i["product_id"] for i in r2["items"]] == ["P3", "P2"]
    assert P.filter_products({}, page=1, page_size=1000)["page_size"] == 100


def test_mots_cles_repli_sans_index_texte(db):
    real = P._page
    calls = {"n": 0}

    def fake(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            raise OperationFailure("text index required", 27)
        return real(*a, **k)
    with mock.patch.object(P, "_page", side_effect=fake):
        r = P.search_by_keywords("hair HAIR")
    assert {i["product_id"] for i in r["items"]} == {"P1", "P2", "P4"}
    with pytest.raises(ValueError):
        P.search_by_keywords("   ")


def test_mots_cles_caracteres_speciaux_ne_cassent_pas_la_regex(db):
    real = P._page
    calls = {"n": 0}

    def fake(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            raise OperationFailure("x", 27)
        return real(*a, **k)
    with mock.patch.object(P, "_page", side_effect=fake):
        assert P.search_by_keywords("(hair")["total"] == 0


# ---------- hierarchie ----------
def test_category_id_identique_a_json_stringify():
    # JSON.stringify(["Beauty & Personal Care","Hair Care"]) -> sans espaces, sans echappement unicode
    assert P.category_id("A", ["A", "B"]) == '["A","A","B"]'
    assert P.category_id("é", ["x"]) == '["é","x"]'


def test_categorie_et_descendants(db):
    main = "Beauty & Personal Care"
    hair, wigs = [main, "Hair Care"], [main, "Hair Care", "Wigs"]
    c = P.category_id
    db.categories.insert_many([
        {"category_id": c(main, [main]), "name": main, "path": [main], "ancestors": [], "depth": 0},
        {"category_id": c(main, hair), "name": "Hair Care", "path": hair, "ancestors": [c(main, [main])], "depth": 1},
        {"category_id": c(main, wigs), "name": "Wigs", "path": wigs,
         "ancestors": [c(main, [main]), c(main, hair)], "depth": 2},
        {"category_id": c(main, [main, "Skin Care"]), "name": "Skin Care", "path": [main, "Skin Care"],
         "ancestors": [c(main, [main])], "depth": 1},
    ])
    names = [x["name"] for x in P.category_with_descendants(main, hair)]
    assert names == ["Hair Care", "Wigs"]
    assert len(P.category_with_descendants(main, [main])) == 4
