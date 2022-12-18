# splunk-youtube
Get desktop notifications of new YouTube videos.
## Components
- YouTube Scraper
- Splunk
- Desktop Notifier (receive notifications of new videos)

## Running the YouTube Scraper
### Requirements
- Docker
- YouTube API KEY
- [Optional] Local Splunk installation with HEC enabled

### How to run the YouTube scraper
#### Environment Setup
Create a `.env` file with (`SPLUNK_PASSWORD` only needed if you are running Splunk docker container too):
```
YOUTUBE_API_KEY=
SPLUNK_PASSWORD=
SPLUNK_HEC_TOKEN=
SPLUNK_HEC_BASE_URL=
```
Note that if you are running Splunk locally, then set `SPLUNK_HEC_BASE_URL=http://host.docker.internal:8088`
#### Run docker container
```
docker compose up --build yt-scraper
```
Alternatively, if you want to run Splunk as docker container too:
```
docker compose up
```
#### Resulting Actions
The `yt-scraper` should use the grab video metadata for the channels listed in `/yt-channels.yaml`
and send the data across to Splunk.
#### Notes
Uses bind mount with host folder `./db/` to store sqlite database, which maintains state of pagination with the API.

## Running the Desktop Notifier
### What is this
Quart-based server which acts as a Splunk alert webhook.
Quart is similar to flask but is async native.

Uses pync to create desktop notifications.

### Requirements
- Python3 installed locally

### How to run
Install the requirements (in a new virtual environment):
```
pip3 install -r requirements.txt
```
Run it
```
python3 -m notifier
```


