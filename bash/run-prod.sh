#!/bin/bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn dashboard.wsgi -b 0.0.0.0:8000 --log-file -
