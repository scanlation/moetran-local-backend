FROM python:3.9.2

LABEL project="moetran-backend"

COPY . /app
WORKDIR /app
EXPOSE 5000

VOLUME ["/app/storage"]


RUN pip install -r requirements.txt