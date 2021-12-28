# pull official base image
FROM python:3.8-slim-bullseye

RUN useradd -r -s /bin/bash alex

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

USER alex
COPY --chown=alex:alex ./app /app

WORKDIR /app

# EXPOSE 80

CMD [ "python", "./main.py" ]
# ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000" "--reload", "--debug"]
# ENTRYPOINT ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", ":5000", "main:app"]


# EXPOSE 5678