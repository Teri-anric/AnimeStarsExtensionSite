.PHONY: frontend-api-client-build build up down migration-autogenerate migration-upgrade clear

frontend-api-client-build:
	cd frontend && npm run generate-api-client && cd ..

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f backend frontend

migration-autogenerate:
	docker compose run --remove-orphans backend python -m alembic revision --autogenerate

migration-upgrade:
	docker compose run backend python -m alembic upgrade head

migration-down:
	docker compose run backend python -m alembic downgrade -1

clear:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

black:
	docker compose run backend black .
