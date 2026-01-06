COMPOSE ?= docker compose
SERVICE ?= api

.PHONY: run down build exec test create-migration migrate collect-static

run:
	$(COMPOSE) up

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

exec:
	$(COMPOSE) exec $(SERVICE) sh

test:
	$(COMPOSE) exec $(SERVICE) pytest

create-migration:
	$(COMPOSE) exec $(SERVICE) python manage.py makemigrations

migrate:
	$(COMPOSE) exec $(SERVICE) python manage.py migrate

collect-static:
	$(COMPOSE) exec $(SERVICE) python manage.py collectstatic --noinput --clear
