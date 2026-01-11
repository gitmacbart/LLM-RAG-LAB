import chromadb
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os

# Initialize embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Initialize Chroma client
client = chromadb.PersistentClient(path="./chroma_db")

# Create or get collection
collection = client.get_or_create_collection(name="schema_info")

# Vector store
vectorstore = Chroma(
    client=client,
    collection_name="schema_info",
    embedding_function=embeddings,
)

def update_schema_info():
    """Update the vector store with current schema information."""
    global vectorstore
    # Clear existing collection
    try:
        client.delete_collection(name="schema_info")
    except:
        pass  # Collection may not exist

    # Create new vector store
    vectorstore = Chroma(
        client=client,
        collection_name="schema_info",
        embedding_function=embeddings,
    )

    # Schema documents
    docs = [
        Document(
            page_content="Table: items\nColumns: id (integer, primary key), name (string), description (text), quantity (integer), category (string)\nDescription: Stores inventory items with their details.",
            metadata={"type": "table", "name": "items"}
        ),
        Document(
            page_content="Actions: add_item(name, description, quantity, category), update_quantity(item_id, new_quantity), list_items(category=None), search_items(query)",
            metadata={"type": "actions"}
        ),
        # Add more as needed
    ]

    vectorstore.add_documents(docs)
    return vectorstore

def retrieve_relevant_info(vectorstore, query, k=2):
    """Retrieve relevant schema info for a query."""
    return vectorstore.similarity_search(query, k=k)