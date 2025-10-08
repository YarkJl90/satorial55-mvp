from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError
from app.db import db
import json


catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.route("/items", methods=["GET"])
def list_items():
    from app import db
    from app.models import Item, ItemCategory
    query = Item.query
    category = request.args.get("category")
    q = request.args.get("q")
    if category:
        query = query.join(ItemCategory).filter(ItemCategory.code == category)
    if q:
        query = query.filter(Item.name.ilike(f"%{q}%"))
    items = query.all()
    return jsonify([
        {
            "id": item.id,
            "sku": item.sku,
            "name": item.name,
            "category": item.category.code if item.category else None,
            "base_uom": item.uom.code if item.uom else None,
            "brand": item.brand,
            "active": item.active,
            "spec": item.spec,
        }
        for item in items
    ])

@catalog_bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    from app.models import Item
    item = Item.query.get_or_404(item_id)
    return jsonify({
        "id": item.id,
        "sku": item.sku,
        "name": item.name,
        "category": item.category.code if item.category else None,
        "base_uom": item.uom.code if item.uom else None,
        "brand": item.brand,
        "active": item.active,
        "spec": item.spec,
    })

@catalog_bp.route("/items", methods=["POST"])
def create_item():
    from app import db
    from app.models import Item, ItemCategory, Uom
    data = request.get_json()
    try:
        category = ItemCategory.query.filter_by(code=data["category"]).first()
        uom = Uom.query.filter_by(code=data["base_uom"]).first()
        if not category or not uom:
            abort(400, description="Invalid category or UoM.")
        # Serialize 'spec' as a JSON string to store in a Text column
        spec_value = data.get("spec", {})
        if not isinstance(spec_value, str):
            spec_value = json.dumps(spec_value)

        item = Item(
            sku=data["sku"],
            name=data["name"],
            category_id=category.id,
            base_uom_id=uom.id,
            brand=data.get("brand"),
            active=data.get("active", True),
            spec=spec_value,
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({"id": item.id}), 201
    except IntegrityError:
        db.session.rollback()
        abort(409, description="Duplicate SKU.")
    except Exception as e:
        db.session.rollback()
        abort(400, description=str(e))

@catalog_bp.route("/boms", methods=["POST"])
def create_bom():
    from app import db
    from app.models import Bom, BomLine
    data = request.get_json()
    try:
        bom = Bom(
            product_item_id=data["product_item_id"],
            version=data.get("version", 1),
            effective_from=data.get("effective_from"),
            effective_to=data.get("effective_to"),
            notes=data.get("notes"),
        )
        db.session.add(bom)
        db.session.flush()
        for line in data.get("lines", []):
            bom_line = BomLine(
                bom_id=bom.id,
                component_item_id=line["component_item_id"],
                qty_per=line["qty_per"],
                uom_id=line["uom_id"],
                scrap_pct=line.get("scrap_pct", 0),
                is_optional=line.get("is_optional", False),
                alt_group=line.get("alt_group"),
                color_match_rule=line.get("color_match_rule"),
                size_rule=line.get("size_rule"),
                notes=line.get("notes"),
            )
            db.session.add(bom_line)
        db.session.commit()
        return jsonify({"id": bom.id}), 201
    except Exception as e:
        db.session.rollback()
        abort(400, description=str(e))

@catalog_bp.route("/boms/<int:bom_id>", methods=["GET"])
def get_bom(bom_id):
    from app.models import Bom
    bom = Bom.query.get_or_404(bom_id)
    return jsonify({
        "id": bom.id,
        "product_item_id": bom.product_item_id,
        "version": bom.version,
        "effective_from": str(bom.effective_from) if bom.effective_from else None,
        "effective_to": str(bom.effective_to) if bom.effective_to else None,
        "notes": bom.notes,
        "lines": [
            {
                "id": line.id,
                "component_item_id": line.component_item_id,
                "qty_per": float(line.qty_per),
                "uom_id": line.uom_id,
                "scrap_pct": float(line.scrap_pct) if line.scrap_pct else 0,
                "is_optional": line.is_optional,
                "alt_group": line.alt_group,
                "color_match_rule": line.color_match_rule,
                "size_rule": line.size_rule,
                "notes": line.notes,
            }
            for line in bom.lines
        ]
    })


@catalog_bp.route("/boms", methods=["GET"])
def list_boms():
    """Simple listing of BOMs for the API.

    Returns:
        A JSON list with the main fields for each BOM.
    """
    from app.models import Bom
    boms = Bom.query.all()
    return jsonify([
        {"id": b.id, "product_item_id": b.product_item_id, "version": b.version}
        for b in boms
    ])
