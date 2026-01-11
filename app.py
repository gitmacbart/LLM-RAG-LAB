import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from rag import update_schema_info, retrieve_relevant_info
from models import Session, Item
import json
import re

# Initialize LLM
llm = OllamaLLM(model="llama3.2:1b")  # Using smaller model for faster performance

# Update schema info on start
vectorstore = update_schema_info()

# Ensure sample data exists
session = Session()
if session.query(Item).count() == 0:
    sample_items = [
        Item(name="Laptop", description="Gaming laptop", quantity=5, category="Electronics"),
        Item(name="Book", description="Python programming guide", quantity=10, category="Education"),
        Item(name="Mouse", description="Wireless mouse", quantity=15, category="Electronics"),
        Item(name="Notebook", description="Spiral notebook", quantity=20, category="Stationery"),
    ]
    session.add_all(sample_items)
    session.commit()
session.close()

# Define prompt
prompt_template = """
You are a helpful assistant for managing an inventory database.

Database Schema:
{context}

Available Actions:
- add_item: Add a new item. Parameters: {{"name": "string", "description": "string", "quantity": number, "category": "string"}}
- list_items: List items. Parameters: {{}} or {{"category": "string"}}
- update_quantity: Update quantity. Parameters: {{"item_id": number, "new_quantity": number}}

CRITICAL INSTRUCTIONS:
- For ANY action (add, list, update): Respond with ONLY: ACTION: action_name followed by JSON parameters in curly braces
- For questions/info: Respond with ONLY: ANSWER: your response
- NEVER mix formats or add extra text
- ALWAYS include proper JSON parameters with curly braces

Examples:
User: "add a laptop" 
Response: ACTION: add_item {{"name": "laptop", "quantity": 1}}

User: "show all items"
Response: ACTION: list_items {{}}

User: "update item 1 to 5"
Response: ACTION: update_quantity {{"item_id": 1, "new_quantity": 5}}

User: "how many items?"
Response: ANSWER: There are 4 items in the database.

User Query: {query}
Response:"""

prompt = PromptTemplate.from_template(prompt_template)

# Functions
def add_item(name, description="", quantity=0, category=""):
    session = Session()
    item = Item(name=name, description=description, quantity=quantity, category=category)
    session.add(item)
    session.commit()
    session.close()
    return f"Added item: {name}"

def list_items(category=None):
    session = Session()
    if category:
        items = session.query(Item).filter(Item.category == category).all()
    else:
        items = session.query(Item).all()
    session.close()
    return "\n".join([f"{i.id}: {i.name} ({i.quantity}) - {i.description}" for i in items])

def update_quantity(item_id, new_quantity):
    session = Session()
    item = session.query(Item).get(item_id)
    if item:
        item.quantity = new_quantity
        session.commit()
        session.close()
        return f"Updated {item.name} quantity to {new_quantity}"
    session.close()
    return "Item not found"

# Streamlit app
st.title("LLM RAG Resource Management Lab")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt_text := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user"):
        st.markdown(prompt_text)

    # Retrieve relevant info
    relevant_docs = retrieve_relevant_info(vectorstore, prompt_text, k=2)
    context = "\n".join([doc.page_content for doc in relevant_docs])

    # Generate response
    full_prompt = prompt.format(context=context, query=prompt_text)
    response = llm.invoke(full_prompt)

    # Debug: show raw response
    st.write(f"Debug - Raw LLM response: {response}")

    # Check if it's an action or answer
    # Look for known action patterns in the response
    response_lower = response.lower()

    # Check for add_item action
    if "add_item" in response_lower:
        add_match = re.search(r'add_item\s*(\{.*?\})', response, re.IGNORECASE)
        if add_match:
            params_str = add_match.group(1)
            try:
                params = json.loads(params_str)
                result = add_item(**params)
                response = result
            except (json.JSONDecodeError, TypeError):
                response = "Invalid parameters for add_item"
        else:
            response = "Missing parameters for add_item"

    # Check for list_items action
    elif "list_items" in response_lower:
        list_match = re.search(r'list_items\s*(\{.*?\})', response, re.IGNORECASE)
        if list_match:
            params_str = list_match.group(1)
            try:
                params = json.loads(params_str)
                result = list_items(**params)
                response = result
            except (json.JSONDecodeError, TypeError):
                result = list_items()  # Default to list all
                response = result
        else:
            result = list_items()  # Default to list all
            response = result

    # Check for update_quantity action
    elif "update_quantity" in response_lower:
        update_match = re.search(r'update_quantity\s*(\{.*?\})', response, re.IGNORECASE)
        if update_match:
            params_str = update_match.group(1)
            try:
                params = json.loads(params_str)
                result = update_quantity(**params)
                response = result
            except (json.JSONDecodeError, TypeError):
                response = "Invalid parameters for update_quantity"
        else:
            response = "Missing parameters for update_quantity"

    else:
        # Check for ANSWER format
        answer_match = re.search(r'ANSWER:\s*(.*)', response, re.IGNORECASE | re.DOTALL)
        if answer_match:
            response = answer_match.group(1).strip()
        # If no known pattern, keep original response

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)