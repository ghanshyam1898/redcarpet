FROM python:3

ENV PYTHONUNBUFFERRED 1
WORKDIR /app
ADD . /app
COPY . /app/
RUN pip install -r requirements.txt
