"""Tests hors ligne (mongomock) : pytest tests/"""
import sys
from pathlib import Path
from unittest import mock

import mongomock
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.operations import update_stock as us
from src.operations.indexes import ensure_review_indexes, ensure_inventory_unique_index
from src.queries.reviews import sort_spec, SORTS


@pytest.fixture
def db():
    d = mongomock.MongoClient().marketplace_db
    with mock.patch.object(us, "get_db", return_value=d):
        yield d


@pytest.mark.parametrize("fn", [us.increase_stock, us.reserve_stock, us.confirm_sale])
@pytest.mark.parametrize("bad", [0, -1, 1.5, "3", True, None])
def test_quantite_invalide_refusee(db, fn, bad):
    with pytest.raises(ValueError):
        fn("P1", bad)
    assert db.inventory.count_documents({}) == 0


def test_increase_cree_fiche_avec_reserved_zero(db):
    us.increase_stock("P1", 5)
    d = db.inventory.find_one({"product_id": "P1"})
    assert d["quantity"] == 5 and d["reserved"] == 0 and "last_updated" in d
    us.increase_stock("P1", 3)
    assert db.inventory.find_one({"product_id": "P1"})["quantity"] == 8
    assert us.get_available("P1") == 8


def test_reserve_puis_vente(db):
    us.increase_stock("P1", 5)
    assert us.reserve_stock("P1", 3) is True
    assert us.reserve_stock("P1", 3) is False      # il ne reste que 2 disponibles
    assert us.confirm_sale("P1", 3) is True
    d = db.inventory.find_one({"product_id": "P1"})
    assert (d["quantity"], d["reserved"]) == (2, 0)


def test_vente_sans_reservation_refusee(db):
    us.increase_stock("P1", 5)
    assert us.confirm_sale("P1", 1) is False


def test_index_reviews_idempotent_et_anciens_supprimes(db):
    db.reviews.create_index([("product_id", 1), ("created_at", -1)], name="product_id_1_created_at_-1")
    names = ensure_review_indexes(db)
    assert "product_id_1_created_at_-1" not in names
    assert {"reviews_product_recent", "reviews_product_helpful", "reviews_product_rating"} <= set(names)
    assert ensure_review_indexes(db) == names


def test_index_unique_inventory(db):
    ensure_inventory_unique_index(db)
    db.inventory.insert_one({"product_id": "P1", "quantity": 1, "reserved": 0})
    with pytest.raises(Exception):
        db.inventory.insert_one({"product_id": "P1", "quantity": 2, "reserved": 0})


def test_index_unique_refuse_si_doublons(db):
    db.inventory.insert_many([{"product_id": "P1"}, {"product_id": "P1"}])
    with pytest.raises(RuntimeError):
        ensure_inventory_unique_index(db)


def test_tris_ont_un_index_correspondant():
    # chaque tri doit etre egal a un index (ou a son inverse exact) de la forme (product_id, champ, _id)
    idx = {("created_at", -1, 1), ("helpful_vote", -1, 1), ("rating", -1, 1)}
    for name in SORTS:
        (f, d), (_, tie) = sort_spec(name)
        assert (f, d, tie) in idx or (f, -d, -tie) in idx, name


def test_index_unique_existant_avec_autre_nom_est_reutilise(db):
    db.inventory.create_index([("product_id", 1)], unique=True, name="idx_inventory_product_id")
    assert ensure_inventory_unique_index(db) == "idx_inventory_product_id"
    names = [i["name"] for i in db.inventory.list_indexes()]
    assert "inventory_product_id_unique" not in names


def test_index_non_unique_existant_pas_touche(db):
    db.inventory.create_index([("product_id", 1)], name="idx_inventory_product_id")
    with pytest.raises(RuntimeError):
        ensure_inventory_unique_index(db)
    assert "idx_inventory_product_id" in [i["name"] for i in db.inventory.list_indexes()]
