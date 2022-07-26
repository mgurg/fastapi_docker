# pull official base image
FROM python:3.10.5-slim-bullseye
# FROM pypy:3.9-slim-buster https://tonybaloney.github.io/posts/pypy-in-production.html

# RUN apt-get update && apt-get install -y libmagic1

RUN useradd -r -s /bin/bash alex

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set app config option
ENV FLASK_ENV=production

# set argument vars in docker-run command
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION

ARG AWS_S3_BUCKET
ARG AWS_S3_DEFAULT_REGION
ARG AWS_S3_ACCESS_KEY_ID
ARG AWS_S3_SECRET_ACCESS_KEY

#APP
ARG APP_ENV

# SENTRY DSN
ARG SENTRY_DSN

# AWS RDS vars
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_DATABASE

# EMAIL LABS
ARG EMAIL_LABS_APP_KEY
ARG EMAIL_LABS_SECRET_KEY
ARG EMAIL_LABS_SMTP
ARG EMAIL_LABS_SENDER
ARG EMAIL_DEV

ENV APP_ENV $APP_ENV

ENV AWS_ACCESS_KEY_ID $AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY $AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION $AWS_DEFAULT_REGION

ENV AWS_S3_BUCKET $AWS_S3_BUCKET
ENV AWS_S3_DEFAULT_REGION $AWS_S3_DEFAULT_REGION
ENV AWS_S3_ACCESS_KEY_ID $AWS_S3_ACCESS_KEY_ID
ENV AWS_S3_SECRET_ACCESS_KEY $AWS_S3_SECRET_ACCESS_KEY

ENV SENTRY_DSN $SENTRY_DSN

ENV EMAIL_LABS_APP_KEY $EMAIL_LABS_APP_KEY
ENV EMAIL_LABS_SECRET_KEY $EMAIL_LABS_SECRET_KEY
ENV EMAIL_LABS_SMTP $EMAIL_LABS_SMTP
ENV EMAIL_LABS_SENDER $EMAIL_LABS_SENDER
ENV EMAIL_DEV $EMAIL_DEV

ENV DB_USERNAME $DB_USERNAME
ENV DB_PASSWORD $DB_PASSWORD
ENV DB_HOST $DB_HOST
ENV DB_DATABASE $DB_DATABASE

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt
# EXPOSE 80

#USER alex
COPY --chown=alex:alex ./migrations /src/migrations
COPY --chown=alex:alex ./alembic.ini /src/alembic.ini
COPY --chown=alex:alex ./app /src/app
COPY --chown=alex:alex ./tests/api_responses /src/tests/api_responses


WORKDIR /src



# EXPOSE 80

# ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000" "--reload", "--debug"]
CMD uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload --debug --reload-dir /src/app
# ENTRYPOINT ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", ":5000", "app.main:app"]


# EXPOSE 5432