# pull official base image
FROM python:3.10.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*


RUN useradd -r -s /bin/bash alex

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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
ARG APP_HOST

# SENTRY DSN
ARG SENTRY_DSN

# GUS
ARG GUS_API_DEV 

# API_VIDEO
ARG API_VIDEO 
ARG API_VIDEO_UPLOAD 

# AWS RDS vars
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT
ARG DB_DATABASE

# EMAIL LABS
ARG EMAIL_LABS_APP_KEY
ARG EMAIL_LABS_SECRET_KEY
ARG EMAIL_LABS_SMTP
ARG EMAIL_LABS_SENDER
ARG EMAIL_DEV

# MAILJET
ARG MAILJET_EMAIL_API_KEY
ARG MAILJET_EMAIL_SECRET
ARG MAILJET_EMAIL_SENDER
ARG MAILJET_SMS_API_KEY
ARG MAILJET_SMS_SENDER

ENV APP_ENV $APP_ENV
ENV APP_HOST $APP_HOST

ENV AWS_ACCESS_KEY_ID $AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY $AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION $AWS_DEFAULT_REGION

ENV AWS_S3_BUCKET $AWS_S3_BUCKET
ENV AWS_S3_DEFAULT_REGION $AWS_S3_DEFAULT_REGION
ENV AWS_S3_ACCESS_KEY_ID $AWS_S3_ACCESS_KEY_ID
ENV AWS_S3_SECRET_ACCESS_KEY $AWS_S3_SECRET_ACCESS_KEY

ENV SENTRY_DSN $SENTRY_DSN
ENV GUS_API_DEV $GUS_API_DEV
ENV API_VIDEO $API_VIDEO
ENV API_VIDEO_UPLOAD $API_VIDEO_UPLOAD 

ENV EMAIL_LABS_APP_KEY $EMAIL_LABS_APP_KEY
ENV EMAIL_LABS_SECRET_KEY $EMAIL_LABS_SECRET_KEY
ENV EMAIL_LABS_SMTP $EMAIL_LABS_SMTP
ENV EMAIL_LABS_SENDER $EMAIL_LABS_SENDER
ENV EMAIL_DEV $EMAIL_DEV

ENV MAILJET_EMAIL_API_KEY $MAILJET_EMAIL_API_KEY
ENV MAILJET_EMAIL_SECRET $MAILJET_EMAIL_SECRET
ENV MAILJET_EMAIL_SENDER $MAILJET_EMAIL_SENDER
ENV MAILJET_SMS_API_KEY $MAILJET_SMS_API_KEY
ENV MAILJET_SMS_SENDER $MAILJET_SMS_SENDER

ENV DB_USERNAME $DB_USERNAME
ENV DB_PASSWORD $DB_PASSWORD
ENV DB_HOST $DB_HOST
ENV DB_PORT $DB_PORT
ENV DB_DATABASE $DB_DATABASE

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt
# EXPOSE 80

#USER alex
COPY --chown=alex:alex ./commands /src/commands
COPY --chown=alex:alex ./migrations /src/migrations
COPY --chown=alex:alex ./alembic.ini /src/alembic.ini
COPY --chown=alex:alex ./app /src/app
COPY --chown=alex:alex ./tests/api_responses /src/tests/api_responses


WORKDIR /src

# EXPOSE 80

# ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000" "--reload", "--debug"]
# CMD uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload --debug --reload-dir /src/app
# CMD uvicorn app.main:app --host 0.0.0.0 --port 5000 
CMD ["uvicorn", "app.main:app","--no-server-header","--no-proxy-headers", "--host", "0.0.0.0", "--port", "5000" ]

# ENTRYPOINT ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", ":5000", "app.main:app"]


HEALTHCHECK --interval=21s --timeout=3s --start-period=10s CMD curl --fail http://localhost:5000/health || exit 1

# EXPOSE 5432