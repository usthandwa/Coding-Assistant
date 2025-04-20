# AI Coding Assistant

A robust AI-powered coding assistant that analyzes code, explains functionality, identifies issues, suggests improvements, and helps with coding tasks across multiple programming languages.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-green)

## 🌟 Features

- **Multi-source Code Analysis**: Analyze Git repositories, local directories, individual files, or code snippets
- **Support for 25+ Programming Languages**: Python, JavaScript, TypeScript, Java, C/C++, C#, Go, Rust, and more
- **Cloud-backed Architecture**: Redis caching and DynamoDB persistence for improved performance and reliability
- **Advanced Context Management**: Session-based conversation history and intelligent code context tracking
- **Multiple Interface Options**: Command-line interface, REST API, and WordPress plugin integration
- **Robust Error Handling**: Comprehensive error handling and logging at every level
- **Intelligent Response Refinement**: Language-specific heuristics to improve AI responses

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [WordPress Integration](#wordpress-integration)
- [Configuration](#configuration)
- [Development Setup](#development-setup)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Optional: Redis server (for caching)
- Optional: AWS account with DynamoDB access (for persistence)

### Installation Steps

1. Clone this repository:

```bash
git clone https://github.com/yourusername/ai-coding-assistant.git
cd ai-coding-assistant
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create configuration file:

```bash
cp config/default_config.yaml config/my_config.yaml
# Edit my_config.yaml with your settings
```

4. For AWS integration (optional):

```bash
cp config/aws_config.example.yaml config/aws_config.yaml
# Edit aws_config.yaml with your AWS credentials
```

## 🚀 Usage

### Command Line Interface

```bash
# Process current directory and enter interactive mode
python main.py

# Process a specific directory
python main.py --dir /path/to/directory --recursive

# Process a Git repository
python main.py --repo https://github.com/username/repository.git

# Process a single file
python main.py --file /path/to/file.py

# Ask a direct question
python main.py --dir /path/to/code --query "Explain the main function in main.py"

# Continue a previous session
python main.py --dir /path/to/code --session-id 12345-abcde
```

### REST API

Start the API server:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

Example API requests:

```bash
# Create a new session
curl -X POST http://localhost:8000/sessions -H "Content-Type: application/json"

# Process a directory
curl -X POST http://localhost:8000/process_directory \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/code", "recursive": true, "session_id": "your-session-id"}'

# Submit a query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the main function", "session_id": "your-session-id"}'
```

### Interactive Mode

When running in interactive mode, you can use the following commands:

- Type your question and press Enter to submit
- Type `help` to see available commands
- Type `session` to see current session information
- Type `exit` or `quit` to end the session

## 🏗️ Architecture

The AI Coding Assistant is designed with a modular, multi-tier architecture:

```
AI Coding Assistant/
├── main.py                           # Main entry point with CLI interface
├── api_server.py                     # FastAPI server for RESTful access
├── code_analysis/                    # Code analysis components
├── context_management/               # Context handling components
├── interaction/                      # User interaction components
├── reasoning/                        # AI reasoning components
├── repository_integration/           # Repository handling components
├── source_processing/                # Code source processing
├── utils/                            # Utility functions
└── wp_integration/                   # WordPress integration
```

### Multi-Tier Architecture

1. **Frontend Layer**:
   - Command Line Interface (main.py)
   - WordPress Plugin (wordpress-plugin.php)
   - RESTful API Server (api_server.py)

2. **Business Logic Layer**:
   - Code Processing (CodeSourceScanner, EnhancedCodeAnalyzer)
   - Analysis (SyntaxParser, SemanticAnalyzer)
   - Context Management (SessionContextStore, CodeContextGraph)
   - AI Reasoning (LLMInterface, HeuristicsEngine)
   - Response Handling (QueryProcessor, ResponseGenerator)

3. **Caching Layer**:
   - Redis Caching (RedisCache) for responses, analysis, and queries

4. **Persistence Layer**:
   - DynamoDB (DynamoDBManager) for session contexts, analysis, and history

### Data Flow

1. User requests → Frontend Layer
2. Request processing → Business Logic Layer
3. Check cache → Redis Caching Layer
4. If cache miss → Process and store in cache
5. For persistence → DynamoDB Storage Layer
6. Response formatting → Frontend Layer → User

## 📚 API Reference

The REST API provides the following endpoints:

### Sessions

- `POST /sessions` - Create a new session
  - Returns: `{"session_id": "uuid", "message": "Session created successfully"}`

### Directory Processing

- `POST /process_directory` - Process a directory or repository
  - Request body: `{"path": "/path/to/dir", "recursive": true, "session_id": "optional-uuid"}`
  - Returns: Details about the processed code

### Queries

- `POST /query` - Process a user query
  - Request body: `{"query": "Your question here", "session_id": "uuid"}`
  - Returns: AI assistant response

## 🔌 WordPress Integration

The AI Coding Assistant can be integrated with WordPress using the included plugin:

1. Copy the `wordpress-plugin.php` and associated files to your WordPress plugins directory
2. Activate the "AI Coding Agent" plugin from the WordPress admin
3. Configure the plugin in the WordPress admin under "AI Coding Agent"

The plugin provides:
- An admin interface for code exploration and queries
- REST API endpoints for programmatic access
- Session management for conversation context

## ⚙️ Configuration

Configuration is managed through YAML files in the `config/` directory:

### Main Configuration (default_config.yaml)

```yaml
repository_integration:
  storage_dir: repositories
  max_repo_size_mb: 100
  # ... other repository settings

code_analysis:
  enable_syntax_parsing: true
  enable_semantic_analysis: true
  # ... other analysis settings

context_management:
  storage_dir: sessions
  max_context_items: 50
  # ... other context settings

reasoning:
  model: deepseek-r1-distill-llama-70b
  max_tokens: 4000
  # ... other LLM settings

# ... other configuration sections
```

### AWS Configuration (aws_config.yaml)

```yaml
dynamodb:
  enabled: true
  region: us-east-1
  endpoint_url: null  # Use AWS service or local endpoint
  context_table: ai_coding_assistant_context
  analysis_table: ai_coding_assistant_analysis

redis:
  enabled: true
  host: localhost
  port: 6379
  db: 0
  password: null
  timeout: 5
```

## 💻 Development Setup

### Setting Up a Development Environment

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

3. Set up pre-commit hooks:

```bash
pre-commit install
```

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
cd docs
make html
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

Please make sure your code follows the project's coding standards and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [GitPython](https://github.com/gitpython-developers/GitPython) for Git integration
- [Tree-sitter](https://github.com/tree-sitter/py-tree-sitter) for code parsing
- [NetworkX](https://networkx.org/) for code relationship graphs
- [Redis](https://redis.io/) for caching
- [AWS DynamoDB](https://aws.amazon.com/dynamodb/) for persistence
- [FastAPI](https://fastapi.tiangolo.com/) for the REST API
