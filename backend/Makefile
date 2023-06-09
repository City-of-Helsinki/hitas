.PHONY: helptext
.PHONY: all
.PHONY: docker-build
.PHONY: docker-build-backend-only
.PHONY: tests
.PHONY: format
.PHONY: dump
.PHONY: hitasmigrate


define helptext

 Commands:

 all                                Format, test and build docker container stack.
 docker-build                       Build docker container stack.
 docker-build-backend-only          Build backend container only.
 tests                              Run tests.
 format                             Format code with pre-commit.
 dump                               Create a database dump with the current schema.
 hitasmigrate                       Migrate oracle database.
 bash                               Enter bash in the backend container.
 translate                          Make and complile translations.

endef

export helptext

# Help should be first so that make without arguments is the same as help
help:
	@echo "$$helptext"

all: format tests docker-build

docker-build:
	docker-compose up --detach --build

docker-build-backend-only:
	docker-compose build hitas-backend
	docker-compose up --detach hitas-backend

tests:
	poetry run python manage.py makemigrations --check --no-color --no-input --dry-run
	pytest --cov

format:
	poetry run pre-commit run --all-files

dump:
	poetry run python manage.py dumpdata users authtoken hitas > initial.json
	cat initial.json | jq '.|=sort_by(.model, .pk)' > initial-formatted.json
	mv initial-formatted.json initial.json

hitasmigrate:
	poetry run python manage.py hitasmigrate --truncate
	DJANGO_SUPERUSER_PASSWORD=hitas poetry run python manage.py createsuperuser --username hitas --email foo@example.com --no-input
	poetry run python manage.py token --username hitas --set 52bf0606e0a0075c990fecc0afa555e5dae56404

bash:
	docker compose exec hitas-backend bash

translate:
	poetry run python manage.py makemessages -l "fi"
	poetry run python manage.py compilemessages -l "fi"
