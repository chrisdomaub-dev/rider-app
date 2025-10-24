# Rider

This project contains clean, simple implementation of a Dockerized Django Rest Framework project.

## SETTING UP

### Clone Project from Pepository

1. go to desired folder and run `git clone https://github.com/chrisdomaub-dev/rider-app.git`

### Create Virtual Environment

2. Create a virtual environment in the project root directory, activate it, and install dependencies:

   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - `pip install -r requirements.txt`

3. Setup default interpreter to the newly created venv if its not automatically identified.

### Startup project

4. Start project by running:
   - `make runbuild`

#### Create User

5. After building and the project is running, create a superuser:
   `docker compose run --rm web python manage.py createsuperuser`

## Basic Commands

- To start:

  - `make runbuild` or `docker compose up --build`

- To makemigrations:

  - `make makemigration` or `docker compose run --rm api python3 manage.py makemigrations`

- To migrate:

  - `make migrate` or `docker compose run --rm api python3 manage.py migrate`

- Or look for the Makefile in the project's root for more commands

## App Directory

- django admin url:
  `localhost:8000/admin/`
  `localhost:8000/admin/login/`

- swagger:
  `localhost:8000`

- redocs:
  `localhost:8000/redoc/`
