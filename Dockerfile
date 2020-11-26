FROM python:3

ENV PYTHONUNBUFFERRED 1
WORKDIR /app/django_project
ADD . /app
COPY . /app/
RUN pip install -r requirements.txt
