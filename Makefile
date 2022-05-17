.DEFAULT_GOAL := help
.PHONY: help
help: ## ℹ️ Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: run
start: run
run: ## 🚀 Run all the components quickly
	@echo "🚀 Launching the Backend of the Software Passport platform"
	docker compose up -d
	@sleep 3
	@echo "🍔 Executing database migrations"
	docker compose exec api alembic upgrade head

logs: ## 📋 Show the logs of the containers
	@echo "📋 Showing the logs of the containers"
	docker compose logs -f

down: halt
stop: halt
halt: ## 💔 Stop all the components
	@echo "💔 Stopping the Docker containers"
	docker compose down

clean: ## 🗑  Clean the containers
	@echo "🗑 Cleaning the Docker containers"
	docker compose down -v --rmi all --remove-orphans


