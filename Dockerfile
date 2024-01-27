FROM python:3.11-alpine

WORKDIR /app

EXPOSE 3000

COPY ./goit_m2_web_homework_4 .

VOLUME /app/storage/

ENTRYPOINT ["python", "main.py", "--host", "0.0.0.0"]