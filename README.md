# Healthcare Support Portal

A **Secure, Efficient, and Reliable Agentic RAG Application** built with Python microservices, featuring role-based access control, vector search, and AI-powered document assistance for healthcare professionals.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Services](#services)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Deployment](#deployment)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🏥 Overview

The Healthcare Support Portal is a demonstration of building secure, efficient, and reliable agentic RAG (Retrieval-Augmented Generation) applications using modern Python technologies. This system provides healthcare professionals with intelligent document management and AI-powered assistance while maintaining strict role-based access controls.

### Key Technologies

- **🔐 Security:** [Oso](https://osohq.com) for fine-grained authorization
- **🧠 AI/RAG:** [OpenAI](https://openai.com) for embeddings and chat completions
- **🗄️ Database:** PostgreSQL with [pgvector](https://github.com/pgvector/pgvector) for vector similarity search
- **🐍 Backend:** [FastAPI](https://fastapi.tiangolo.com) microservices with [SQLAlchemy](https://sqlalchemy.org)
- **📦 Package Management:** [uv](https://github.com/astral-sh/uv) for fast Python package management
- **🏗️ Architecture:** Python microservices in a monorepo

## ✨ Features

### 🔒 Security & Authorization
- **JWT-based authentication** with secure token management
- **Role-based access control** (Doctor, Nurse, Admin) using Oso policies
- **Fine-grained permissions** at the database level with SQLAlchemy integration
- **Department-based access controls** for multi-tenant healthcare environments

### 🧠 AI-Powered RAG
- **Document embeddings** using OpenAI's latest embedding models
- **Semantic search** with pgvector for fast similarity queries
- **Context-aware responses** that adapt to user roles and permissions
- **Smart document chunking** with token-aware text processing

### 🏥 Healthcare-Specific Features
- **Patient management** with doctor assignments and department organization
- **Medical document storage** with sensitivity levels and access controls
- **Audit trails** for all document access and modifications
- **HIPAA-compliant** design patterns (when properly configured)

### 🚀 Performance & Reliability
- **Microservices architecture** for scalability and maintainability
- **Database connection pooling** and query optimization
- **Asynchronous processing** for AI operations
- **Comprehensive error handling** and logging

## 🏗️ Architecture

```
Healthcare Support Portal
├── 🔐 Auth Service (Port 8001)
│   ├── User authentication & JWT tokens
│   ├── User management & roles
│   └── Authorization policy enforcement
│
├── 🏥 Patient Service (Port 8002)
│   ├── Patient CRUD operations
│   ├── Doctor-patient assignments
│   └── Department-based filtering
│
├── 🤖 RAG Service (Port 8003)
│   ├── Document management & embeddings
│   ├── Vector similarity search
│   ├── AI-powered Q&A with context
│   └── File upload & processing
│
├── 📦 Common Package
│   ├── Shared models & database schema
│   ├── Authentication utilities
│   ├── Oso authorization policies
│   └── Pydantic schemas
│
└── 🗄️ PostgreSQL + pgvector
    ├── User, Patient, Document tables
    ├── Vector embeddings storage
    └── Oso policy enforcement
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+** with pgvector extension
- **Docker & Docker Compose** (for database)
- **OpenAI API Key** (for RAG functionality)
- **uv package manager**

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd healthcare-support-portal

# Run initial setup
./setup.sh

# This will:
# - Create necessary directories
# - Copy .env.example files to .env
# - Generate secure SECRET_KEY
# - Make scripts executable
```

### 2. Configure Environment

```bash
# Edit the RAG service .env to add your OpenAI API key
nano services/rag_service/.env
# Set: OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Start Database

```bash
# Start PostgreSQL with pgvector
docker-compose up -d db

# Wait for database to be ready (about 10 seconds)
```

### 4. Install Dependencies

```bash
# Install dependencies for all services
cd common && uv sync && cd ..
cd services/auth_service && uv sync && cd ../..
cd services/patient_service && uv sync && cd ../..
cd services/rag_service && uv sync && cd ../..
```

### 5. Start All Services

```bash
# Start all services at once
./run_all.sh

# Or start individually:
cd services/auth_service && ./run.sh &
cd services/patient_service && ./run.sh &
cd services/rag_service && ./run.sh &
```

### 6. Verify Installation

Visit the API documentation:
- **🔐 Auth Service:** http://localhost:8001/docs
- **🏥 Patient Service:** http://localhost:8002/docs
- **🤖 RAG Service:** http://localhost:8003/docs

## 🎯 Services

### 🔐 Auth Service (Port 8001)
**Purpose:** User authentication, authorization, and management

**Key Features:**
- JWT token generation and validation
- User registration with role assignment
- Token refresh and session management
- Oso policy enforcement for user access

**Endpoints:**
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Current user info
- `GET /api/v1/users/` - List users (with authorization)

[📖 Detailed Documentation](services/auth_service/README.md)

### 🏥 Patient Service (Port 8002)
**Purpose:** Patient record management with role-based access

**Key Features:**
- Patient CRUD operations with authorization
- Doctor-patient assignment management
- Department-based filtering and search
- Soft delete for data preservation

**Endpoints:**
- `GET /api/v1/patients/` - List authorized patients
- `POST /api/v1/patients/` - Create new patient
- `GET /api/v1/patients/{id}` - Get patient details
- `PUT /api/v1/patients/{id}` - Update patient

[📖 Detailed Documentation](services/patient_service/README.md)

### 🤖 RAG Service (Port 8003)
**Purpose:** AI-powered document management and intelligent assistance

**Key Features:**
- Document upload with automatic embedding generation
- Vector similarity search using pgvector
- Context-aware AI responses with OpenAI GPT
- Role-based AI behavior and document access

**Endpoints:**
- `POST /api/v1/documents/` - Create/upload documents
- `POST /api/v1/chat/search` - Semantic document search
- `POST /api/v1/chat/ask` - AI-powered Q&A
- `GET /api/v1/documents/` - List authorized documents

[📖 Detailed Documentation](services/rag_service/README.md)

## 📚 API Documentation

Each service provides interactive API documentation:

| Service | Swagger UI | ReDoc |
|---------|------------|-------|
| Auth Service | http://localhost:8001/docs | http://localhost:8001/redoc |
| Patient Service | http://localhost:8002/docs | http://localhost:8002/redoc |
| RAG Service | http://localhost:8003/docs | http://localhost:8003/redoc |

## 🔧 Usage Examples

### 1. Register and Authenticate

```bash
# Register a new doctor
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr_smith",
    "email": "smith@hospital.com",
    "password": "secure_password",
    "role": "doctor",
    "department": "cardiology"
  }'

# Login to get JWT token
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dr_smith&password=secure_password"

# Response: {"access_token": "eyJ...", "token_type": "bearer"}
```

### 2. Manage Patients

```bash
# Create a new patient (use JWT token from login)
curl -X POST "http://localhost:8002/api/v1/patients/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "medical_record_number": "MRN-2024-001",
    "department": "cardiology",
    "assigned_doctor_id": 1
  }'

# List patients (filtered by authorization)
curl -X GET "http://localhost:8002/api/v1/patients/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. AI-Powered Document Assistance

```bash
# Upload a medical document
curl -X POST "http://localhost:8003/api/v1/documents/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Diabetes Management Protocol",
    "content": "Type 2 diabetes management includes monitoring blood glucose levels, dietary modifications, regular exercise, and medication adherence...",
    "document_type": "protocol",
    "department": "endocrinology",
    "is_sensitive": false
  }'

# Ask an AI question with context
curl -X POST "http://localhost:8003/api/v1/chat/ask" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the best practices for diabetes management?",
    "context_department": "endocrinology",
    "max_results": 5
  }'

# Search documents semantically
curl -X POST "http://localhost:8003/api/v1/chat/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "diabetes treatment guidelines",
    "document_types": ["protocol", "guideline"],
    "limit": 10
  }'
```

## 💻 Development

### Project Structure

```
healthcare-support-portal/
├── common/                     # Shared package
│   ├── src/common/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── db.py              # Database utilities
│   │   ├── auth.py            # Authentication utilities
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── policies/
│   │       └── authorization.polar  # Oso policies
│   └── pyproject.toml
├── services/
│   ├── auth_service/          # Authentication service
│   ├── patient_service/       # Patient management service
│   └── rag_service/           # RAG and AI service
├── docker-compose.yml         # Database setup
├── run_all.sh                 # Start all services
├── stop_all.sh                # Stop all services
└── setup.sh                   # Initial project setup
```

### Development Workflow

```bash
# Start development environment
./run_all.sh

# Make changes to code (auto-reload enabled)

# Stop all services
./stop_all.sh

# Or stop individual services
pkill -f "auth_service"
```

### Adding New Features

1. **Models:** Add to `common/src/common/models.py`
2. **Policies:** Update `common/src/common/policies/authorization.polar`
3. **APIs:** Add endpoints to appropriate service routers
4. **Tests:** Add tests in service directories (when implemented)

### Database Migrations

```bash
# Connect to database
docker exec -it healthcare-support-portal-db-1 psql -U postgres -d healthcare

# Or use alembic (if configured)
cd common && uv run alembic revision --autogenerate -m "description"
cd common && uv run alembic upgrade head
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and deploy with Docker Compose
docker-compose up -d

# Or build individual services
docker build -t healthcare-auth services/auth_service/
docker build -t healthcare-patient services/patient_service/
docker build -t healthcare-rag services/rag_service/
```

### Production Configuration

1. **Environment Variables:**
   ```bash
   export DEBUG=false
   export ENVIRONMENT=production
   export SECRET_KEY=your-super-secure-key
   export DATABASE_URL=postgresql://user:pass@prod-db:5432/healthcare
   export OPENAI_API_KEY=sk-your-production-key
   ```

2. **Database:**
   - Use managed PostgreSQL service
   - Enable pgvector extension
   - Configure connection pooling
   - Set up regular backups

3. **Security:**
   - Use HTTPS/TLS certificates
   - Configure proper CORS origins
   - Enable rate limiting
   - Set up monitoring and logging

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (if available).

## 🔒 Security

### Authentication & Authorization

- **JWT Tokens:** Secure token-based authentication
- **Role-Based Access:** Doctor, Nurse, Admin roles with different permissions
- **Policy Engine:** Oso policies for fine-grained authorization
- **Database Security:** Row-level security with SQLAlchemy integration

### Data Protection

- **Encryption:** Database connections use TLS
- **Sensitive Data:** Marked documents have additional access controls
- **Audit Trails:** All operations are logged with user attribution
- **Password Security:** Bcrypt hashing for user passwords

### Security Best Practices

- Regularly rotate JWT secrets
- Use environment variables for sensitive configuration
- Enable database connection encryption
- Implement rate limiting for API endpoints
- Monitor for suspicious access patterns

## 🔧 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check port availability
lsof -i :8001  # or 8002, 8003

# Check environment variables
env | grep -E "(SECRET_KEY|DATABASE_URL|OPENAI_API_KEY)"

# Check PYTHONPATH
echo $PYTHONPATH
```

#### Database Connection Issues
```bash
# Test database connection
docker exec -it healthcare-support-portal-db-1 psql -U postgres -d healthcare -c "SELECT version();"

# Check database URL format
# Should be: postgresql+psycopg2://user:pass@host:port/database
```

#### OpenAI API Issues
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/models"

# Check quota and usage
# Visit: https://platform.openai.com/usage
```

#### Import Errors
```bash
# Verify common package installation
cd services/auth_service
uv run python -c "from common.models import User; print('Success')"

# Check PYTHONPATH in run scripts
grep PYTHONPATH services/*/run.sh
```

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Getting Help

1. Check service-specific README files
2. Review API documentation at `/docs` endpoints
3. Check logs in `logs/` directory
4. Verify environment configuration

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `./setup.sh`
4. Make your changes
5. Add tests (when test framework is implemented)
6. Update documentation
7. Submit a pull request

### Code Standards

- **Python:** Follow PEP 8 style guidelines
- **FastAPI:** Use async/await for database operations
- **SQLAlchemy:** Use declarative models with proper relationships
- **Oso:** Write clear, testable authorization policies
- **Documentation:** Update README files for new features

### Pull Request Process

1. Ensure all services start without errors
2. Update relevant README files
3. Add example API calls for new endpoints
4. Verify authorization policies work correctly
5. Test with different user roles

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Oso](https://osohq.com)** - For excellent authorization framework and SQLAlchemy integration
- **[OpenAI](https://openai.com)** - For powerful embedding and chat completion models
- **[pgvector](https://github.com/pgvector/pgvector)** - For efficient vector similarity search in PostgreSQL
- **[FastAPI](https://fastapi.tiangolo.com)** - For the excellent Python web framework
- **[uv](https://github.com/astral-sh/uv)** - For fast Python package management

## 📞 Support

For questions, issues, or feature requests:

1. **Documentation:** Check service-specific README files
2. **Issues:** Create a GitHub issue with detailed information
3. **Discussions:** Use GitHub Discussions for general questions

---

**Built with ❤️ for healthcare professionals who deserve better tools.**

---

## 🏷️ Tags

`python` `fastapi` `rag` `openai` `postgresql` `pgvector` `oso` `sqlalchemy` `healthcare` `microservices` `jwt` `vector-search` `ai` `authorization` `uv`

