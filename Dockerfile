# start with python
FROM python:3.8-slim-buster

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# copy all file from current folder to container's folder
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# set working directory container's default folder
WORKDIR .

# install dependencies specified in requirements file
RUN pip install --no-cache-dir -r requirements.txt


CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app