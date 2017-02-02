FROM python:3.5

# RUN apt-get update && apt-get install -y gettext

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

VOLUME /app/staticfiles

ENV DATABASE_URL postgres://postgresql:postgresql@db:5432/dashboard

EXPOSE 8000

CMD /app/bash/run-prod.sh

# RUN python manage.py compilemessages -l en -l fr
