# AI Coding Assistant

A robust AI-powered coding assistant that analyzes code, explains functionality, identifies issues, suggests improvements, and helps with coding tasks across multiple programming languages. Now with knowledge base functionality to capture and export development thinking processes!

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-green)
![Version](https://img.shields.io/badge/version-1.0.0-orange)

## 🌟 Features

- **Multi-source Code Analysis**: Analyze Git repositories, local directories, individual files, or code snippets
- **Support for 25+ Programming Languages**: Python, JavaScript, TypeScript, Java, C/C++, C#, Go, Rust, and more
- **Knowledge Base System**: Capture conversations, code insights, and thinking processes for future reference
- **Export Functionality**: Export thinking processes and insights as Markdown, HTML, or JSON
- **Advanced Context Management**: Session-based conversation history and intelligent code context tracking
- **Multiple Interface Options**: Command-line interface, REST API, and WordPress plugin integration
- **Robust Error Handling**: Comprehensive error handling and logging at every level
- **Intelligent Response Refinement**: Language-specific heuristics to improve AI responses

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Knowledge Base Usage](#knowledge-base-usage)
  - [Export Functionality](#export-functionality)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Development Setup](#development-setup)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for repository analysis)

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

4. Set up LLM API key:
   - Edit your configuration file to include your API key for the chosen LLM provider
   - Alternatively, set the API key as an environment variable:

```bash
# For DeepSeek AI
export DEEPSEEK_API_KEY=your_api_key

# For Anthropic
export ANTHROPIC_API_KEY=your_api_key

# For OpenAI
export OPENAI_API_KEY=your_api_key
```

## 🚀 Usage

### Basic Usage

#### Command Line Interface

```bash
# Process current directory and enter interactive mode
python main.py

# Process a specific directory
python main.py --dir /path/to/directory --recursive

# Process a Git repository
python main.py --dir /path/to/repository --recursive

# Ask a direct question
python main.py --dir /path/to/code --query "Explain the main function in main.py"
```

#### Interactive Mode

Start interactive mode and enter commands:

```bash
python main.py --interactive

> help
Available commands:
  - Type your question and press Enter to submit
  - 'exit' or 'quit' to end the session
  - 'search' to search the knowledge base
  - 'export' to export conversations or thinking processes
  - 'knowledge' to see knowledge base statistics
```

### Knowledge Base Usage

The AI Coding Assistant includes a powerful knowledge base system that captures insights, conversations, and thinking processes during development.

#### Searching the Knowledge Base

```bash
# Search from command line
python main.py --search "architecture design"

# Or in interactive mode
> search
Search query: architecture design
```

#### Adding a Thinking Process

Create a JSON file with your thinking process and add it to the knowledge base:

```bash
# Add a thinking process from a file
python main.py --add-thinking examples/thinking_process_example.json
```

The thinking process JSON structure follows this format:

```json
{
  "title": "Feature Implementation Thinking Process",
  "description": "Thought process for implementing feature X",
  "tags": ["feature", "implementation", "design"],
  "steps": [
    {
      "title": "Problem Analysis",
      "content": "First, I analyzed the problem...",
      "language": "markdown"
    },
    {
      "title": "Solution Design",
      "content": "Next, I designed the solution...",
      "code": "function implementation() { ... }",
      "language": "javascript"
    }
  ]
}
```

### Export Functionality

Export conversations and thinking processes to share with your team or include in documentation.

#### Exporting from Interactive Mode

```bash
> export
Export type (conversation, thinking, all): thinking
Item ID: 12345-abcde
Format (markdown, html, json): markdown
```

#### Using the Export Script

For more advanced export options, use the dedicated export script:

```bash
# Export from knowledge base
python export_thinking.py kb --type thinking --id 12345-abcde --format markdown

# Export from file
python export_thinking.py file --input examples/thinking_process_example.json --type thinking

# Export all knowledge
python export_thinking.py kb --type all --format markdown
```

#### Export Format Example (Markdown)

```markdown
# Feature Implementation Thinking Process

_Exported on: 2025-05-10T12:34:56.789012_

## Summary

Thought process for implementing feature X

**Tags:** feature, implementation, design

## Thinking Process

### Step 1: Problem Analysis

First, I analyzed the problem...

### Step 2: Solution Design

Next, I designed the solution...

```javascript
function implementation() { ... }
```
```

## 🏗️ Architecture

The AI Coding Assistant is designed with a modular, multi-tier architecture:

```
AI Coding Assistant/
├── Main Application (main.py)
├── Knowledge Base (knowledge_manager.py, export_manager.py)
├── Code Processing Layer (code_source_scanner.py, enhanced_code_analyzer.py)
├── Repository Integration (git_parser.py, code_indexer.py)
├── Code Analysis (syntax_parser.py, semantic_analyzer.py)
├── Context Management (session_context.py, code_context_graph.py)
├── Reasoning (llm_interface.py, heuristics.py)
├── Interaction (query_processor.py, response_generator.py)
├── Utilities (config_utils.py)
└── WordPress Integration (wordpress-plugin.php, api_bridge.py)
```

### Component Flow

1. **Input Flow**: User Query → Query Processor → Context Management → Reasoning Engine → Response Generator → User
2. **Analysis Flow**: Code Source → Repository Integration → Code Analyzer → Syntax/Semantic Analysis → Knowledge Base
3. **Knowledge Management Flow**: Conversation → Knowledge Extraction → Knowledge Base → Export Manager → Documentation

For more details, see the [Technical Specification](docs/SPEC.md).

## ⚙️ Configuration

Configuration is managed through YAML files in the `config/` directory.

### Key Configuration Sections

```yaml
# Repository integration configuration
repository_integration:
  storage_dir: repositories
  max_repo_size_mb: 100
  index_file_extensions: [.py, .js, .ts, .java, ...]
  ignore_patterns: [node_modules, venv, .git, ...]

# Reasoning configuration
reasoning:
  model: deepseek-r1-distill-llama-70b
  max_tokens: 4000
  temperature: 0.7
  top_p: 0.9
  enable_heuristics: true

# Knowledge base configuration
knowledge_base:
  storage_dir: knowledge_base
  max_insights_per_conversation: 5
  auto_extract_insights: true
  tag_languages: [python, javascript, typescript, ...]

# Export configuration
export:
  export_dir: exports
  default_format: markdown
  include_metadata: true
  include_timestamps: true
  enable_syntax_highlighting: true
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
- DeepSeek AI, Anthropic, and OpenAI for LLM APIs
- [FastAPI](https://fastapi.tiangolo.com/) for the REST API

## 📚 Examples

### Example: Analyzing a Python Project

```bash
# Process the project
python main.py --dir /path/to/python_project --recursive

# Ask about the architecture
python main.py --query "Explain the overall architecture of this project"

# Get detailed explanations of specific components
python main.py --query "How does the data processing pipeline work?"
```

### Example: Capturing a Thinking Process

```bash
# Start interactive mode
python main.py --interactive

# Discuss your thinking process
> I'm trying to design a caching system for API responses. First, I need to determine the cache key strategy...

# Export the conversation as a thinking process
> export
Export type (conversation, thinking, all): conversation
Item ID: [conversation_id]
Format (markdown, html, json): markdown
```

### Example: Creating a Custom Thinking Process

Create a JSON file `my_thinking.json`:

```json
{
  "title": "API Caching System Design",
  "description": "Thought process for designing an efficient API caching system",
  "tags": ["caching", "api", "performance"],
  "steps": [
    {
      "title": "Cache Key Strategy",
      "content": "For the cache key, I decided to use a combination of the API endpoint, query parameters, and user context..."
    },
    {
      "title": "TTL Strategy",
      "content": "For time-to-live (TTL) values, I implemented a tiered approach...",
      "code": "function calculateTTL(endpoint, parameters) {\n  // Logic to determine appropriate TTL\n}",
      "language": "javascript"
    }
  ]
}
```

Add and export it:

```bash
python export_thinking.py file --input my_thinking.json --type thinking --format markdown
```
