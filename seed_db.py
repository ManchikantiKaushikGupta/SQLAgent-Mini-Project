"""
Database Seeder

Creates some dummy tables and data so the AI has something to query.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
from db.database import DATABASE_URL

print(f"Connecting to {DATABASE_URL}...")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    signup_date = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    category = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    order_date = Column(DateTime, default=datetime.datetime.utcnow)

# Drop existing tables and recreate
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Add dummy data
print("Inserting dummy data...")
u1 = User(name="Alice", email="alice@example.com")
u2 = User(name="Bob", email="bob@example.com")
u3 = User(name="Charlie", email="charlie@example.com")

p1 = Product(name="Laptop", price=1200.00, category="Electronics")
p2 = Product(name="Mouse", price=25.50, category="Accessories")
p3 = Product(name="Keyboard", price=45.00, category="Accessories")
p4 = Product(name="Desk", price=250.00, category="Furniture")

session.add_all([u1, u2, u3, p1, p2, p3, p4])
session.commit()

# Create some orders
o1 = Order(user_id=u1.id, product_id=p1.id, quantity=1)
o2 = Order(user_id=u1.id, product_id=p2.id, quantity=2)
o3 = Order(user_id=u2.id, product_id=p3.id, quantity=1)
o4 = Order(user_id=u3.id, product_id=p4.id, quantity=2)
o5 = Order(user_id=u3.id, product_id=p2.id, quantity=1)

session.add_all([o1, o2, o3, o4, o5])
session.commit()

session.close()
print("Database seeded successfully with Users, Products, and Orders!")
