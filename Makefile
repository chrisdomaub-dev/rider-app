# Makefile for Django + Docker Compose
.PHONY: run runbuild buildnocache makemigrations migrate shell createsuperuser logs stop

run:
	docker compose up

runbuild:
	docker compose up --build

buildnocache:
	docker compose build --nocache

makemigrations:
	docker compose run --rm api python manage.py makemigrations

migrate:
	docker compose run --rm api python manage.py migrate

shell:
	docker compose run --rm api python manage.py shell

createsuperuser:
	docker compose run --rm api python manage.py createsuperuser

logs:
	docker compose logs -f api

stop:
	docker compose down
