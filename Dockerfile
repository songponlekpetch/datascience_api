FROM tiangolo/uwsgi-nginx:python3.6

RUN apt-get update && apt-get install -y \
      cron\
      nano

RUN pip install flask

ENV STATIC_URL /static

ENV STATIC_PATH /app/static

ENV STATIC_INDEX 0

COPY ./app /app
WORKDIR /app

RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

ENV FLASK_APP main.py

ENV FLASK_DEBUG 1

COPY start.sh /start.sh
RUN chmod +x /start.sh

RUN mv /entrypoint.sh /uwsgi-nginx-entrypoint.sh

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/start.sh"]
