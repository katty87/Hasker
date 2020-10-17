ENV PYTHONUNBUFFERED 1
RUN git clone https://github.com/katty87/Hasker.git /code/hasker/
WORKDIR /code/hasker
SECRET_KEY="$(openssl rand -base64 50)"
COPY requirements.txt /code/
RUN pip install -r requirements.txt