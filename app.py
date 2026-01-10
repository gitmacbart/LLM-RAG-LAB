import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from rag import update_schema_info, retrieve_relevant_info
from models import Session, Item
import json
import re

# Initialize LLM
llm = OllamaLLM(model="llama3.2")  # Assuming user has this model

# Update schema info on start
vectorstore = update_schema_info()

# Define prompt
prompt_template = """
You are a helpful assistant for managing an inventory database.

Database Schema:
{context}

Available Actions:
- add_item: Add a new item. Parameters: name (string), description (string, optional), quantity (integer, default 0), category (string)
- list_items: List items. Parameters: category (string, optional)
- update_quantity: Update quantity of an item. Parameters: item_id (integer), new_quantity (integer)

User Query: {query}

If the query is a request to perform an action, respond with ACTION: <action_name> <json_parameters>
Otherwise, respond with a helpful message.

Examples:
- "Add a laptop" -> ACTION: add_item {{"name": "laptop", "quantity": 1}}
- "List all items" -> ACTION: list_items {{}}
- "Update item 1 to 5" -> ACTION: update_quantity {{"item_id": 1, "new_quantity": 5}}
"""

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
    relevant_docs = retrieve_relevant_info(vectorstore, prompt_text)
    context = "\n".join([doc.page_content for doc in relevant_docs])

    # Generate response
    full_prompt = prompt.format(context=context, query=prompt_text)
    response = llm.invoke(full_prompt)

    # Check if it's an action
    action_match = re.match(r"ACTION:\s*(\w+)\s*(\{.*\})", response.strip())
    if action_match:
        action_name = action_match.group(1)
        params = json.loads(action_match.group(2))
        if action_name == "add_item":
            result = add_item(**params)
        elif action_name == "list_items":
            result = list_items(**params)
        elif action_name == "update_quantity":
            result = update_quantity(**params)
        else:
            result = "Unknown action"
        response = result
    else:
        # Normal response
        pass

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)