#!/bin/sh
python3 manage.py migrate && python3 manage.py collectstatic --noinput && gunicorn dashboard.wsgi -b 0.0.0.0:8000 --log-file -
