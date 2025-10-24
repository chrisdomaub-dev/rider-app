# Rider

This project contains clean, simple implementation of a Dockerized Django Rest Framework project.

## SETTING UP

#### Clone Project from Pepository

1. go to desired folder and run `git clone https://github.com/chrisdomaub-dev/rider-app.git`

#### Create Virtual Environment

2. Create a virtual environment in the project root directory, activate it, and install dependencies:

   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - `pip install -r requirements.txt`

3. Setup default interpreter to the newly created venv if its not automatically identified.

#### Startup project

4. Start project by running:
   - `make runbuild`

#### Loading Dump Data or Create Super User

5. After building and the project is running, load the initial dump data:

   - `make loaddata` or `docker compose run --rm api python manage.py loaddata data.json`
   - initial admin account is email: `admin@rider.com` pass: `Start1234`

6. Optionally if you want to create a superuser:
   - `make createsuperuser` or `docker compose run --rm api python manage.py createsuperuser`

## Basic Commands

- To start:

  - `make runbuild` or `docker compose up --build`

- To makemigrations:

  - `make makemigration` or `docker compose run --rm api python manage.py makemigrations`

- To migrate:

  - `make migrate` or `docker compose run --rm api python manage.py migrate`

- To Create Superuser:

  - `make createsuperuser` or `docker compose run --rm api python manage.py createsuperuser`

- Or look for the Makefile in the project's root for more commands

## App Directory

- django admin url:
  `localhost:8000/admin/`
  `localhost:8000/admin/login/`

- swagger:
  `localhost:8000`

- redocs:
  `localhost:8000/redoc/`

## Bonus SQL:

- This will select all rides whose trips are over 1 hour, Identified by pickup timestamp and dropoff timestamp.

```
SELECT
    TO_CHAR(ride.pickup_time, 'YYYY-MM') AS month,
    user.first_name || ' ' || user.last_name AS driver_name,
    COUNT(*) AS trips_over_1hr
FROM ride JOIN user ON user.id = ride.driver_id

JOIN LATERAL (
    SELECT rideevent.created_at FROM rideevent
    WHERE rideevent.ride_id = ride.id AND rideevent.description LIKE '%Status changed to pickup%'
    ORDER BY rideevent.created_at DESC LIMIT 1
) AS pickup_event ON true

JOIN LATERAL (
    SELECT rideevent.created_at FROM rideevent
    WHERE rideevent.ride_id = ride.id AND rideevent.description LIKE '%Status changed to dropoff%'
    ORDER BY rideevent.created_at DESC LIMIT 1
) AS dropoff_event ON true

WHERE
    dropoff_event.created_at - pickup_event.created_at > interval '1 hour'

GROUP BY
    month, driver_name

ORDER BY
    month, driver_name;
```
