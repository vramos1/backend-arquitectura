FROM python:3.8-alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev build-base libevent-dev musl-dev libffi-dev
RUN mkdir /code
COPY entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "entrypoint.sh" ]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]