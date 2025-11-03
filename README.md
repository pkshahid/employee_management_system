# Employee Management System
-----------------------
Employee Management System is an app for managing empolyees. The task is
to develop the django using Django and backend REST API using Django REST Framework.

In this we have used SortableJs for implementing drag and droppable custom dynamic form fields (https://github.com/SortableJS/jquery-sortablejs).
Also we have used Bootstrap for styling templates.


# How to run/deploy the app

1. Install `docker` and `docker-compose` in the system.(https://docs.docker.com/engine/install/)

2. Clone the repository.

3. Change directory to the path where `compose.yml` file is placed.

4. Run `docker compose up -d` in terminal to start the API

5. To run tests `docker exec -it app-container python manage.py test` .
   
6. Run `docker compose down` in terminal to stop the API

------------------------------------------------------------
# Note:
1. This repository contains sample `env` file and values to check the application. Change them as requirement.
