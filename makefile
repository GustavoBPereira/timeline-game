SERVICE ?= api

.PHONY: run down build exec test create-migration migrate collect-static

run:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

shell:
	docker exec -ti $(SERVICE) bash

test:
	docker exec $(SERVICE) python manage.py test

create-migration:
	docker exec $(SERVICE) python manage.py makemigrations

migrate:
	docker exec $(SERVICE) python manage.py migrate

collect-static:
	docker exec $(SERVICE) python manage.py collectstatic --noinput --clear

load-occurrences:
	docker exec $(SERVICE) python manage.py load_occurrences