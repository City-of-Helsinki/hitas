.PHONY = all docker-build docker-build-backend-only tests format dump

all: format tests docker-build

docker-build:
	docker-compose up --detach --build

docker-build-backend-only:
	docker-compose up --detach --build hitas-backend

tests:
	pytest --cov

format:
	autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports .
	isort .
	black .
	flake8 .

dump:
	./manage.py dumpdata users hitas > initial.json
	cat initial.json | jq > initial-formatted.json
	mv initial-formatted.json initial.json
