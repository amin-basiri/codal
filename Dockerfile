FROM python:3.9
LABEL MAINTAINER="Amin Bs | github.com/amin-bs"

# Add tini
ENV TINI_VERSION=v0.19.0
RUN curl -L https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini -o /tini && \
    chmod +x /tini


RUN apt-get update --assume-yes       && \
    apt-get upgrade --assume-yes      && \
    apt-get install -y --assume-yes      \
    gconf-service                        \
    libxext6                             \
    libxfixes3                           \
    libxi6                               \
    libxrandr2                           \
    libxrender1                          \
    libcairo2                            \
    libcups2                             \
    libdbus-1-3                          \
    libexpat1                            \
    libfontconfig1                       \
    libgcc1                              \
    libgconf-2-4                         \
    libgdk-pixbuf2.0-0                   \
    libglib2.0-0                         \
    libgtk-3-0                           \
    libnspr4                             \
    libpango-1.0-0                       \
    libpangocairo-1.0-0                  \
    libstdc++6                           \
    libx11-6                             \
    libx11-xcb1                          \
    libxcb1                              \
    libxcomposite1                       \
    libxcursor1                          \
    libxdamage1                          \
    libxss1                              \
    libxtst6                             \
    libnss3                              \
    libasound2                           \
    libatk1.0-0                          \
    libc6                                \
    ca-certificates                      \
    fonts-liberation                     \
    lsb-release                          \
    xdg-utils                            \
    wget                                 \
    libldap2-dev                         \
    lib32z1


ENV PYTHONUNBUFFERED 1

RUN mkdir /codal
COPY . /codal
WORKDIR /codal


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Web Driver
RUN mkdir -p /root/.local/share/pyppeteer/local-chromium/588429/ && \
    wget https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/588429/chrome-linux.zip -O temp.zip && \
    unzip temp.zip -d /root/.local/share/pyppeteer/local-chromium/588429/ && \
    rm temp.zip

# Headless Web Driver
RUN wget https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-41/stable-headless-chromium-amazonlinux-2017-03.zip -O temp.zip && \
    unzip temp.zip -d /root/ && \
    rm temp.zip