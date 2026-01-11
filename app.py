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
- add_item: Add a new item. Parameters: name (string), description (string, optional), quantity (integer, default 0), category (string)
- list_items: List items. Parameters: category (string, optional) - use {{}} for all items
- update_quantity: Update quantity of an item. Parameters: item_id (integer), new_quantity (integer)

IMPORTANT: You MUST respond with EXACTLY one of these formats:
For actions: ACTION: <action_name> <json_parameters>
For questions: ANSWER: <your_answer>

User Query: {query}

Examples:
- "Add a laptop" -> ACTION: add_item {{"name": "laptop", "quantity": 1}}
- "List all items" -> ACTION: list_items {{}}
- "Update item 1 to 5" -> ACTION: update_quantity {{"item_id": 1, "new_quantity": 5}}
- "How many items are there?" -> ANSWER: There are X items in the database.

Respond with ACTION or ANSWER format only. For list_items, always include parameters even if empty.
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
    relevant_docs = retrieve_relevant_info(vectorstore, prompt_text, k=2)
    context = "\n".join([doc.page_content for doc in relevant_docs])

    # Generate response
    full_prompt = prompt.format(context=context, query=prompt_text)
    response = llm.invoke(full_prompt)

    # Debug: show raw response
    st.write(f"Debug - Raw LLM response: {response}")

    # Check if it's an action or answer
    # First check for ACTION or ANSWER with action anywhere in the response
    action_search = re.search(r"(?:ACTION|ANSWER):\s*(\w+)\s*(\{.*?\})?", response)
    if action_search:
        action_name = action_search.group(1)
        params_str = action_search.group(2) if action_search.group(2) else "{}"
        try:
            params = json.loads(params_str)
            if action_name == "add_item":
                result = add_item(**params)
            elif action_name == "list_items":
                result = list_items(**params)
            elif action_name == "update_quantity":
                result = update_quantity(**params)
            else:
                result = "Unknown action"
            response = result
        except json.JSONDecodeError:
            response = "Invalid action parameters"
    else:
        # Check for ANSWER
        answer_match = re.match(r"ANSWER:\s*(.*)", response.strip(), re.DOTALL)
        if answer_match:
            response = answer_match.group(1).strip()
        # else keep original response

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)