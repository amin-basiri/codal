FROM python:3.9
LABEL MAINTAINER="Amin Bs | github.com/amin-bs"

# Add tini
ENV TINI_VERSION=v0.19.0
RUN curl -L https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini -o /tini && \
    chmod +x /tini

# Add gosu
ENV GOSU_VERSION=1.12
RUN curl -L https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64 -o /usr/local/bin/gosu && \
    chmod +x /usr/local/bin/gosu

RUN apt-get update --assume-yes      && \
    apt-get upgrade --assume-yes      && \
    apt-get install -y --assume-yes     \
    gconf-service           \
    libxext6                \
    libxfixes3              \
    libxi6                  \
    libxrandr2              \
    libxrender1             \
    libcairo2               \
    libcups2                \
    libdbus-1-3             \
    libexpat1               \
    libfontconfig1          \
    libgcc1                 \
    libgconf-2-4            \
    libgdk-pixbuf2.0-0      \
    libglib2.0-0            \
    libgtk-3-0              \
    libnspr4                \
    libpango-1.0-0          \
    libpangocairo-1.0-0     \
    libstdc++6              \
    libx11-6                \
    libx11-xcb1             \
    libxcb1                 \
    libxcomposite1          \
    libxcursor1             \
    libxdamage1             \
    libxss1                 \
    libxtst6                \
#    libappindicator1        \
    libnss3                 \
    libasound2              \
    libatk1.0-0             \
    libc6                   \
    ca-certificates         \
    fonts-liberation        \
    lsb-release             \
    xdg-utils               \
    wget                    \
    libldap2-dev            \
    lib32z1
#    lib32ncurses5           \
#    lib32bz2-1.0            \
#    lib32stdc++6            \
#    ibX11-xcb.so.1          \


ENV PYTHONUNBUFFERED 1

RUN mkdir /codal
COPY . /codal
WORKDIR /codal


RUN pip install --upgrade pip
RUN pip install -r requirements.txt


RUN mkdir -p /root/.local/share/pyppeteer/local-chromium/588429/ && \
    wget https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/588429/chrome-linux.zip -O temp.zip && \
    unzip temp.zip -d /root/.local/share/pyppeteer/local-chromium/588429/
    rm temp.zip

RUN wget https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-41/stable-headless-chromium-amazonlinux-2017-03.zip -O temp.zip && \
    unzip temp.zip -d /codal/modules && \
    rm temp.zip