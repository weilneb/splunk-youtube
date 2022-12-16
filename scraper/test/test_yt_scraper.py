import datetime

import pytest

from scraper import YoutubeChannel, YTScraper
from unittest.mock import patch


@pytest.mark.usefixtures("test_db")
class TestScraper:
    def test_register_youtube_channel(self, test_db):
        scraper = YTScraper(api_key="abc", db_session=test_db)

        channels = test_db.query(YoutubeChannel).all()
        assert len(channels) == 0

        with patch.object(YTScraper, 'get_channel_playlist_id', return_value="pid1"):
            scraper.add_channel_id(channel_id="abc123")

        channels = test_db.query(YoutubeChannel).all()
        assert len(channels) == 1
        channel = test_db.query(YoutubeChannel).filter_by(channel_id="abc123").first()
        assert channel.channel_id == "abc123"
        assert channel.playlist_id == "pid1"

    def test_get_next_to_scrape(self, test_db):
        scraper = YTScraper(api_key="abc", db_session=test_db)
        now = datetime.datetime.utcnow()
        two_hours_ago = now - datetime.timedelta(hours=2)
        channel_a = YoutubeChannel(channel_id="123", playlist_id="pid1", next_scheduled_at=now)
        channel_b = YoutubeChannel(channel_id="456", playlist_id="pid2", next_scheduled_at=two_hours_ago)

        test_db.add(channel_a)
        test_db.add(channel_b)

        channels = test_db.query(YoutubeChannel).all()
        assert len(channels) == 2
        assert scraper.get_next_to_scrape() == channel_b
