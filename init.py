from models import engine, Base
from rag import update_schema_info

# Create tables
Base.metadata.create_all(engine)

# Update schema info
vectorstore = update_schema_info()

# Add some sample data
from models import Session, Item
session = Session()
if session.query(Item).count() == 0:  # Only add if empty
    sample_items = [
        Item(name="Laptop", description="Gaming laptop", quantity=5, category="Electronics"),
        Item(name="Book", description="Python programming guide", quantity=10, category="Education"),
        Item(name="Mouse", description="Wireless mouse", quantity=15, category="Electronics"),
        Item(name="Notebook", description="Spiral notebook", quantity=20, category="Stationery"),
    ]
    session.add_all(sample_items)
    session.commit()
session.close()

print("Database and RAG initialized with sample data.")