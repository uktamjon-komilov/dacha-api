FROM python:3.9.6-alpine

WORKDIR /home/user/web

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade setuptools pip
COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /home/user/web/entrypoint.sh
RUN chmod +x /home/user/web/entrypoint.sh

COPY . .

ENTRYPOINT ["/home/user/web/entrypoint.sh"]