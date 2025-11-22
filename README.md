# AI Chat Application

A simple Python web application with chat functionality using a local LLM, deployed on Kubernetes.

## Features

- Web-based chat interface
- OpenAI-compatible API using Ollama
- Kubernetes deployment with Minikube
- CI/CD with GitHub Actions

## Prerequisites

- Python 3.12+
- Docker
- Minikube
- kubectl
- Ollama (for local development)

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -e ".[dev]"

# Start Ollama and pull model
ollama serve
ollama pull llama3.2:1b

# Run the application
ai-chat
# Visit http://localhost:8000
```

### Kubernetes Deployment
```bash
# Setup cluster
make cluster-setup

# Add hostname to /etc/hosts (command shown in output)
echo "$(minikube ip -p ai-chat-cluster)    ai-chat" | sudo tee -a /etc/hosts

# Deploy application
make deploy

# Access at http://ai-chat
```

## Project Structure
```
├── src/ai_chat/       # Application source code
├── tests/             # Test suite
├── k8s/               # Kubernetes manifests
├── scripts/           # Automation scripts
├── .github/workflows/ # CI/CD pipeline
├── Dockerfile         # Container definition
└── pyproject.toml     # Project configuration
```

## Development
```bash
# Run tests
make test

# Run linting
make lint

# Format code
make format

# Build wheel
make build
```


## License

MIT
```

---