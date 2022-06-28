.PHONY = build format tests dump

build: tests
	./manage.py collectstatic --clear --no-input --verbosity=0
	docker-compose up --detach --build

format:
	autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports .
	isort .
	black .
	flake8 .

tests:
	pytest --cov

dump:
	./manage.py dumpdata users hitas > initial.json
	cat initial.json | jq > initial-formatted.json
	mv initial-formatted.json initial.json
