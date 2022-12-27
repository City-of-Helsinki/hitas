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
 format                             Format code.
 dump                               Create a database dump with the current schema.
 hitasmigrate                       Migrate oracle database.

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
	./manage.py makemigrations --check --no-color --no-input --dry-run
	pytest --cov

format:
	autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports .
	isort .
	black .
	flake8 .

dump:
	./manage.py dumpdata users authtoken hitas > initial.json
	cat initial.json | jq '.|=sort_by(.model, .pk)' > initial-formatted.json
	mv initial-formatted.json initial.json

hitasmigrate:
	./manage.py hitasmigrate --truncate
	DJANGO_SUPERUSER_PASSWORD=hitas python manage.py createsuperuser --username hitas --email foo@example.com --no-input
	./manage.py token --username hitas --set 52bf0606e0a0075c990fecc0afa555e5dae56404
