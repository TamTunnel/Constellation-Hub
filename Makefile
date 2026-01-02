.PHONY: help demo seed reset-demo up down logs migrate test

help: ## Show this help message
	@echo "Constellation Hub - Make Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker-compose up -d
	@echo "✅ Services started. Frontend: http://localhost:3000, API docs: http://localhost:8001/docs"

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

demo: ## Run full demo setup (migrations + seed data)
	@chmod +x scripts/setup_demo.sh
	@./scripts/setup_demo.sh

seed: ## Load demo data only (assumes DB is already migrated)
	@cd backend && python scripts/load_demo_data.py

reset-demo: down ## Reset demo (stop services, clear data, restart with demo)
	docker-compose down -v
	docker-compose up -d
	@sleep 10
	@make demo

migrate: ## Run database migrations
	@cd backend && python scripts/run_migrations.py upgrade head

test: ## Run all tests
	@echo "Running backend tests..."
	@cd backend/core-orbits && pytest
	@cd backend/routing && pytest
	@cd backend/ground-scheduler && pytest
	@cd backend/ai-agents && pytest
	@echo "Running frontend tests..."
	@cd frontend/web && npm test

lint: ## Run linters
	@echo "Running backend linter..."
	@cd backend/core-orbits && ruff check .
	@cd backend/routing && ruff check .
	@cd backend/ground-scheduler && ruff check .
	@cd backend/ai-agents && ruff check .
	@echo "Running frontend linter..."
	@cd frontend/web && npm run lint
