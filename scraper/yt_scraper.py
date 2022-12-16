import datetime
import time
from typing import Dict, List
from dateutil.parser import isoparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .db import YoutubeChannel
from .splunk_hec import send_to_splunk_hec

ERROR_RETRY_TIMEOUT_SECONDS = 300
SECONDS_BETWEEN_API_CALLS = 5


class YTScraper:
    def __init__(self, api_key: str, db_session, api_page_size=50):
        self.youtube = build("youtube", "v3", developerKey=api_key)
        self.db_session = db_session
        self.api_page_size = api_page_size

    def add_channel_ids(self, channel_ids: List[str]):
        for c_id in channel_ids:
            self.add_channel_id(channel_id=c_id)

    def add_channel_id(self, channel_id: str):
        if self.db_session.query(YoutubeChannel).filter_by(channel_id=channel_id).first() is None:
            playlist_id = self.get_channel_playlist_id(channel_id)
            self.db_session.add(YoutubeChannel(channel_id=channel_id, playlist_id=playlist_id))

    def get_next_to_scrape(self):
        return self.db_session.query(YoutubeChannel).order_by(YoutubeChannel.next_scheduled_at).first()

    def get_channel_playlist_id(self, channel_id: str) -> str:
        request = self.youtube.channels().list(
            part="id,snippet,contentDetails,statistics",
            id=channel_id
        )
        response = request.execute()
        items = response["items"]
        assert len(items) == 1
        uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return uploads_playlist_id

    def get_videos(self, playlist_id: str, page_token: str = None) -> (str, List[Dict]):
        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=self.api_page_size,
            playlistId=playlist_id,
            pageToken=page_token
        )
        response = request.execute()
        next_token = response.get('nextPageToken', None)
        videos = [item['snippet'] for item in response['items']]
        return next_token, videos

    def scrape(self, channel: YoutubeChannel):

        page_token = channel.next_token
        playlist_id = channel.playlist_id
        print(f"Scraping for {playlist_id} with page_token={page_token}")
        next_token, videos = self.get_videos(playlist_id=playlist_id, page_token=page_token)
        print(f"playlist_id={playlist_id}, Next token={next_token}")
        for vid in videos:
            print(f"{vid['channelTitle']}: {vid['title']}")

            # TODO: send videos to Splunk via HEC
            #  we want timestamp = when video was published
            timestamp = isoparse(vid['publishedAt']).timestamp()
            send_to_splunk_hec(data=vid, timestamp=timestamp)

        # TODO: only update if next_token is not None
        #  need to add check for last video received by publishedAt to prevent dupes
        #  also.. if next_token is None, then should wait a long time for next video...
        channel.next_token = next_token
        channel.next_scheduled_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        self.db_session.commit()

    def scrape_loop(self):
        while True:
            channel = self.get_next_to_scrape()
            if channel is None:
                raise RuntimeError("No channels registered to scrape.")
            try:
                self.scrape(channel=channel)
                print(f"Sleeping for {SECONDS_BETWEEN_API_CALLS}")
                time.sleep(SECONDS_BETWEEN_API_CALLS)

            # https://github.com/googleapis/google-api-python-client/blob/main/googleapiclient/http.py#L938
            # This should handle any non-200 HTTP status codes
            except HttpError as err:
                print(f"Error: {err}")
                time.sleep(ERROR_RETRY_TIMEOUT_SECONDS)
