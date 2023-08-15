FROM python:3.8.5
RUN  apt update
RUN  apt install nano
RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt .
COPY ./ReadyToGo-bot .
RUN pip3 install -r requirements.txt --no-cache-dir
CMD python bot.py