# pull official base image
FROM python:3.10.14-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  postgresql-client \
  && rm -rf /var/lib/apt/lists/*

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Enable python stacktraces on segfaults
ENV PYTHONFAULTHANDLER=1

WORKDIR /src

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser


# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# TODO: UV - https://github.com/djangopackages/djangopackages/blob/main/dockerfiles/django/Dockerfile-dev

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

# Switch to the non-privileged user to run the application.
USER appuser

#USER alex
COPY --chown=appuser:appuser ./commands /src/commands
COPY --chown=appuser:appuser ./migrations /src/migrations
COPY --chown=appuser:appuser ./alembic.ini /src/alembic.ini
COPY --chown=appuser:appuser ./app /src/app
COPY --chown=appuser:appuser ./tests/api_responses /src/tests/api_responses

# Expose the port that the application listens on.
EXPOSE 5000

CMD ["uvicorn", "app.main:app","--no-server-header","--no-proxy-headers", "--host", "0.0.0.0", "--port", "5000" ]

HEALTHCHECK --interval=21s --timeout=3s --start-period=10s CMD curl --fail http://localhost:5000/health || exit 1
