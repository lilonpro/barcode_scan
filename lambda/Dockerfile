FROM python:3.7
RUN apt-get update
RUN apt-get install poppler-utils build-essential libzbar-dev python3-opencv -y
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
CMD [ "python", "./app.py" ]