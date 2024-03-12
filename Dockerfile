FROM python:3.10-bookworm

COPY Pipfile.lock Pipfile /app/

WORKDIR /app/

# Install pip, webserver and dependencies from pipfile
RUN pip3 install --upgrade pip
RUN pip3 install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

#Copy the actual Project source
COPY ./src /app/
COPY gerichte_nrw.txt /app/


STOPSIGNAL SIGTERM
CMD ["python3", "scheduled_scrape.py"]