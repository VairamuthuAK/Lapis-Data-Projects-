FROM python:3.11.4-slim-bullseye

WORKDIR /app
COPY . /app

ENV PLAYWRIGHT_BROWSERS_PATH=/playwright-browsers

RUN apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium \
    && chmod -Rf 777 $PLAYWRIGHT_BROWSERS_PATH

ENV SCRAPY_SETTINGS_MODULE gun_scraping.settings
RUN python setup.py install