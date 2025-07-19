# Demo Setup Guide

This guide provides step-by-step instructions for setting up and running the AI-powered Multi-Agent Recruitment System demo.

## Prerequisites

### System Requirements

- **Python**: 3.12 or higher
- **Operating System**: macOS, Linux, or Windows with WSL2
- **Memory**: At least 8GB RAM recommended
- **Storage**: 2GB free space for dependencies and data

### Required Accounts & API Keys

1. **OpenAI API Key**: Required for LLM and embeddings
   - Sign up at: https://openai.com/api/
   - Minimum $5 credit recommended for testing
2. **Neon PostgreSQL Database** (Optional - for production setup):
   - Sign up at: https://neon.tech/
   - Free tier sufficient for demo

## Quick Start (5 minutes)

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd thesis

# Verify Python version
python --version  # Should be 3.12+

# Install dependencies using uv
uv sync --frozen
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

**Required .env Configuration:**

```bash
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database (local SQLite for demo)
DATABASE_URL=sqlite:///./demo.db

# Cache & State
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Settings
HITL_CONFIDENCE_THRESHOLD=0.85
LOG_LEVEL=INFO
EMBEDDING_DIMENSION=1536

# Vector Database (local file)
MILVUS_LITE_FILE=./milvus_lite.db
MILVUS_COLLECTION_NAME=recruitment_embeddings
```

### 3. Start Services

```bash
# Start Redis (required for state management)
docker compose up -d redis

# Verify Redis is running
docker exec recruitment_redis redis-cli ping
# Should return: PONG
```

### 4. Run the Application

```bash
# Start the Chainlit application
uv run chainlit run src/main.py

# Alternative: if uv not available
python -m chainlit run src/main.py
```

### 5. Access the Demo

1. Open your browser to: http://localhost:8000
2. You should see the AI Recruitment Assistant welcome screen
3. System will automatically initialize on first load

## Detailed Setup Instructions

### Docker Services Setup

The demo requires Redis for state management. PostgreSQL is optional (SQLite used by default).

```bash
# View available services
cat docker-compose.yml

# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs if needed
docker compose logs redis

# Stop services (when done)
docker compose down
```

### Database Setup (Optional)

For production demo with PostgreSQL:

```bash
# Update .env with Neon database URL
DATABASE_URL=postgresql://username:password@ep-xxx.region.aws.neon.tech/recruitment_poc?sslmode=require

# Test database connection
uv run python -c "
from config import get_config
import asyncpg
config = get_config()
print('Database URL configured:', bool(config.get('database_url')))
"
```

### Vector Database Initialization

The system uses Milvus Lite for local vector storage:

```bash
# Milvus Lite file will be created automatically
# Location: ./milvus_lite.db (as specified in .env)

# Verify vector store after first run
ls -la milvus_lite.db
```

### Testing the Setup

```bash
# Run basic configuration test
uv run python src/config.py

# Test Redis connection
uv run python -c "
import redis
r = redis.Redis(host='localhost', port=6379)
print('Redis ping:', r.ping())
"

# Run unit tests (optional)
uv run python -m pytest tests/unit/ -v
```

## Demo Data Preparation

### Using Built-in Demo Mode

The application includes a built-in demo with sample data:

1. Start the application: `uv run chainlit run src/main.py`
2. In the chat interface, type: `demo`
3. The system will load sample job description and resume
4. Evaluation will run automatically

### Using Custom Test Scenarios

Use the test scenarios from `/demo/test_scenarios.md`:

1. Copy job descriptions and resumes from the scenarios
2. Upload them through the web interface
3. Click "evaluate" to see results

### File Upload Testing

You can also create files for upload testing:

```bash
# Create test files directory
mkdir -p demo/test_files

# Create sample job description file
cat > demo/test_files/job_python_senior.txt << EOF
Senior Python Developer - TechCorp Inc.

We are seeking an experienced Python developer...
[paste job description from test scenarios]
EOF

# Create sample resume file
cat > demo/test_files/resume_jane_smith.txt << EOF
JANE SMITH
Senior Software Engineer
[paste resume from test scenarios]
EOF
```

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors

```bash
# Ensure you're in the correct directory
pwd  # Should end with /thesis

# Reinstall dependencies
uv pip sync --force

# Verify Python path
python -c "import sys; print(sys.path)"
```

#### 2. OpenAI API errors

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connection
uv run python -c "
from openai import OpenAI
client = OpenAI()
response = client.models.list()
print('API connection successful')
"
```

#### 3. Redis connection failed

```bash
# Check if Redis container is running
docker ps | grep redis

# Restart Redis if needed
docker compose restart redis

# Check Redis logs
docker compose logs redis
```

#### 4. Port already in use (8000)

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process (replace PID)
kill -9 <PID>

# Or use a different port
uv run chainlit run src/main.py --port 8001
```

#### 5. Vector database initialization fails

```bash
# Remove existing vector database and restart
rm -f milvus_lite.db
uv run chainlit run src/main.py
```

### Debug Mode

For detailed debugging:

```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
uv run chainlit run src/main.py --debug

# Check application logs
tail -f ~/.chainlit/logs/chainlit.log
```

### Performance Optimization

For demo performance:

```bash
# Reduce embedding dimension for faster processing (optional)
# Edit .env:
EMBEDDING_DIMENSION=768  # Smaller, faster embeddings

# Use faster OpenAI model (optional)
# Edit src/config.py to use gpt-3.5-turbo instead of gpt-4
```

## Demo Presentation Tips

### Before the Demo

1. **Test everything**: Run through all scenarios once
2. **Prepare browser**: Open http://localhost:8000 in a clean tab
3. **Have backups**: Keep test scenarios document open
4. **Check timing**: Each scenario takes 2-5 minutes to process

### During the Demo

1. **Start with built-in demo**: Type `demo` for quick demonstration
2. **Explain loading states**: Highlight the step-by-step progress
3. **Discuss results**: Walk through confidence scores and bias detection
4. **Show different scenarios**: Perfect match, hidden gem, clear rejection

### After the Demo

1. **Stop services**: `docker compose down`
2. **Clean up**: Remove demo databases if needed
3. **Export logs**: Save interesting evaluation results

## System Architecture (For Technical Audience)

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Chainlit UI   │────│    Agent     │────│   Vector Store  │
│  (Web Interface)│    │ (src/agents) │    │ (Milvus Lite)   │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │
                       ┌──────────────┐    ┌─────────────────┐
                       │  OpenAI API  │    │      Redis      │
                       │(LLM+Embeddings)│   │ (State Mgmt)    │
                       └──────────────┘    └─────────────────┘
```

Key components:

- **Frontend**: Chainlit provides chat interface
- **Backend**: Unified recruitment agent orchestrates all logic
- **LLM**: OpenAI GPT-4 for reasoning and text processing
- **Embeddings**: OpenAI text-embedding-3-small for semantic matching
- **Vector Store**: Milvus Lite for similarity search
- **Cache**: Redis for state management and performance

## Support

If you encounter issues during demo setup:

1. **Check logs**: Look for error messages in terminal output
2. **Verify prerequisites**: Ensure all requirements are met
3. **Test components**: Use individual test commands provided above
4. **Environment**: Double-check .env configuration
5. **Resources**: Ensure sufficient memory and disk space

For additional help, refer to:

- Test scenarios: `/demo/test_scenarios.md`
- Technical documentation: `/docs/POC.md`
- Configuration details: `/src/config.py`
