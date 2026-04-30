"""
Complex Database Seeder for Presentation

Creates a realistic E-Commerce schema with connected tables:
Users, Categories, Products, Orders, OrderItems, and Reviews.
Populates it with rich dummy data to showcase the AI's JOIN capabilities.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import random
from db.database import DATABASE_URL

print(f"Connecting to Postgres to seed complex data...")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True)
    city = Column(String(50))
    country = Column(String(50))
    is_premium = Column(Boolean, default=False)
    signup_date = Column(DateTime, default=datetime.datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    department = Column(String(50))

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Float)
    stock_quantity = Column(Integer)
    average_rating = Column(Float, default=0.0)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20)) # Pending, Shipped, Delivered, Cancelled
    shipping_cost = Column(Float, default=5.00)

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Float)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer) # 1 to 5
    review_text = Column(Text)

# Recreate Schema securely
print("Dropping old tables and building new enterprise schema...")
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# --- SEED DATA ---
print("Generating Categories...")
categories_data = [
    ("Laptops", "Electronics"), ("Smartphones", "Electronics"), 
    ("Audio", "Electronics"), ("Desks", "Furniture"), 
    ("Chairs", "Furniture"), ("T-Shirts", "Apparel"), 
    ("Jackets", "Apparel"), ("Fitness", "Sporting Goods")
]
categories = [Category(name=c[0], department=c[1]) for c in categories_data]
session.add_all(categories)
session.commit()

print("Generating Users...")
cities = ["New York", "London", "San Francisco", "Tokyo", "Sydney", "Berlin", "Toronto", "Austin"]
users = []
for i in range(1, 31):
    u = User(
        first_name=f"User{i}", 
        last_name=f"Test_{i}",
        email=f"user{i}@example.com",
        city=random.choice(cities),
        country="USA" if random.random() > 0.4 else "International",
        is_premium=random.choice([True, False]),
        signup_date=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(10, 365))
    )
    users.append(u)
session.add_all(users)
session.commit()

print("Generating Products...")
products = []
for i in range(1, 61):
    cat = random.choice(categories)
    base_price = random.uniform(10.0, 1500.0) if cat.department == "Electronics" else random.uniform(15.0, 300.0)
    p = Product(
        name=f"{cat.name[:-1]} Model {chr(65+(i%26))}{i}", # e.g. "Laptop Model A1"
        category_id=cat.id,
        price=round(base_price, 2),
        stock_quantity=random.randint(0, 500),
        average_rating=round(random.uniform(3.0, 5.0), 1)
    )
    products.append(p)
session.add_all(products)
session.commit()

print("Generating Orders and OrderItems...")
statuses = ["Delivered", "Delivered", "Delivered", "Shipped", "Processing", "Cancelled"]
orders = []
for i in range(1, 101):
    usr = random.choice(users)
    o = Order(
        user_id=usr.id,
        order_date=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(1, 100)),
        status=random.choice(statuses),
        shipping_cost=0.0 if usr.is_premium else 15.00
    )
    session.add(o)
    session.commit()
    
    # Add 1 to 4 items per order
    for _ in range(random.randint(1, 4)):
        prod = random.choice(products)
        qty = random.randint(1, 3)
        oi = OrderItem(order_id=o.id, product_id=prod.id, quantity=qty, unit_price=prod.price)
        session.add(oi)

print("Generating Reviews...")
for _ in range(75):
    prod = random.choice(products)
    usr = random.choice(users)
    r = Review(
        product_id=prod.id,
        user_id=usr.id,
        rating=random.randint(1, 5),
        review_text=f"This {prod.name} is a {random.choice(['great', 'terrible', 'average', 'fantastic'])} product."
    )
    session.add(r)

session.commit()
session.close()

print("Database seeded with Complex E-commerce schema successfully!")
