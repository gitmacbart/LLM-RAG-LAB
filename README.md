# LLM-RAG-LAB

A comprehensive lab for evaluating Local Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) for dynamic resource management using SQL databases.

## Overview

This project demonstrates an innovative approach to database interaction by replacing traditional web interfaces with natural language conversations powered by local LLMs. Users can manage inventory resources through conversational queries, leveraging Ollama for local model execution and ChromaDB for vector-based retrieval of schema information.

## Architecture

- **LLM Engine**: Ollama with Gemma 3 1B model for fast, local natural language processing
- **Embeddings**: Nomic Embed Text for semantic search
- **Vector Database**: ChromaDB for storing and retrieving schema/action information
- **Relational Database**: SQLite for persistent inventory data
- **UI Framework**: Streamlit for web-based chat interface

## Features

- **Natural Language Database Operations**:
  - Add new inventory items
  - List items by category or all
  - Update item quantities
  - Query inventory status

- **Dynamic RAG System**:
  - Schema-aware retrieval for accurate SQL operations
  - Context-aware responses based on database structure
  - Extensible for additional database schemas

- **Local-First Design**:
  - No external API dependencies
  - Privacy-preserving (all data stays local)
  - Offline-capable

## Performance Notes

The lab uses Gemma 3 1B model for optimal performance while maintaining good language understanding. Response times are typically 2-5 seconds per query on modern hardware. For even faster performance, consider:

- Using GPU acceleration if available (`ollama serve --gpu`)
- Further reducing RAG retrieval results (k=1)
- Implementing response caching for frequent queries

**Recent Updates**: Fixed ACTION parsing to handle both `ACTION:` and `ANSWER:` response formats from the LLM, ensuring reliable execution of database operations like "show me all items". Switched to Gemma 3 1B model for faster performance.

## Setup

### Prerequisites

1. **Install Ollama**: Follow instructions at [https://ollama.ai/](https://ollama.ai/)
2. **Pull Required Models**:
   ```bash
   ollama pull gemma3:1b
   ollama pull nomic-embed-text:latest
   ```

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory
2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Initialize the system**:
   ```bash
   python init.py
   ```
5. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open your browser to `http://localhost:8501`
2. Start chatting with the system using natural language queries like:
   - "Add a laptop to electronics with quantity 5"
   - "Show me all items"
   - "Update the quantity of item 1 to 10"
   - "What items do we have in electronics?"

## Testing

The application comes pre-loaded with sample data. Try these test queries:

### Basic Operations
- **List all items**: "show me all items" or "list all items"
- **Add new item**: "add a gaming mouse with quantity 3 in electronics category"
- **Update quantity**: "update item 1 to quantity 10"
- **Filter by category**: "show electronics items" or "list items in stationery"

### Sample Data
The system initializes with these items:
- Laptop (Gaming laptop, Qty: 5, Electronics)
- Book (Python programming guide, Qty: 10, Education)  
- Mouse (Wireless mouse, Qty: 15, Electronics)
- Notebook (Spiral notebook, Qty: 20, Stationery)

### Debug Information
The chat interface shows debug output including:
- Raw LLM responses
- Parsed actions and parameters
- Execution results

This helps understand how the RAG system interprets your queries and executes database operations.

## Project Structure

```
├── app.py              # Main Streamlit application
├── models.py           # SQLAlchemy database models
├── rag.py              # RAG system implementation
├── init.py             # Database and vector store initialization
├── requirements.txt    # Python dependencies
├── inventory.db        # SQLite database (created automatically)
├── chroma_db/          # ChromaDB vector storage
└── README.md           # This file
```

## Technical Details

### RAG Implementation

The RAG system stores vector embeddings of:
- Database schema descriptions
- Available action definitions
- Table structures and relationships

When a user query is received, relevant context is retrieved and provided to the LLM to ensure accurate interpretation and execution of database operations.

### LLM Integration

Uses Ollama's Python client for seamless integration with local models. The system prompts the LLM to output structured actions (JSON format) for database operations, which are then parsed and executed.

### Database Schema

Current schema supports inventory management:
- `items` table with fields: id, name, description, quantity, category

Easily extensible for additional tables and fields.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Future Enhancements

- Support for multiple database types (PostgreSQL, MySQL)
- Advanced query capabilities (joins, aggregations)
- Multi-user support
- API endpoints for external integrations
- Custom model fine-tuning for domain-specific tasks
