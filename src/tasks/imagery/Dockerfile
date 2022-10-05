FROM python:3.10

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY /tcc-lucas-pierre-7490c66905ca.json $APP_HOME/tcc-lucas-pierre-7490c66905ca.json
ENV GOOGLE_APPLICATION_CREDENTIALS=$APP_HOME/tcc-lucas-pierre-7490c66905ca.json
COPY . .

# Install production dependencies.
RUN pip install Flask gunicorn
RUN pip install -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
