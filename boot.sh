#!/bin/sh 

source vevn/bin/activate 
flask db upgrade 
# flask translate compile 
exec gunicorn -b :5000 --access-logfile - --error-logfile - bookoutlet_service:app