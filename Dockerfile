FROM python:latest
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD scraper ./scraper
ADD yt-channels.yaml .

CMD [ "python3", "-m" , "scraper", "yt-channels.yaml", "/app/db/db.sqlite"]
#CMD ["/bin/bash"]