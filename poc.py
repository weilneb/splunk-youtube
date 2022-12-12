import os
from typing import Dict, List
from collections import deque
from googleapiclient.discovery import build
import time
from pprint import pprint


class YTScraper:
    def __init__(self, api_key: str):
        self.youtube = build("youtube", "v3", developerKey=api_key)
        # map playlist_id -> page token
        self.playlist_id_to_page_token = dict()
        self.queue = deque()

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
            maxResults=1,
            playlistId=playlist_id,
            pageToken=page_token
        )
        response = request.execute()
        next_token = response['nextPageToken']
        videos = [x['snippet'] for x in response['items']]
        return next_token, videos

    def scrape(self, playlist_id: str):
        page_token = self.playlist_id_to_page_token.get(playlist_id, None)
        print(f"Scraping for {playlist_id} with page_token={page_token}")
        next_token, videos = self.get_videos(playlist_id=playlist_id, page_token=page_token)
        print(f"playlist_id={playlist_id}, Next token={next_token}")
        pprint(videos)

        # TODO: send videos to Splunk via HEC

        self.playlist_id_to_page_token[playlist_id] = next_token

    def scrape_loop(self):
        # TODO: handle 429 / rate limiting
        while self.queue:
            playlist_id = self.queue.pop()
            self.scrape(playlist_id)
            self.queue.appendleft(playlist_id)
            # time.sleep(3)


if __name__ == '__main__':
    api_key = os.environ['YOUTUBE_API_KEY']
    scraper = YTScraper(api_key)
    # Jimmy Kim
    scraper.add_channel_id(channel_id="UCOU2PEQuXiz4JsfEtW3frhA")
    scraper.scrape_loop()
    # pid = scraper.get_channel_playlist_id()
    # scraper.get_videos(playlist_id=pid)
"""
- Get channel's 'uploads' playlist ID which is in item['contentDetails']['relatedPlaylists']['uploads']
Then use https://developers.google.com/youtube/v3/docs/playlistItems/list to list videos in the playlist.
- Store pagination token (nextPageToken) and use it in next call.
- Store all video metadata in local sqlite db.
- 

Inputs:
- channel names
- timestamp to start video search at
- Youtube API KEY
Processing:
- Find all videos created at/after timestamp by given channels
- Handle rate limiting / quota
- Scheduler - every 30 minutes?
Output:
- Push to Splunk HEC
Links:
- Rate limits/quotas: https://developers.google.com/youtube/v3/determine_quota_cost
- Splunk HEC (HTTP): https://docs.splunk.com/Documentation/Splunk/latest/Data/HECExamples
"""
