import time
from collections import deque
from typing import Dict, List

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ERROR_RETRY_TIMEOUT_SECONDS = 300
SECONDS_BETWEEN_API_CALLS = 5


class YTScraper:
    def __init__(self, api_key: str):
        self.youtube = build("youtube", "v3", developerKey=api_key)
        # map playlist_id -> page token
        self.playlist_id_to_page_token = dict()
        self.queue = deque()

    def add_channel_ids(self, channel_ids: List[str]):
        for c_id in channel_ids:
            self.add_channel_id(channel_id=c_id)

    def add_channel_id(self, channel_id: str):
        playlist_id = self.get_channel_playlist_id(channel_id)
        if playlist_id not in self.playlist_id_to_page_token:
            self.playlist_id_to_page_token[playlist_id] = None
            self.queue.appendleft(playlist_id)

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
            maxResults=3,
            playlistId=playlist_id,
            pageToken=page_token
        )
        response = request.execute()
        next_token = response['nextPageToken']
        videos = [item['snippet'] for item in response['items']]
        return next_token, videos

    def scrape(self, playlist_id: str):
        page_token = self.playlist_id_to_page_token.get(playlist_id, None)
        print(f"Scraping for {playlist_id} with page_token={page_token}")
        next_token, videos = self.get_videos(playlist_id=playlist_id, page_token=page_token)
        print(f"playlist_id={playlist_id}, Next token={next_token}")
        for vid in videos:
            print(vid['channelTitle'], vid['title'])

        # TODO: send videos to Splunk via HEC
        #  we want timestamp = when video was published

        self.playlist_id_to_page_token[playlist_id] = next_token

    def scrape_loop(self):
        while self.queue:
            playlist_id = self.queue.pop()
            try:
                self.scrape(playlist_id)
                self.queue.appendleft(playlist_id)
                time.sleep(SECONDS_BETWEEN_API_CALLS)

            # https://github.com/googleapis/google-api-python-client/blob/main/googleapiclient/http.py#L938
            # This should handle any non-200 HTTP status codes
            except HttpError as err:
                print(f"Error: {err}")
                # retry
                self.queue.append(playlist_id)
                time.sleep(ERROR_RETRY_TIMEOUT_SECONDS)
