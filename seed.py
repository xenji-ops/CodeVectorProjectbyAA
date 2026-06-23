from faker import Faker
from database import SessionLocal
from models import Product

fake = Faker()

db = SessionLocal()

products = []

categories = [
    "Electronics",
    "Books",
    "Fashion",
    "Sports",
    "Gaming"
]

for i in range(200000):

    product = Product(
        name=fake.word(),
        category=fake.random_element(categories),
        price=fake.random_int(
            min=100,
            max=100000
        )
    )

    products.append(product)

    if len(products) == 5000:

        db.bulk_save_objects(products)

        db.commit()

        products = []

# Save remaining products
if products:

    db.bulk_save_objects(products)

    db.commit()

print("Done")