.PHONY: frontend-api-client-build up-prod up down

frontend-api-client-build:
	cd frontend && npm run generate-api-client && cd ..

up-prod:
	docker compose up -d

up:
	docker compose up -d

down:
	docker compose down

clear:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

black:
	docker compose run backend black .
