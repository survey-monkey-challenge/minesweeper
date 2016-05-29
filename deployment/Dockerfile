FROM python:3.5.1-slim

WORKDIR /project

# Install gcc for the installation of uwsgi
RUN apt-get update
RUN apt-get install -y gcc

# Only copy the deployment folder to install the requirements
# If we copy everything, any file change will invalidate the 
# cache and it will cause everything to be reinstalled
COPY deployment/requirements.txt /project/deployment/requirements.txt
RUN pip install -r deployment/requirements.txt

# nginx and supervisor
RUN apt-get install -y nginx supervisor
RUN echo "daemon off;" >> /etc/nginx/nginx.conf  # otherwise supervisor will try to restart it
COPY deployment/nginx.conf /etc/nginx/sites-enabled/default
COPY deployment/supervisor-app.conf /etc/supervisor/conf.d/
RUN mkdir -p /var/log/uwsgi  # For the uwsgi logs. See uwsgi.ini for more info

# Copy everything else and run the dev server
COPY . /project
RUN python manage.py collectstatic --noinput

# Run nginx and django under supervisord
EXPOSE 80
CMD ["supervisord", "-n"]
