# Requirements
- Python 3.3 or greater
- Django 1.9.6
- django-crispy-forms 1.6.0
- django-picklefield 0.3.2
- uWSGI 2.0.13.1

# Installation

## With docker (production version)
```shell
1. ./deployment/build_and_run_docker.sh
2. Go to http://docker_hostname (probably http://localhost if you are running the docker daemon on your linux box)
```

## Using virtualenv
```shell
1. python3.3 -m venv path_to_new_venv
2. source path_to_new_venv/bin/activate
3. pip install -r deployment/requirements.txt
4. python manage.py migrate
5. python manage.py runserver
6. Go to http://localhost:8000
```

## Without virtualenv
```shell
1. python3.3 -m pip install --user -r deployment/requirements.txt
2. python3.3 manage.py migrate
3. python3.3 manage.py runserver
4. Go to http://localhost:8000
```
