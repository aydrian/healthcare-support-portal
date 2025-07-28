# RAG Service

The RAG (Retrieval-Augmented Generation) Service provides intelligent document management and AI-powered question answering for the Healthcare Support Portal. It combines vector search with OpenAI's GPT models to deliver contextually relevant responses.

## Features

- **Document Management:** CRUD operations with automatic embedding generation
- **Vector Search:** Semantic search using pgvector and OpenAI embeddings
- **AI Chat:** Context-aware responses powered by OpenAI GPT models
- **File Upload:** Process and embed various document formats
- **Authorization:** Role-based access control with Oso policies
- **Smart Chunking:** Intelligent text segmentation for optimal embedding
- **Context Filtering:** Search within specific patients or departments
- **Role-based Responses:** AI responses tailored to user roles

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL with pgvector extension
- OpenAI API key
- uv package manager
- Authentication Service running (for JWT validation)

### Installation

```bash
cd services/rag_service
uv sync
```

### Environment Variables

Create a `.env` file or set these environment variables:

```env
DEBUG=true
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare
OPENAI_API_KEY=your-openai-api-key-here

# Optional RAG Configuration
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CONTEXT_LENGTH=8000
SIMILARITY_THRESHOLD=0.7
MAX_RESULTS=5
```

### Running the Service

```bash
# Set environment variables and run
export PYTHONPATH="../../common/src:$PYTHONPATH"
export OPENAI_API_KEY="your-openai-api-key-here"
uv run uvicorn src.rag_service.main:app --reload --port 8003

# Or use the run script
./run.sh
```

The service will be available at http://localhost:8003

### API Documentation

Interactive API docs are available at:
- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

## API Endpoints

### Document Management

| Method | Endpoint | Description | Auth Required | Roles |
|--------|----------|-------------|---------------|-------|
| GET | `/api/v1/documents/` | List documents (authorized) | Yes | All |
| GET | `/api/v1/documents/{doc_id}` | Get specific document | Yes | Based on access rules |
| POST | `/api/v1/documents/` | Create new document | Yes | doctor, admin |
| POST | `/api/v1/documents/upload` | Upload document file | Yes | doctor, admin |
| DELETE | `/api/v1/documents/{doc_id}` | Delete document | Yes | admin |

### AI Chat & Search

| Method | Endpoint | Description | Auth Required | Roles |
|--------|----------|-------------|---------------|-------|
| POST | `/api/v1/chat/search` | Vector similarity search | Yes | All |
| POST | `/api/v1/chat/ask` | AI-powered Q&A | Yes | All |
| GET | `/api/v1/chat/conversation-history` | Get chat history | Yes | All |
| POST | `/api/v1/chat/feedback` | Submit response feedback | Yes | All |

### Health Check

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Service health check | No |
| GET | `/` | Service info | No |

## Example Usage

### Get Your JWT Token First

```bash
# Login via auth service
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dr_smith&password=secure_password"
```

### Create a Document

```bash
curl -X POST "http://localhost:8003/api/v1/documents/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Diabetes Management Protocol",
    "content": "Type 2 diabetes management includes monitoring blood glucose levels, dietary modifications, regular exercise, and medication adherence. Patients should check blood sugar levels at least twice daily and maintain HbA1c levels below 7%.",
    "document_type": "protocol",
    "department": "endocrinology",
    "is_sensitive": false
  }'
```

### Upload a Document File

```bash
curl -X POST "http://localhost:8003/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@protocol.txt" \
  -F "title=Patient Care Protocol" \
  -F "document_type=protocol" \
  -F "department=general" \
  -F "is_sensitive=false"
```

### Search Documents

```bash
curl -X POST "http://localhost:8003/api/v1/chat/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "diabetes treatment guidelines",
    "document_types": ["protocol", "guideline"],
    "department": "endocrinology",
    "limit": 10
  }'
```

Response:
```json
{
  "results": [
    {
      "embedding_id": 1,
      "document_id": 1,
      "content_chunk": "Type 2 diabetes management includes...",
      "document_title": "Diabetes Management Protocol",
      "document_type": "protocol",
      "department": "endocrinology",
      "similarity": 0.89
    }
  ],
  "total_results": 1
}
```

### Ask an AI Question

```bash
curl -X POST "http://localhost:8003/api/v1/chat/ask" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the best practices for diabetes management?",
    "context_department": "endocrinology",
    "max_results": 5
  }'
```

Response:
```json
{
  "response": "Based on the available protocols, diabetes management best practices include:\n\n1. Regular blood glucose monitoring (at least twice daily)\n2. Maintaining HbA1c levels below 7%\n3. Dietary modifications focusing on carbohydrate control\n4. Regular physical exercise\n5. Medication adherence as prescribed\n\nThese recommendations are based on current endocrinology department protocols.",
  "sources": [
    {
      "document_title": "Diabetes Management Protocol",
      "similarity": 0.89,
      "content_chunk": "Type 2 diabetes management includes..."
    }
  ],
  "token_count": 95,
  "context_used": true
}
```

## AI Models and Configuration

### Embedding Models
- **Default:** `text-embedding-3-small` (1536 dimensions)
- **Alternative:** `text-embedding-3-large` (3072 dimensions, higher accuracy)

