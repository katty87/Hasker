FROM python:3
ENV PYTHONUNBUFFERED 1
COPY . /code/hasker/
WORKDIR /code/hasker
COPY requirements.txt /code/
RUN pip install -r requirements.txt