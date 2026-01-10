from models import engine, Base
from rag import update_schema_info

# Create tables
Base.metadata.create_all(engine)

# Update schema info
vectorstore = update_schema_info()

print("Database and RAG initialized.")