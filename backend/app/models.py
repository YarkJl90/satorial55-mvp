from . import db

# =========================================================
# MODELOS BASE PARA SATORIAL55 MVP
# =========================================================

class TimestampMixin:
    """Agrega columnas automáticas de creación y actualización."""
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class Supplier(db.Model, TimestampMixin):
    """Tabla de proveedores"""
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    country = db.Column(db.String(50))

    items = db.relationship("Item", back_populates="supplier", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Supplier {self.name}>"


class Item(db.Model, TimestampMixin):
    """Tabla de productos asociados a un proveedor"""
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)
    supplier = db.relationship("Supplier", back_populates="items")

    def __repr__(self):
        return f"<Item {self.name}, ${self.price}>"


class User(db.Model, TimestampMixin):
    """Usuarios del sistema"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), default="user")

    def __repr__(self):
        return f"<User {self.name}>"
