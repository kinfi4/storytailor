build:
	docker compose build
	cd backend && docker compose build
	cd frontend && docker compose build

run:
	docker compose up -d
	cd backend && docker compose up -d
	cd frontend && docker compose up -d

down:
	docker compose down
	cd backend && docker compose down
	cd frontend && docker compose down

logs:
	docker compose logs -f
	cd backend && docker compose logs -f
	cd frontend && docker compose logs -f
