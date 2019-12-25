FROM python:3.7-alpine

RUN adduser -D bookoutlet

WORKDIR /home/bookoutlet

COPY requirements.txt .
RUN python -m venv venv
RUN pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY bookoutlet_service bookoutlet_service 
COPY migrations migrations 
COPY run.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP run.py

RUN chown -R bookoutlet:bookoutlet ./
USER bookoutlet 

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]