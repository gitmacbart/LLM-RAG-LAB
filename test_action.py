import sys
sys.path.append('/home/arnaud/Developments/LLM-RAG-LAB')

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from rag import retrieve_relevant_info
import re
import json

# Initialize LLM
llm = OllamaLLM(model="llama3.2:1b")

# Define prompt (same as in app.py)
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

# Test query
query = "show me all items"
from rag import vectorstore
context_docs = retrieve_relevant_info(vectorstore, query)
context = "\n".join([doc.page_content for doc in context_docs])

# Format prompt
formatted_prompt = prompt.format(context=context, query=query)

# Get response
response = llm.invoke(formatted_prompt)

print("Raw LLM Response:")
print(response)
print("\n" + "="*50 + "\n")

# Parse ACTION or ANSWER with action
action_match = re.search(r'(?:ACTION|ANSWER):\s*(\w+)\s*(\{.*?\})?', response)
if action_match:
    action = action_match.group(1)
    params_str = action_match.group(2) if action_match.group(2) else "{}"
    print(f"Parsed Action: {action}")
    print(f"Params String: {params_str}")
    try:
        params = json.loads(params_str)
        print(f"Params: {params}")
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")

# Test the list_items function
if action == "list_items":
    from models import Session, Item
    session = Session()
    category = params.get("category")
    if category:
        items = session.query(Item).filter(Item.category == category).all()
    else:
        items = session.query(Item).all()
    
    if items:
        result = "\n".join([f"- {item.name}: {item.description} (Qty: {item.quantity}, Category: {item.category})" for item in items])
    else:
        result = "No items found."
    session.close()
    print(f"\nList Items Result:\n{result}")
else:
    print(f"Action {action} not tested.")