# Reference: https://codelabs.developers.google.com/codelabs/cloud-run-hello-python3#4
# Reference: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04

FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements_prod.txt

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 wsgi:app