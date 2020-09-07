FROM python:3
ENV PYTHONUNBUFFERED 1
RUN git clone https://github.com/katty87/Hasker.git /code/hasker/
WORKDIR /code/hasker
COPY requirements.txt /code/
RUN pip install -r requirements.txt