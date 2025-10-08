"""Procurement routes.

Blueprint that exposes endpoints for Suppliers, SupplierItems and PurchaseOrders.

Routes:
 - POST /suppliers, GET /suppliers
 - POST /supplier_items, GET /supplier_items
 - POST /pos, GET /pos
 - POST /pos/<id>/lines

Docstrings follow Google style and include explanatory comments.
"""
from flask import Blueprint, request, jsonify, abort
from app.db import db

procurement_bp = Blueprint("procurement", __name__)


@procurement_bp.route("/suppliers", methods=["POST"])
def create_supplier():
    """Create a supplier.

    Args:
        request.json: supplier data

    Returns:
        JSON with {'id': <new id>} and HTTP 201 on success.
    """
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        abort(400, description="'name' is required")

    from app.models import Supplier

    supplier = Supplier(
        name=name,
        country=data.get("country"),
        payment_terms=data.get("payment_terms"),
        lead_time_days=data.get("lead_time_days"),
        currency=data.get("currency"),
    )
    db.session.add(supplier)
    db.session.commit()
    return jsonify({"id": supplier.id}), 201


@procurement_bp.route("/suppliers", methods=["GET"])
def list_suppliers():
    """Return list of suppliers."""
    from app.models import Supplier

    suppliers = Supplier.query.all()
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "country": s.country,
            "payment_terms": s.payment_terms,
            "lead_time_days": s.lead_time_days,
            "currency": s.currency,
        }
        for s in suppliers
    ])


@procurement_bp.route("/supplier_items", methods=["POST"])
def create_supplier_item():
    """Create a supplier-item mapping.

    Validates that referenced supplier and item exist.
    """
    data = request.get_json() or {}
    supplier_id = data.get("supplier_id")
    item_id = data.get("item_id")
    if not supplier_id or not item_id:
        abort(400, description="supplier_id and item_id are required")

    from app.models import Supplier, Item, SupplierItem

    if not Supplier.query.get(supplier_id):
        abort(400, description="supplier not found")
    if not Item.query.get(item_id):
        abort(400, description="item not found")

    si = SupplierItem(
        supplier_id=supplier_id,
        item_id=item_id,
        vendor_sku=data.get("vendor_sku"),
        price=data.get("price"),
        moq=data.get("moq"),
        incoterms=data.get("incoterms"),
    )
    db.session.add(si)
    db.session.commit()
    return jsonify({"id": si.id}), 201


@procurement_bp.route("/supplier_items", methods=["GET"])
def list_supplier_items():
    """List supplier items."""
    from app.models import SupplierItem

    items = SupplierItem.query.all()
    return jsonify([
        {
            "id": i.id,
            "supplier_id": i.supplier_id,
            "item_id": i.item_id,
            "vendor_sku": i.vendor_sku,
            "price": float(i.price) if i.price is not None else None,
            "moq": float(i.moq) if i.moq is not None else None,
            "incoterms": i.incoterms,
        }
        for i in items
    ])


@procurement_bp.route("/pos", methods=["POST"])
def create_po():
    """Create a Purchase Order (PO).

    Validates that supplier exists. The PO initially has total=0; lines
    can be added with POST /pos/<id>/lines which will recalculate total.
    """
    data = request.get_json() or {}
    supplier_id = data.get("supplier_id")
    if not supplier_id:
        abort(400, description="supplier_id is required")

    from app.models import Supplier, PurchaseOrder

    if not Supplier.query.get(supplier_id):
        abort(400, description="supplier not found")

    po = PurchaseOrder(
        supplier_id=supplier_id,
        po_number=data.get("po_number"),
        status=data.get("status"),
        eta=data.get("eta"),
        currency=data.get("currency"),
        total=0,
    )
    db.session.add(po)
    db.session.commit()
    return jsonify({"id": po.id}), 201


@procurement_bp.route("/pos", methods=["GET"])
def list_pos():
    """List purchase orders."""
    from app.models import PurchaseOrder

    pos = PurchaseOrder.query.all()
    return jsonify([
        {
            "id": p.id,
            "supplier_id": p.supplier_id,
            "po_number": p.po_number,
            "status": p.status,
            "eta": str(p.eta) if p.eta else None,
            "currency": p.currency,
            "total": float(p.total) if p.total is not None else None,
        }
        for p in pos
    ])


@procurement_bp.route("/pos/<int:po_id>/lines", methods=["POST"])
def add_po_line(po_id: int):
    """Add a line to a PO and recalculate the PO total.

    The total is computed as sum(qty * price) for all lines of the PO.
    """
    data = request.get_json() or {}
    qty = data.get("qty")
    item_id = data.get("item_id")
    uom_id = data.get("uom_id")
    price = data.get("price")
    if qty is None or item_id is None or price is None:
        abort(400, description="qty, item_id and price are required")

    from app.models import PurchaseOrder, PoLine, Item

    po = PurchaseOrder.query.get(po_id)
    if not po:
        abort(404, description="PO not found")

    if not Item.query.get(item_id):
        abort(400, description="item not found")

    line = PoLine(
        po_id=po_id,
        item_id=item_id,
        qty=qty,
        uom_id=uom_id,
        price=price,
        lot_request=data.get("lot_request"),
        shade_request=data.get("shade_request"),
    )
    db.session.add(line)
    db.session.flush()

    # Recalculate the PO total
    total = db.session.query(db.func.coalesce(db.func.sum(PoLine.qty * PoLine.price), 0)).filter(PoLine.po_id == po_id).scalar()
    po.total = total
    db.session.commit()

    return jsonify({"id": line.id, "po_total": float(po.total)}), 201
