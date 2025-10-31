#!/bin/bash

python manage.py migrate

gunicorn livestock_management.wsgi:application --bind 0.0.0.0:$PORT
