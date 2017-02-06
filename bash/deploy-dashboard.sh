#!/bin/bash

docker pull bdeinsalyon/dashboard
docker kill dashboard
docker rm dashboard
docker run --name dashboard --env-file /var/conf/environements/dashboard.env --volume /var/www/dashboard:/app/staticfiles -d bdeinsalyon/dashboard
