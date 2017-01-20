#!/bin/bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn dashboard.wsgi --log-file -
