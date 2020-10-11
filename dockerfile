FROM python:3
ENV PYTHONUNBUFFERED 1
RUN git clone https://github.com/katty87/Hasker.git /code/hasker/
WORKDIR /code/hasker
ENV SECRET_KEY 'vq*ag#8x3#cx!sdj!w3ij_=)3^n(f-uk0sx95-s3__0=683=r#'
COPY requirements.txt /code/
RUN pip install -r requirements.txt