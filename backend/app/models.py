from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Boolean, Numeric, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.db import db

# --------------------------------------------
# 🔹 Base Units and Catalog
# --------------------------------------------

class Uom(db.Model):
    __tablename__ = "uoms"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)


class ItemCategory(db.Model):
    __tablename__ = "item_categories"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)


class Item(db.Model):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("item_categories.id"))
    base_uom_id = Column(Integer, ForeignKey("uoms.id"))
    brand = Column(String)
    active = Column(Boolean, default=True)
    # Use Text by default; if PostgreSQL is used, migrate this column to JSONB via Alembic
    spec = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("ItemCategory")
    uom = relationship("Uom")


# --------------------------------------------
# 🔹 BOM (Bill of Materials)
# --------------------------------------------

class Bom(db.Model):
    __tablename__ = "boms"
    id = Column(Integer, primary_key=True)
    product_item_id = Column(Integer, ForeignKey("items.id"))
    version = Column(Integer, default=1)
    effective_from = Column(Date, default=datetime.utcnow)
    effective_to = Column(Date)
    notes = Column(Text)

    product_item = relationship("Item", backref="boms")


class BomLine(db.Model):
    __tablename__ = "bom_lines"
    id = Column(Integer, primary_key=True)
    bom_id = Column(Integer, ForeignKey("boms.id", ondelete="CASCADE"))
    component_item_id = Column(Integer, ForeignKey("items.id"))
    qty_per = Column(Numeric(12, 4), nullable=False)
    uom_id = Column(Integer, ForeignKey("uoms.id"))
    scrap_pct = Column(Numeric(5, 2), default=0)
    is_optional = Column(Boolean, default=False)
    alt_group = Column(String)
    color_match_rule = Column(String)
    size_rule = Column(String)
    notes = Column(Text)

    bom = relationship("Bom", backref="lines")
    component_item = relationship("Item")
    uom = relationship("Uom")


# --------------------------------------------
# 🔹 Inventory and Warehouses
# --------------------------------------------

class Warehouse(db.Model):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)


class Location(db.Model):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    code = Column(String)
    type = Column(String, CheckConstraint("type IN ('STORAGE','RECEIVING','SHIPPING','WIP')"))

    warehouse = relationship("Warehouse", backref="locations")


class StockOnHand(db.Model):
    __tablename__ = "stock_on_hand"
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), primary_key=True)
    lot_code = Column(String, primary_key=True, default="")
    qty = Column(Numeric(14, 4), default=0)
    uom_id = Column(Integer, ForeignKey("uoms.id"))
    updated_at = Column(DateTime, default=datetime.utcnow)

    item = relationship("Item")
    location = relationship("Location")
    uom = relationship("Uom")


class StockMove(db.Model):
    __tablename__ = "stock_moves"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    from_location = Column(Integer)
    to_location = Column(Integer)
    qty = Column(Numeric(14, 4), nullable=False)
    uom_id = Column(Integer, ForeignKey("uoms.id"))
    move_type = Column(String)
    ref_type = Column(String)
    ref_id = Column(Integer)
    moved_at = Column(DateTime, default=datetime.utcnow)
    lot_code = Column(String)
    unit_cost = Column(Numeric(12, 4))

    item = relationship("Item")
    uom = relationship("Uom")


# --------------------------------------------
# 🔹 Procurement and Suppliers
# --------------------------------------------

class Supplier(db.Model):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String)
    payment_terms = Column(String)
    lead_time_days = Column(Integer)
    currency = Column(String)


class SupplierItem(db.Model):
    __tablename__ = "supplier_items"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    vendor_sku = Column(String)
    price = Column(Numeric(12, 4))
    moq = Column(Numeric(12, 4))
    incoterms = Column(String)

    supplier = relationship("Supplier", backref="items")
    item = relationship("Item")


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    po_number = Column(String, unique=True)
    status = Column(String)
    eta = Column(Date)
    currency = Column(String)
    total = Column(Numeric(12, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", backref="purchase_orders")


class PoLine(db.Model):
    __tablename__ = "po_lines"
    id = Column(Integer, primary_key=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey("items.id"))
    qty = Column(Numeric(12, 4))
    uom_id = Column(Integer, ForeignKey("uoms.id"))
    price = Column(Numeric(12, 4))
    lot_request = Column(String)
    shade_request = Column(String)

    po = relationship("PurchaseOrder", backref="lines")
    item = relationship("Item")
    uom = relationship("Uom")
