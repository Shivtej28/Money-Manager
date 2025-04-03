#!/bin/bash
python manage.py collectstatic --noinput
gunicorn moneymanager.wsgi:application --bind 0.0.0.0:$PORT