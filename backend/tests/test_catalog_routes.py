import pytest
from app import create_app
from app.db import db


@pytest.fixture
def client():
    """Crear una app en modo testing y una base de datos SQLite en memoria.

    Se crea la app, se sobreescribe la URI para que use sqlite:///:memory: y
    se crean las tablas dentro del app context. Al finalizar, se eliminan las
    tablas y se limpian las sesiones.
    """
    # Crear la app pasando la configuración de testing y la BD en memoria
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    # Crear contexto y tablas
    with app.app_context():
        from app import models  # importa modelos para registrar las clases

        db.create_all()

        # Insertar datos semilla mínimos para que GET /items y /boms devuelvan datos
        from app.models import Uom, ItemCategory, Item, Bom

        u = Uom(code="EA")
        c = ItemCategory(code="GEN")
        db.session.add_all([u, c])
        db.session.commit()

        item = Item(sku="SKU1", name="Seed Item", category_id=c.id, base_uom_id=u.id)
        db.session.add(item)
        db.session.commit()

        bom = Bom(product_item_id=item.id, version=1)
        db.session.add(bom)
        db.session.commit()

    # Proveer el test client al test
    with app.test_client() as client:
        yield client

    # Teardown: limpiar la base de datos
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_get_items(client):
    """GET /items debe devolver 200 y elementos con claves mínimas.

    Se verifica que la respuesta JSON sea una lista y que el primer elemento
    contenga al menos las claves 'id', 'sku' y 'name'.
    """
    resp = client.get("/items")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    first = data[0]
    # Comprobar claves mínimas
    for key in ("id", "sku", "name"):
        assert key in first


def test_get_boms(client):
    """GET /boms debe devolver 200 y elementos con claves de BOM.

    Verificamos que la respuesta tiene al menos un BOM y que contiene
    las claves 'id', 'product_item_id' y 'version'.
    """
    resp = client.get("/boms")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    first = data[0]
    for key in ("id", "product_item_id", "version"):
        assert key in first


def test_create_item(client):
    """POST /items debe crear un item válido.

    Dado que la ruta POST /items devuelve el id del nuevo item, aquí hacemos el
    POST y luego comprobamos mediante GET /items que el SKU nuevo está presente.
    Esto valida que la creación fue exitosa (201) y que el SKU quedó persistido.
    """
    new = {
        "sku": "SKU_NEW",
        "name": "New Item",
        "category": "GEN",
        "base_uom": "EA",
    }
    resp = client.post("/items", json=new)
    assert resp.status_code == 201
    # La ruta devuelve {'id': ...}; confirmar que el item aparece en GET /items
    resp2 = client.get("/items")
    assert resp2.status_code == 200
    items = resp2.get_json()
    skus = [i.get("sku") for i in items]
    assert "SKU_NEW" in skus
