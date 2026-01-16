.PHONY: help install dev up down logs shell migrate makemigrations test lint format

# Colors
YELLOW := \033[1;33m
NC := \033[0m

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# ============ Local Development ============

install: ## Install dependencies with uv
	uv sync

dev: ## Run development server locally
	cd src && python manage.py runserver

# ============ Docker ============

up: ## Start all services (dev mode)
	docker compose -f docker-compose.dev.yml up -d

up-prod: ## Start all services (production mode)
	docker compose up -d

down: ## Stop all services
	docker compose -f docker-compose.dev.yml down

down-prod: ## Stop production services
	docker compose down

logs: ## View logs
	docker compose -f docker-compose.dev.yml logs -f

logs-api: ## View API logs
	docker compose -f docker-compose.dev.yml logs -f api

build: ## Build docker images
	docker compose -f docker-compose.dev.yml build

rebuild: ## Rebuild and restart
	docker compose -f docker-compose.dev.yml up -d --build

# ============ Django ============

shell: ## Open Django shell
	cd src && python manage.py shell

dbshell: ## Open database shell
	cd src && python manage.py dbshell

migrate: ## Run migrations
	cd src && python manage.py migrate

makemigrations: ## Create new migrations
	cd src && python manage.py makemigrations

createsuperuser: ## Create superuser
	cd src && python manage.py createsuperuser

collectstatic: ## Collect static files
	cd src && python manage.py collectstatic --noinput

# ============ Docker Django Commands ============

docker-migrate: ## Run migrations in docker
	docker compose -f docker-compose.dev.yml exec api python manage.py migrate

docker-makemigrations: ## Create migrations in docker
	docker compose -f docker-compose.dev.yml exec api python manage.py makemigrations

docker-shell: ## Open Django shell in docker
	docker compose -f docker-compose.dev.yml exec api python manage.py shell

docker-createsuperuser: ## Create superuser in docker
	docker compose -f docker-compose.dev.yml exec api python manage.py createsuperuser

# ============ Testing ============

test: ## Run tests
	cd src && pytest

test-cov: ## Run tests with coverage
	cd src && pytest --cov=apps --cov-report=html

# ============ Linting ============

lint: ## Run linters
	ruff check src/

lint-fix: ## Fix linting errors
	ruff check src/ --fix

format: ## Format code
	ruff format src/

typecheck: ## Run type checking
	mypy src/

# ============ Utilities ============

clean: ## Clean cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
