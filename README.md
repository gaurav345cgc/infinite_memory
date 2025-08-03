# EOXS AI Embedding Microservice

A FastAPI-based microservice for AI-powered document embedding, retrieval, and RAG (Retrieval-Augmented Generation) functionality.

## Features

- **Document Embedding**: Generate embeddings for user messages and AI responses
- **Similarity Search**: Query similar documents using vector similarity
- **RAG Integration**: Retrieve context and generate AI responses
- **Multi-thread Support**: Organize conversations by thread IDs
- **Monitoring**: API call tracking and performance monitoring
- **ChromaDB Integration**: Vector database for efficient similarity search

## Prerequisites

- Python 3.8+
- MongoDB (for monitoring)
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone (https://github.com/gaurav345cgc/infinite_memory)
   cd infinite_memory
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MONGO_URI=mongodb://localhost:27017/
   CHROMA_PERSIST_PATH=./chroma_persist
   PORT=3001
   ```

## Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:3001`

### API Endpoints

- `POST /embed` - Embed user messages
- `POST /embed-ai-response` - Embed AI responses
- `POST /rag-context` - Get RAG context
- `POST /rag-generate` - Generate AI responses with RAG
- `POST /query` - Query similar messages
- `GET /health` - Health check
- `GET /monitoring/stats` - Get API statistics

### Example Usage

```python
import requests

# Embed a message
response = requests.post("http://localhost:3001/embed", json={
    "userId": "user123",
    "messageId": "msg456",
    "content": "Hello, how are you?",
    "threadId": "thread789"
})

# Query similar messages
response = requests.post("http://localhost:3001/query", json={
    "userId": "user123",
    "query": "How are you doing?",
    "threadId": "thread789"
})
```

## Project Structure

```
📁 infinite/
├── 📄 app.py                    # Main FastAPI application
├── 📄 models.py                 # Pydantic models
├── 📄 db.py                     # ChromaDB operations
├── 📄 embedding.py              # Embedding generation
├── 📄 monitoring.py             # API monitoring
├── 📄 logging_config.py         # Logging configuration
├── 📄 utils.py                  # Utility functions
├── 📄 requirements.txt          # Python dependencies
├── 📁 chroma_persist/           # ChromaDB data
├── 📁 logs/                     # Application logs
└── 📁 venv/                     # Virtual environment
```

## Development

### Running Tests
```bash
python testing.py
```

### Monitoring
Access monitoring endpoints:
- `GET /monitoring/stats` - API call statistics
- `GET /monitoring/latency` - Performance metrics
- `GET /monitoring/endpoints` - Endpoint summary

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Required |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `CHROMA_PERSIST_PATH` | ChromaDB persistence directory | `./chroma_persist` |
| `PORT` | Server port | `3001` |

## Troubleshooting

1. **ChromaDB Issues**: Ensure the `chroma_persist` directory has write permissions
2. **MongoDB Connection**: Make sure MongoDB is running and accessible
3. **OpenAI API**: Verify your API key is valid and has sufficient credits
4. **Port Conflicts**: Change the `PORT` environment variable if 3001 is in use

## License

Made by gaurav345cgc
