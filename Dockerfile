FROM python:3.11-alpine

WORKDIR /homework_4

COPY . .

VOLUME /homework_4/goit_m2_web_homework_4/storage/

RUN pip install -r requirements.txt

EXPOSE 3000

ENTRYPOINT ["python", "goit_m2_web_homework_4/main.py"]