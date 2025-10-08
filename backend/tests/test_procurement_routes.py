import pytest
from app import create_app
from app.db import db


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        from app import models
        db.create_all()
        # Crear unidad y categoría e item para referencias
        from app.models import Uom, ItemCategory, Item
        u = Uom(code="EA")
        c = ItemCategory(code="GEN")
        db.session.add_all([u, c])
        db.session.commit()
        item = Item(sku="PO_ITEM", name="PO Item", category_id=c.id, base_uom_id=u.id)
        db.session.add(item)
        db.session.commit()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_create_supplier_and_list(client):
    """Crear un supplier y comprobar que aparece en GET /suppliers."""
    resp = client.post("/suppliers", json={"name": "Acme"})
    assert resp.status_code == 201
    sid = resp.get_json()["id"]

    resp2 = client.get("/suppliers")
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert any(s["id"] == sid for s in data)


def test_create_supplier_item_and_list(client):
    """Crear supplier_item validando supplier e item existen."""
    # Crear supplier
    r = client.post("/suppliers", json={"name": "Vendor"})
    sid = r.get_json()["id"]

    # Obtener item id
    from app.models import Item
    with client.application.app_context():
        item = Item.query.filter_by(sku="PO_ITEM").first()

    resp = client.post("/supplier_items", json={"supplier_id": sid, "item_id": item.id, "vendor_sku": "VSKU", "price": 10})
    assert resp.status_code == 201
    iid = resp.get_json()["id"]

    resp2 = client.get("/supplier_items")
    assert resp2.status_code == 200
    assert any(i["id"] == iid for i in resp2.get_json())


def test_create_po_and_add_lines(client):
    """Crear una PO y añadir líneas; comprobar que total se calcula correctamente."""
    # Crear supplier
    r = client.post("/suppliers", json={"name": "Vendor2"})
    sid = r.get_json()["id"]

    # Crear PO
    r2 = client.post("/pos", json={"supplier_id": sid, "po_number": "PO123"})
    assert r2.status_code == 201
    po_id = r2.get_json()["id"]

    # Obtener item id
    from app.models import Item
    with client.application.app_context():
        item = Item.query.filter_by(sku="PO_ITEM").first()

    # Añadir línea
    r3 = client.post(f"/pos/{po_id}/lines", json={"item_id": item.id, "qty": 2, "price": 5, "uom_id": item.base_uom_id})
    assert r3.status_code == 201
    body = r3.get_json()
    assert "po_total" in body
    assert body["po_total"] == 10.0
