from app import db

class Uom(db.Model):
    __tablename__ = "uoms"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"<UoM {self.code}>"

class ItemCategory(db.Model):
    __tablename__ = "item_categories"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<ItemCategory {self.code}>"

class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("item_categories.id"))
    base_uom_id = db.Column(db.Integer, db.ForeignKey("uoms.id"))
    active = db.Column(db.Boolean, default=True)
    spec = db.Column(db.JSON)  # JSON para atributos flexibles (color, material, etc.)

    category = db.relationship("ItemCategory", backref="items")
    uom = db.relationship("Uom", backref="items")

    def __repr__(self):
        return f"<Item {self.sku}>"
