.PHONY: help install dev run test clean docker build deploy

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -r tests/requirements.txt

dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r tests/requirements.txt
	pip install -e .

run: ## Run the server
	python start.py

run-dev: ## Run the server in development mode
	DEBUG=true python start.py

test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=html

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

docker-build: ## Build Docker image
	docker build -t odoo-mcp-server .

docker-run: ## Run Docker container
	docker-compose up -d

docker-stop: ## Stop Docker container
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-shell: ## Get shell in Docker container
	docker-compose exec odoo-mcp-server bash

lint: ## Run code linting
	flake8 src/ tests/
	black --check src/ tests/

format: ## Format code
	black src/ tests/
	isort src/ tests/

setup-env: ## Set up environment file
	cp .env.example .env
	@echo "Please edit .env with your Odoo credentials"

health-check: ## Check server health
	curl -f http://localhost:8000/health

example: ## Run example client
	python examples/client_example.py

demo-modes: ## Demonstrate readonly/readwrite modes
	python examples/mode_demo.py

check-mode: ## Check current MCP mode
	curl -f http://localhost:8000/mcp/mode

claude-config: ## Generate Claude Desktop config interactively
	python tools/generate-claude-config.py --interactive

claude-examples: ## Show Claude Desktop config examples
	python tools/generate-claude-config.py --examples

check-setup: ## Check complete setup (dependencies, config, connections)
	python tools/check-setup.py

# Development targets
install-dev-tools: ## Install development tools
	pip install black flake8 isort pytest-cov

pre-commit: ## Run pre-commit checks
	black --check src/ tests/
	flake8 src/ tests/
	pytest tests/ -v

# Docker development
docker-dev: ## Run Docker in development mode
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production targets
deploy-prod: ## Deploy to production
	docker-compose -f docker-compose.prod.yml up -d

backup: ## Backup configuration
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz .env logs/

# Documentation
docs-serve: ## Serve documentation locally
	python -m http.server 8080 -d docs/