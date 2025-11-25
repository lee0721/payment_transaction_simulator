COMPOSE = docker compose

.PHONY: help up down restart logs ps seed build openapi

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

up: ## Build and launch the entire stack
	$(COMPOSE) up -d --build

down: ## Stop containers and remove orphans
	$(COMPOSE) down --remove-orphans

restart: down up ## Recreate the stack

logs: ## Tail logs from all services
	$(COMPOSE) logs -f

ps: ## Show running containers
	$(COMPOSE) ps

seed: ## Populate the database with demo data (service profile: tools)
	$(COMPOSE) run --rm seed

openapi: ## Regenerate shared OpenAPI schema
	PYTHONPATH=. python3 scripts/export_openapi.py