### Chat Models
- **Default:** `gpt-4o-mini` (cost-effective, fast)
- **Alternative:** `gpt-4o` (higher quality responses)

### Chunking Strategy
- **Chunk Size:** 1000 characters (configurable)
- **Overlap:** 200 characters (preserves context across chunks)
- **Token-aware:** Uses tiktoken for accurate token counting

## Authorization Rules

### Document Access
- **Doctors:** Can read documents for their patients + general documents
- **Nurses:** Can read non-sensitive documents in their department
- **Admins:** Can read all documents

### Document Creation
- **Doctors:** Can create documents
- **Admins:** Can create and delete documents
- **Nurses:** Read-only access

### AI Chat Access
- All authenticated users can use AI chat
- Context is filtered based on document access permissions
- Response style adapts to user role

## Data Models

### Document Schema

```json
{
  "id": 1,
  "title": "Diabetes Management Protocol",
  "content": "Full document content...",
  "document_type": "protocol",
  "patient_id": null,
  "department": "endocrinology",
  "created_by_id": 1,
  "is_sensitive": false,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Chat Request Schema

```json
{
  "message": "What are the best practices for diabetes management?",
  "context_patient_id": null,
  "context_department": "endocrinology",
  "max_results": 5
}
```

### Search Request Schema

```json
{
  "query": "diabetes treatment",
  "document_types": ["protocol", "guideline"],
  "department": "endocrinology",
  "limit": 10
}
```

## Vector Search Details

### Similarity Calculation
- Uses cosine similarity with pgvector
- Threshold: 0.7 (configurable)
- Returns similarity score with results

### Performance Optimization
- Indexed vector columns
- Efficient similarity queries
- Authorized document filtering at database level

## Development

### Project Structure

```
src/rag_service/
├── __init__.py
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── routers/
│   ├── __init__.py
│   ├── documents.py     # Document management
│   └── chat.py          # AI chat and search
└── utils/
    ├── __init__.py
    ├── embeddings.py    # Vector operations
    └── text_processing.py  # Text chunking and cleaning
```

### Key Dependencies

- **FastAPI:** Web framework
- **OpenAI:** AI models and embeddings
- **pgvector:** Vector similarity search
- **tiktoken:** Token counting and text processing
- **numpy:** Numerical operations
- **common:** Shared models and utilities

### Testing

```bash
# Test embeddings (requires OpenAI API key)
uv run python -c "
from src.rag_service.utils.embeddings import generate_embedding
import asyncio
result = asyncio.run(generate_embedding('test text'))
print(f'Embedding length: {len(result)}')
"

# Test text processing
uv run python -c "
from src.rag_service.utils.text_processing import chunk_text
chunks = chunk_text('This is a test document with some content.')
print(f'Generated {len(chunks)} chunks')
"
```

## Performance Considerations

### Embedding Generation
- Batch processing for multiple documents
- Async operations to prevent blocking
- Error handling for API rate limits

### Vector Search
- Database-level similarity calculations
- Indexed vector columns for fast retrieval
- Result limiting to prevent large responses

### Token Management
- Context length monitoring
- Smart truncation for long contexts
- Token counting for cost estimation

## Security Features

- **API Key Security:** OpenAI keys stored in environment variables
- **Content Filtering:** Sensitive document access controls
- **Audit Trail:** Document creation and access logging
- **Input Validation:** Sanitization of user inputs
- **Rate Limiting:** Protection against API abuse

## Cost Optimization

### OpenAI Usage
- Use smaller embedding models when possible
- Implement caching for frequently accessed embeddings
- Monitor token usage for cost tracking
- Use cheaper chat models for non-critical responses

### Database Optimization
- Efficient vector storage with pgvector
- Proper indexing strategies
- Query optimization for large document sets

## Troubleshooting

### Common Issues

1. **OpenAI API errors:** Check API key and quota limits
2. **Vector search issues:** Ensure pgvector extension is installed
3. **Import errors:** Verify PYTHONPATH includes common package
4. **Embedding failures:** Check network connectivity and API limits
5. **Performance issues:** Monitor database query performance

### Debug Mode

Set `DEBUG=true` for detailed logging:
- Embedding generation logs
- Vector search query details
- AI response generation steps
- Authorization decision logging

### Monitoring

Key metrics to monitor:
- OpenAI API usage and costs
- Vector search performance
- Document processing success rates
- User query patterns
- Response quality feedback

## Integration

This service integrates with:
- **Auth Service:** User authentication and role information
- **Patient Service:** Patient-specific document context
- **Common Package:** Shared models and database utilities
- **OpenAI API:** Embeddings and chat completions
- **PostgreSQL + pgvector:** Vector storage and similarity search

## Contributing

1. Follow existing async/await patterns for AI operations
2. Add comprehensive error handling for external API calls
3. Update vector search logic carefully to maintain performance
4. Test with various document types and sizes
5. Consider cost implications of AI model changes
6. Update this README for new features and configuration options

## Future Enhancements

- Conversation history storage
- Advanced search filters
- Document summarization
- Multi-language support
- Custom embedding models
- Response quality analytics
