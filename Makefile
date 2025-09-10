# IGDB Game Recommendation System - Makefile
# Common commands for development and deployment

.PHONY: help install dev test clean lint format check-git-hygiene

# Default target
help: ## Show this help message
	@echo 'IGDB Game Recommendation System - Available Commands'
	@echo '===================================================='
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# =============================================================================
# Installation & Setup
# =============================================================================

install: ## Install all dependencies
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "📦 Installing Node.js dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed!"

install-dev: install ## Install development dependencies
	@echo "📦 Installing development tools..."
	pip install black isort flake8 pytest
	cd frontend && npm install --save-dev @types/node
	@echo "✅ Development dependencies installed!"

# =============================================================================
# Development Servers
# =============================================================================

dev: ## Start both API and frontend servers
	@echo "🚀 Starting development servers..."
	@echo "   API: http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Press Ctrl+C to stop all servers"
	@echo ""
	make -j2 api frontend

api: ## Start API server only
	@echo "🚀 Starting API server..."
	python scripts/start-api.py

frontend: ## Start frontend server only
	@echo "🚀 Starting frontend server..."
	cd frontend && npm run dev

# =============================================================================
# Data Collection
# =============================================================================

collect-data: ## Run data collection script
	@echo "📊 Collecting IGDB data..."
	python collect_data.py --games-limit 1000
	@echo "✅ Data collection completed!"

collect-small: ## Run data collection with small dataset
	@echo "📊 Collecting small IGDB dataset..."
	python collect_data.py --games-limit 10
	@echo "✅ Small dataset collection completed!"

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run linting on all code
	@echo "🔍 Running Python linting..."
	flake8 src/ --max-line-length=100 --ignore=E203,W503
	@echo "🔍 Running TypeScript linting..."
	cd frontend && npm run lint
	@echo "✅ Linting completed!"

format: ## Format all code
	@echo "🎨 Formatting Python code..."
	black src/ --line-length=100
	isort src/ --profile black
	@echo "🎨 Formatting TypeScript code..."
	cd frontend && npm run format
	@echo "✅ Code formatting completed!"

check-git-hygiene: ## Run Git hygiene validation
	@echo "🔍 Running Git hygiene validation..."
	./scripts/operations/maintenance/check-git-hygiene.sh --full
	@echo "✅ Git hygiene check completed!"

# =============================================================================
# Testing
# =============================================================================

test: ## Run all tests
	@echo "🧪 Running Python tests..."
	python -m pytest tests/ -v
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test
	@echo "✅ All tests completed!"

test-api: ## Test API endpoints
	@echo "🧪 Testing API endpoints..."
	curl -s http://localhost:8000/ | head -3
	curl -s http://localhost:8000/api/games | jq '.[0] | {id, name}' || echo "API not running"
	@echo "✅ API tests completed!"

# =============================================================================
# Docker
# =============================================================================

docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build
	@echo "✅ Docker images built!"

docker-up: ## Start services with Docker Compose
	@echo "🐳 Starting services with Docker..."
	docker-compose up -d
	@echo "✅ Services started!"

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker-compose down
	@echo "✅ Services stopped!"

# =============================================================================
# Database
# =============================================================================

db-migrate: ## Run database migrations (future)
	@echo "🗄️ Running database migrations..."
	@echo "⚠️  Database migrations not implemented yet"
	@echo "✅ Database migrations completed!"

db-seed: ## Seed database with sample data (future)
	@echo "🌱 Seeding database..."
	@echo "⚠️  Database seeding not implemented yet"
	@echo "✅ Database seeded!"

# =============================================================================
# Cleanup
# =============================================================================

clean: ## Clean up temporary files and caches
	@echo "🧹 Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	cd frontend && rm -rf .next/ node_modules/.cache/
	@echo "✅ Cleanup completed!"

clean-data: ## Clean up data files (WARNING: This removes all data!)
	@echo "⚠️  WARNING: This will remove all data files!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	rm -rf data/raw/* data/processed/*
	@echo "✅ Data files cleaned!"

# =============================================================================
# Documentation
# =============================================================================

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "⚠️  Documentation generation not implemented yet"
	@echo "✅ Documentation generated!"

# =============================================================================
# Deployment
# =============================================================================

deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	@echo "⚠️  Staging deployment not implemented yet"
	@echo "✅ Staging deployment completed!"

deploy-prod: ## Deploy to production environment
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Production deployment not implemented yet"
	@echo "✅ Production deployment completed!"

# =============================================================================
# Project Status
# =============================================================================

status: ## Show project status
	@echo "📊 IGDB Game Recommendation System - Project Status"
	@echo "=================================================="
	@echo ""
	@echo "🐍 Python Environment:"
	@which python
	@python --version
	@echo ""
	@echo "📦 Python Dependencies:"
	@pip list | grep -E "(fastapi|pandas|scikit-learn)" || echo "Not installed"
	@echo ""
	@echo "📦 Node.js Dependencies:"
	@cd frontend && npm list --depth=0 2>/dev/null | grep -E "(next|react|typescript)" || echo "Not installed"
	@echo ""
	@echo "🗂️  Data Files:"
	@ls -la data/processed/ | wc -l | xargs echo "Processed files:"
	@ls -la data/raw/ | wc -l | xargs echo "Raw files:"
	@echo ""
	@echo "🔍 Git Status:"
	@git status --porcelain | wc -l | xargs echo "Modified files:"
	@echo ""
	@echo "✅ Status check completed!"
