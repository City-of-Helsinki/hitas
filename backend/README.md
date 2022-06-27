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

4. Start the app by running `make`

5. Access Django admin from [localhost:8080/admin](http://localhost:8080/admin). Default username `hitas`/`hitas`


### Running development environment without Docker

* Create a database for this project
* Install Python requirements: `poetry install`
* Enable debug `echo 'DEBUG=True' >> .env` [And setup env variables](#environment-variables)
* Run `python manage.py migrate`
* Run `python manage.py runserver`
* Access Django admin from [localhost:8000/admin](http://localhost:8080/admin). Default username `hitas`/`hitas`

### Testing

* Running the tests: `make tests`

## Environment Variables

- Copy the template env file: `cp .env.template .env` and add values for the _placeholder_ variables in the `.env`
  file.

### Helpful commands

* Opening a shell in the container: `docker-compose run --rm hitas bash`
* Running code formatting and linting: `make format`
* Make a initial database dump: `make dump`
