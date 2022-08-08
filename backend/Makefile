.PHONY = all build format tests dump

all: format tests build

build:
	docker-compose up --detach --build

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
