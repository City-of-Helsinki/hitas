# Hitas backend for City of Helsinki 

## Prerequisites

* [Python 3.10](https://www.python.org/)
* [Poetry](https://github.com/python-poetry/poetry#installation)
* PostgreSQL 13

or

* [Docker](https://docs.docker.com/get-docker/)

## Get the Development Environment Up and Running

1. Clone this repository

2. Ented the backend directory `cd hitas/backend`

3. [Follow the instructions for environment variables](#environment-variables)

4. Start the app `docker-compose up`

5. Access Django admin from [localhost:8000/admin](http://localhost:8000/admin) 


### Running development environment without Docker

* Create a database for this project
* Install Python requirements: `poetry install`
* Enable debug `echo 'DEBUG=True' >> .env` [And setup env variables](#environment-variables)
* Run `python manage.py migrate`
* Run `python manage.py runserver 0.0.0.0:8000`

### Testing

* Running the tests in Docker: `docker-compose run --no-deps --rm --entrypoint='/bin/sh -c' hitas "pytest"`
* Running the tests: `pytest`
* Checking the project test coverage: `pytest --cov`

## Environment Variables

- Copy the template env file: `cp .env.template .env` and add values for the _placeholder_ variables in the `.env`
  file.

### Helpful commands

* Opening a shell in the container: `docker-compose run --rm hitas bash`
* Running code formatting and linting: `sh format.sh`
