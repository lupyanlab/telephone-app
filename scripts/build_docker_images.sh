#!/bin/bash

# Build 'base' image. Must be built first as all other images depend on it.
docker build -t jcalazan/base --no-cache ../../docker-django-local/base

# Build 'postgresql' image.
docker build -t jcalazan/postgresql --no-cache ../../docker-django-local/postgresql

# Build 'django' image.
docker build -t jcalazan/django --no-cache ../../docker-django-local/django