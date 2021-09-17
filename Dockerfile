FROM python:3.9
LABEL MAINTAINER="Amin Bs | github.com/amin-bs"

ENV PYTHONUNBUFFERED 1

RUN mkdir /codal
COPY . /codal
WORKDIR /codal

RUN pip install --upgrade pip
RUN pip install -r requirements.txt