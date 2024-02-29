#!/bin/bash

touch README.md

mkdir templates
mkdir static
mkdir static/css
mkdir static/img
mkdir static/js
mkdir media

poetry init --no-interaction

poetry add django=^5.0.2
poetry add gunicorn=^21.2.0
poetry add psycopg2-binary=^2.9.9
poetry add environs[django]=^10.3.0
poetry add django-allauth=^0.61.1
# poetry add django-debug-toolbar=^4.3.0

django-admin startproject config .
rm db.sqlite
django-admin startapp users

docker-compose up --build
